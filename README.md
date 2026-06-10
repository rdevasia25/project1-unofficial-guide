# The Unofficial Guide — Project 1

A RAG system that answers questions about CS professors at Virginia Tech using student reviews from Rate My Professors and Coursicle. Ask a plain-language question and get a grounded, cited answer drawn from real collected documents.

## How to Run

```bash
python -m venv .venv && source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY

python embed.py        # build vector store (first time, or after document changes)
python app.py          # launch Gradio UI at http://localhost:7860
python evaluate.py     # run all 5 evaluation questions
```

Pipeline modules: `ingest.py` → `chunker.py` → `embed.py` → `retrieve.py` → `generate.py` → `app.py`

---

## Domain

Student reviews of CS professors at Virginia Tech. Official course catalogs describe curriculum and prerequisites, but they do not reflect teaching style, exam difficulty, TA grading speed, or which section is worth the registration fight. That knowledge lives in student reviews on Rate My Professors and Coursicle — scattered, unsearchable, and never cited together.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | John Lewis (RMP) | Professor reviews — CS1064 | `documents/john_lewis_rmp.txt` |
| 2 | Mohammed Farghally (RMP) | Professor reviews — CS2114/CS3114 | `documents/mohammed_farghally_rmp.txt` |
| 3 | Margaret Ellis (RMP) | Professor reviews — CS2104/CS2114 | `documents/margaret_ellis_rmp.txt` |
| 4 | Chris Thomas (RMP) | Professor reviews — grad ML/CV | `documents/chris_thomas_rmp.txt` |
| 5 | Amun Kharel (RMP) | Professor reviews — CS3724 HCI | `documents/amun_kharel_rmp.txt` |
| 6 | Anuj Karpatne (RMP) | Professor reviews — CS5525 | `documents/anuj_karpatne_rmp.txt` |
| 7 | Richard Charles (RMP) | Professor reviews — CS2304 SQL | `documents/richard_charles_rmp.txt` |
| 8 | Shaddi Hasan (RMP) | Professor reviews — grad courses | `documents/shaddi_hasan_rmp.txt` |
| 9 | Heath Hillman (RMP) | Professor reviews — intro courses | `documents/heath_hillman_rmp.txt` |
| 10 | CS1064 (Coursicle) | Course-level reviews (93 total) | `documents/cs1064_coursicle.txt` |
| 11 | CS2114 (Coursicle) | Course-level reviews (91 total) | `documents/cs2114_coursicle.txt` |

See `documents/sources.md` for original URLs and collection notes.

---

## Document Ingestion Pipeline

Documents were collected manually from Rate My Professors and Coursicle (JavaScript-rendered sites that resist automated scraping) and saved as structured `.txt` files in `documents/`. No live web scraping at runtime — the pipeline reads local files only.

**Loading:** `ingest.py` walks `documents/*.txt` and dispatches to one of two parsers based on filename suffix (`*_rmp.txt` or `*_coursicle.txt`).

**Cleaning (during parse):**
- RMP footer boilerplate ("Load More Ratings," copyright lines) was excluded at collection time
- Inline `Tags:` suffixes stripped from review text when written on the same line as `Review:` (e.g., `Review: Good professor. Tags: Amazing lectures...` → `Good professor.`)
- Separate `Tags:` lines removed entirely — they are RMP metadata, not student opinion
- Coursicle metadata-only lines skipped ("Recent professors teaching this course...", "Cons noted for some instructors...")

**Structured output:** Each parsed review becomes a dict with professor, course, source URL, source file, date, quality/difficulty (RMP only), and cleaned review text. Coursicle course descriptions become separate records with `record_type="course_description"`.

**Verification:** `python build_index.py` prints per-file record counts, 5 sample chunks, and validation checks (empty chunks, HTML artifacts, duplicates).

---

## Chunking Strategy

**Chunk size:** One review per chunk (structural chunking, not fixed character count). Typical chunk is 200–600 characters including the metadata prefix. The fallback for reviews longer than 800 characters is a 512-character sliding window with 64-character overlap.

**Overlap:** Zero overlap between review chunks. Each review is a self-contained opinion, so merging the end of one into the start of the next would mix unrelated sentiments. Instead, every chunk carries a repeated metadata prefix (professor, course, source file, URL) so any retrieved chunk is fully attributable without needing context from adjacent chunks.

