# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

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

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which professor do students recommend for CS1064, and how many hours per week do they say they spend on coursework outside of class? | John Lewis; roughly 1–3 hours outside class | Recommends John Lewis; cites "roughly 1-3 hours outside of class" from `john_lewis_rmp.txt` | Relevant — top chunk is the exact Lewis review containing the hours detail | Accurate |
| 2 | Does Mohammed Farghally offer test retakes in CS2114 or CS3114? | Yes — free test retakes; 10% early bonus in CS3114 | States Farghally offers free test retakes in CS2114; says no information on CS3114 | Relevant — top two chunks are Farghally CS2114 reviews mentioning retakes | Partially accurate (retakes confirmed; CS3114 bonus missed because that chunk ranked below top-5) |
| 3 | What specific grading complaint do students raise about Margaret Ellis's CS2114 section? | TAs grade very slowly — grades drop from A to B-/C+ over weeks | Noted "very slow and inconsistent" grading, but attributed it to CS2104 rather than CS2114; also cited deadline strictness | Partially relevant — retrieved Ellis chunks but top result was the CS2104 review, not CS2114 | Partially accurate (identifies slow grading but assigns it to wrong course) |
| 4 | Is Chris Thomas's CS5814 or CS5864 class an easy A? | No — math-heavy, intense exams, but curves and extra credit available | Returned: "I don't have enough information in the provided reviews to answer that question." | Partially relevant — Thomas CS5864 chunks appeared at ranks 4–5 but the "easy A" review ranked ~25th | Inaccurate (correct answer exists in corpus but was not retrieved; system correctly refused to guess) |
| 5 | How many reports are assigned in Amun Kharel's CS3724, and is attendance mandatory? | 4 group + 1 personal report; attendance mandatory in some sections | Correctly cited 4 group + 1 personal report; said no info on attendance | Relevant — top Kharel chunks contain report count details | Partially accurate (report count correct; attendance info exists in documents but model couldn't find it) |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "Is Chris Thomas's CS5814 or CS5864 class an easy A?"

**What the system returned:** "I don't have enough information in the provided reviews to answer that question." — even though two reviews explicitly state the class is not an easy A (one says "if you want easy A take someone else," another says "No easy A by any means").

**Root cause (tied to a specific pipeline stage):** The failure is at the **retrieval stage**. The query "easy A" activated semantic neighbors about easy courses in general — the top 3 results were a Hillman introductory course, a Kharel HCI review describing an "easy class," and a John Lewis CS1064 review mentioning the class "is not super difficult." The Thomas "easy A" chunk ranked 25th out of 47. MiniLM embedded "easy A" more strongly against reviews using those exact words in a positive context (easy class = good) than against the Thomas reviews where "easy A" appears as a negative warning ("if you want easy A take someone else"). The phrase's sentiment flipped the embedding direction just enough to push those chunks below the top-5 retrieval window.

**What you would change to fix it:** Two options: (1) **Increase top-k** from 5 to 8–10 at query time — the Thomas chunks appear at ranks 4–5 when k=5 for one formulation and at rank 25 for another; a larger window would catch them for more query phrasings. (2) **Add BM25 keyword search** (stretch feature) alongside semantic search — "Chris Thomas" is a proper name that BM25 would match exactly, regardless of embedding distance, ensuring his reviews always appear in the retrieval set when his name is in the query.

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