**Why these choices fit your documents:** RMP and Coursicle reviews are short (1–4 sentences) and semantically atomic — each expresses exactly one student's opinion. A fixed 500-character split would either merge unrelated reviews (e.g., Farghally's retake policy bundled with CS3114 project advice) or cut mid-sentence, producing fragments the embedding model cannot match reliably. Chunking by review boundary keeps each chunk's embedding focused on a single, coherent opinion.

**Final chunk count:** 47 chunks across 11 documents (9 RMP professor files × ~5 reviews each, plus 2 Coursicle files producing 3–5 chunks each including a course description chunk).

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`. Produces 384-dimensional vectors, runs entirely on CPU with no API key or rate limits, and downloads once to a local cache. Chosen because it is the recommended default for this project's free tool stack and is fast enough (~50 ms per query on CPU) for a demo system.

**Production tradeoff reflection:** For a real deployment I would weigh: (1) **Accuracy on informal text** — MiniLM was trained on general web text and handles slang ("goated," "my goat") imperfectly. Models like `e5-large-v2` or OpenAI `text-embedding-3-large` produce more nuanced representations of opinionated, informal language. (2) **Context length** — MiniLM's 256-token limit is fine for short reviews, but a system ingesting full Reddit threads or long faculty pages would need a model supporting 512–8,000 tokens. (3) **Multilingual support** — VT's international student population might write reviews in other languages; `multilingual-e5-large` would handle these without separate pipelines. (4) **Latency vs. hosting cost** — MiniLM runs locally for free but requires the host machine to have the model cached. A hosted API (Cohere Embed, OpenAI) scales to millions of chunks without local storage but adds network latency and per-token cost.

---

## Grounded Generation

**System prompt grounding instruction:**

The full system prompt passed to `llama-3.3-70b-versatile` at every request:

```
You are an assistant that answers questions about CS professors at Virginia Tech
using ONLY the student review documents provided below.

Rules you must follow:
1. Answer using only information explicitly stated in the provided documents.
   Do NOT use any outside knowledge or general assumptions about professors or courses.
2. For every factual claim, cite the source file it came from using the format
   (Source: <filename>).
3. If the provided documents do not contain enough information to answer the question,
   respond with exactly: "I don't have enough information in the provided reviews to
   answer that question."
4. Do not speculate, extrapolate, or fill gaps with plausible-sounding guesses.
```

The user message prepends a numbered context block containing the top-5 retrieved chunks, each labeled with its source file, professor, and course code. The LLM only ever sees those 5 chunks as its knowledge base for that query.

**How source attribution is surfaced in the response:**

Source attribution is enforced through two independent mechanisms:

1. **LLM-level:** Rule 2 of the system prompt instructs the model to append `(Source: <filename>)` to every factual claim. This produces inline citations visible to the user.
2. **Programmatic:** `generate.py` builds the `sources` list by iterating `chunk["metadata"]["source_file"]` values from the `retrieve()` output — ordered by first appearance, deduplicated. This list is displayed in the "Retrieved from" field of the Gradio UI regardless of whether the LLM included citations in its prose. Source attribution is never left entirely to the LLM.

---

## Evaluation Report

Run date: June 2026. Full pipeline test via `python evaluate.py`.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which professor do students recommend for CS1064, and how many hours per week do they say they spend on coursework outside of class? | John Lewis; roughly 1–3 hours outside class | Recommends John Lewis; cites "roughly 1-3 hours outside of class" with `(Source: john_lewis_rmp.txt)` | Relevant — top chunk (`john_lewis_rmp_28`, dist=0.41) is the exact review containing hours and recommendation | Accurate |
| 2 | Does Mohammed Farghally offer test retakes in CS2114 or CS3114? | Yes — free test retakes; 10% early bonus in CS3114 | States Farghally offers free test retakes in CS2114; says no information on CS3114 | Relevant — top two chunks are Farghally CS2114 reviews mentioning "Free test retakes" (dist=0.43, 0.50) | Partially accurate |
| 3 | What specific grading complaint do students raise about Margaret Ellis's CS2114 section? | TAs grade very slowly — grades drop from A to B-/C+ over weeks | "I don't have enough information in the provided reviews to answer that question." | Partially relevant — retrieved Ellis chunks but the CS2114 slow-TA review (`margaret_ellis_rmp_31`) ranked 8th; top chunk was a CS2104 complaint about slow grading (dist=0.44) | Inaccurate |
| 4 | Is Chris Thomas's CS5814 or CS5864 class an easy A? | No — math-heavy, intense exams; "if you want easy A take someone else" | "I don't have enough information in the provided reviews to answer that question." | Partially relevant — Thomas CS5864 chunks at ranks 4–5 (dist=0.60) say "Class is hard"; the explicit "easy A" review ranked ~25th | Inaccurate |
| 5 | How many reports are assigned in Amun Kharel's CS3724, and is attendance mandatory? | 4 group + 1 personal report; attendance mandatory in some sections | Correctly cites 4 group + 1 personal report; says no info on attendance | Relevant — top Kharel chunk (`amun_kharel_rmp_1`, dist=0.52) contains report count | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

### Retrieved chunks per question (top-5)

**Q1 — CS1064 / John Lewis**
| Rank | Distance | Chunk | Content preview |
|------|----------|-------|-----------------|
| 1 | 0.41 | `john_lewis_rmp_28` | "If you need to take CS1064, then John Lewis is your guy... spend time outside of class (roughly 1-3 hours)" |
| 2 | 0.41 | `amun_kharel_rmp_0` | Unrelated — Kharel HCI praise |
| 3–5 | 0.43–0.44 | Other professors | Off-topic for CS1064 |

**Q2 — Farghally test retakes**
| Rank | Distance | Chunk | Content preview |
|------|----------|-------|-----------------|
| 1 | 0.43 | `mohammed_farghally_rmp_35` | "Free test retakes are incredible" |
| 2 | 0.50 | `cs2114_coursicle_17` | Duplicate Farghally review from Coursicle |
| 3 | 0.55 | `mohammed_farghally_rmp_36` | "This guy was retakes for tests!" |

**Q3 — Ellis CS2114 grading (failure)**
| Rank | Distance | Chunk | Content preview |
|------|----------|-------|-----------------|
| 1 | 0.44 | `margaret_ellis_rmp_30` | CS**2104** — "Very slow and inconsistent assignment grading" (wrong course) |
| 2 | 0.44 | `cs2114_coursicle_16` | CS2114 — unprofessional/dismissive (different complaint) |
| 5 | 0.52 | `margaret_ellis_rmp_33` | CS2114 — positive review (conflicting signal) |
| 8 | 0.59 | `margaret_ellis_rmp_31` | CS2114 — **"TAs are incredibly slow... grade drops to B-/C+"** (correct chunk, missed top-5) |

**Q4 — Chris Thomas easy A (primary failure)**
| Rank | Distance | Chunk | Content preview |
|------|----------|-------|-----------------|
| 1 | 0.54 | `heath_hillman_rmp_24` | Unrelated Hillman CS1114 review |
| 2 | 0.55 | `amun_kharel_rmp_0` | "Intro to HCI is a really easy class" — false semantic match on "easy" |
| 4 | 0.60 | `chris_thomas_rmp_10` | "Class is hard" — relevant but no "easy A" phrasing |
| ~25 | 0.69 | `chris_thomas_rmp_8` | **"if you want easy A take someone else"** — correct chunk, far below top-5 |

**Q5 — Kharel CS3724 reports**
| Rank | Distance | Chunk | Content preview |
|------|----------|-------|-----------------|
| 1 | 0.52 | `amun_kharel_rmp_1` | "4 group and 1 personal report" |
| 2–3 | 0.66–0.67 | Other Kharel reviews | Related but less specific |

---

## Failure Case Analysis

**Question that failed:** "Is Chris Thomas's CS5814 or CS5864 class an easy A?"

**What the system returned:** "I don't have enough information in the provided reviews to answer that question." — even though two reviews explicitly state the class is not an easy A (one says "if you want easy A take someone else," another says "No easy A by any means").

**Root cause (tied to a specific pipeline stage):** The failure is at the **retrieval stage**. The query "easy A" activated semantic neighbors about easy courses in general — the top 3 results were a Hillman introductory course, a Kharel HCI review describing an "easy class," and a John Lewis CS1064 review mentioning the class "is not super difficult." The Thomas "easy A" chunk ranked 25th out of 47. MiniLM embedded "easy A" more strongly against reviews using those exact words in a positive context (easy class = good) than against the Thomas reviews where "easy A" appears as a negative warning ("if you want easy A take someone else"). The phrase's sentiment flipped the embedding direction just enough to push those chunks below the top-5 retrieval window.

**What you would change to fix it:** (1) **Hybrid search** — combine BM25 keyword search with semantic search so "Chris Thomas" and "CS5864" match exactly regardless of embedding distance. (2) **Increase top-k** from 5 to 8–10 so borderline-relevant chunks like Thomas rank 4–5 and the explicit "easy A" chunk have more chance of inclusion. (3) **Metadata filtering** — when a professor name appears in the query, filter retrieval to chunks where `metadata.professor` contains that name before ranking.

### Secondary failure: Q3 (Ellis CS2114 grading)

**Question:** "What specific grading complaint do students raise about Margaret Ellis's CS2114 section?"

**What happened:** The correct CS2114 chunk (`margaret_ellis_rmp_31`: "TAs are incredibly slow... grade drops to B-/C+") ranked 8th. Top-5 included a CS2104 slow-grading complaint (wrong course), a CS2114 personality complaint, and a positive CS2114 review. The LLM refused to answer entirely rather than synthesizing the partial evidence.

**Root cause:** Same retrieval limitation as Q4 — course-specific facts in short reviews compete with semantically similar but wrong-course chunks. Generation compounded the failure by treating the refusal rule too strictly when related (but misattributed) evidence existed at rank 1.

---

## Spec Reflection

**One way the spec helped you during implementation:** The Chunking Strategy section in `planning.md` explicitly answered the question "why one review = one chunk" before any code was written. When implementing `ingest.py`, the decision to split on blank-line-separated review blocks rather than fixed character counts came directly from the spec's observation that "key facts (test retakes, 10% early bonus, TA grading delays) live in a single sentence inside one review." Without that pre-written reasoning, the default temptation would have been to use LangChain's `RecursiveCharacterTextSplitter` with a fixed 500-character window, which would have merged unrelated reviews together.

**One way your implementation diverged from the spec, and why:** The spec called for a `chunk.py` file, but the final implementation used `chunker.py` instead. During implementation Python's standard library contains a deprecated `chunk` module, which caused a Pylint `Deprecated module 'chunk'` error and import ambiguity when `build_index.py` imported it. Renaming to `chunker.py` eliminated the conflict and is a better name anyway since "chunk" as a module name clashes with Python conventions. The spec was not updated at the time but the behavior is identical.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Chunking Strategy section from `planning.md`, the Documents table listing 11 `.txt` files with two different formats (RMP and Coursicle), and one sample file (`mohammed_farghally_rmp.txt`) showing the exact text structure. Asked Claude to implement `ingest.py` with two parsers and `chunker.py` with the one-review-per-chunk strategy.
- *What it produced:* A working `ingest.py` with `_parse_rmp` and `_parse_coursicle`, and a `chunker.py` with `chunk_records()`. The initial version named the module `chunk.py`.
- *What I changed or overrode:* Renamed `chunk.py` → `chunker.py` to avoid the deprecated stdlib `chunk` module name clash. Also added an inline-tag stripping regex (`re.sub(r"\s+Tags:.*$", "")`) after finding that the first John Lewis review had "Tags: Amazing lectures, Gives good feedback, Caring" appended on the same line as the review text — the original generated code only stripped `Tags:` lines on their own lines.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section from `planning.md`, the `chunker.py` chunk dict schema, and the `requirements.txt` listing `chromadb>=0.6.0` and `sentence-transformers==3.4.1`. Asked Claude to implement `embed.py` and `retrieve.py` per the spec's architecture diagram.
- *What it produced:* Working `embed.py` using `chromadb.PersistentClient` with `hnsw:space=cosine`, and `retrieve.py` with lazy-loaded model and collection globals.
- *What I changed or overrode:* The generated relevance-check logic in `retrieve.py`'s `__main__` block initially required the top-1 result for query 3 (Chris Thomas easy A) to match exactly — which it never would because the query phrase activates general "easy class" embeddings first. Rewrote `_check_relevance` for query 3 to search all top-k results for any Thomas CS5814/CS5864 chunk meeting a difficulty-keyword threshold, which is a more accurate test of what the retrieval stage should guarantee.

**Instance 3**

- *What I gave the AI:* The Evaluation Plan from `planning.md`, the Grounded Generation requirements from the project spec, and the `retrieve()` function signature. Asked Claude to implement `generate.py` with a 4-rule grounding system prompt and `app.py` with Gradio.
- *What it produced:* Working `generate.py` with `ask()` calling Groq `llama-3.3-70b-versatile`, and a Gradio UI with example questions including an out-of-domain dining hall query to test refusal behavior.
- *What I changed or overrode:* Added `temperature=0.2` to reduce hallucination. Stripped the duplicate metadata prefix from chunk text before sending to the LLM (chunks already embed `[Source: ... | Professor: ...]` in the text; the context builder adds a cleaner header instead). Expanded the README evaluation section manually after running `evaluate.py` — the initial AI-generated summaries didn't include per-chunk distance scores, which Milestone 6 requires for honest failure analysis.
