# Demo Video Script — The Unofficial Guide (3–5 minutes)

Use this script while screen-recording. Suggested tool: QuickTime (Mac), OBS, or Loom.

**Before recording:**
1. Activate venv: `source .venv/bin/activate`
2. Ensure vector store exists: `python embed.py` (only if `./chroma_db` is missing)
3. Start the app: `python app.py`
4. Open http://localhost:7860 in your browser
5. Have `README.md` open in a second tab or split screen for the evaluation walkthrough

---

## Segment 1 — Introduction (~30 seconds)

**On screen:** Browser on the Gradio app homepage

**Say:**
> "This is my Project 1 submission: The Unofficial Guide — a RAG system that answers questions about CS professors at Virginia Tech using student reviews from Rate My Professors and Coursicle. Official course catalogs don't tell you which professor gives useful feedback or whether a section is an easy A. This system makes that scattered student knowledge searchable and cited.
>
> The pipeline is: 11 text documents → 47 review chunks → embedded with MiniLM → stored in ChromaDB → retrieved on query → answered by Groq's Llama 3.3 with a grounding prompt that forbids using outside knowledge."

---

## Segment 2 — Three successful queries with citations (~2 minutes)

### Query A — Strong success (CS1064 / John Lewis)

**Type in the question box:**
```
Who should I take for CS1064 and how much time should I expect outside class?
```

**Click Ask. Pause so the answer and "Retrieved from" box are visible.**

**Say:**
> "Here the system recommends John Lewis and cites roughly 1 to 3 hours outside of class. You can see inline citations like `(Source: john_lewis_rmp.txt)` in the answer, and the Retrieved from field lists the source files programmatically — that's not left to the model alone."

---

### Query B — Retrieval + generation both work (Farghally retakes)

**Type:**
```
Does Mohammed Farghally offer test retakes in CS2114?
```

**Say:**
> "This question tests whether the system can find a specific policy buried in a review. It correctly says Farghally offers free test retakes and cites both the Rate My Professors file and the Coursicle course page. Retrieval pulled the right chunks at the top of the ranked list."

---

### Query C — Partial success (Kharel CS3724)

**Type:**
```
How many reports does Amun Kharel assign in CS3724?
```

**Say:**
> "For Kharel's HCI course, the system correctly answers 4 group reports and 1 personal report with a source citation. It may say it doesn't have attendance info — that's honest grounding when the retrieved chunks don't include that detail in the top results."

---

## Segment 3 — Failure case (~1 minute)

**Type:**
```
Is Chris Thomas's CS5814 or CS5864 class an easy A?
```

**Wait for response. It should say it doesn't have enough information, OR give a weak answer.**

**Say:**
> "This is my main failure case. The correct reviews exist — one literally says 'if you want easy A take someone else' — but retrieval ranked those chunks around 25th out of 47. The query phrase 'easy A' matched reviews about easy classes in general — Kharel's HCI review, Lewis's CS1064 — before it matched Thomas's negative warning.
>
> The generation layer actually behaved correctly: it refused to guess rather than hallucinate. The failure is at retrieval — semantic search overweighted the positive 'easy class' phrasing and underweighted Thomas's name plus course code. I'd fix this with hybrid BM25 search so 'Chris Thomas' matches exactly, or by increasing top-k from 5 to 10."

**Optional:** Switch to terminal and run:
```bash
python retrieve.py "Is Chris Thomas's CS5814 or CS5864 class an easy A?"
```
Show that Chris Thomas chunks appear at ranks 4–5 but the best 'easy A' chunk is much lower.

---

## Segment 4 — Out-of-domain refusal (~20 seconds)

**Type:**
```
What is the best dining hall at Virginia Tech?
```

**Say:**
> "When I ask something outside the corpus, the system should refuse. Here it says it doesn't have enough information in the provided reviews — it doesn't invent dining hall advice from general knowledge."

---

## Segment 5 — Evaluation report walkthrough (~1 minute)

**On screen:** Open `README.md` and scroll to **Evaluation Report** and **Failure Case Analysis**

**Say:**
> "I ran all 5 test questions from my planning doc through the full pipeline using `python evaluate.py`. Question 1 on John Lewis was fully accurate. Question 2 on Farghally retakes was partially accurate — it confirmed retakes but missed the CS3114 early bonus because that chunk ranked below top-5. Question 4 on Chris Thomas was inaccurate at the system level even though generation refused to hallucinate — the right evidence wasn't retrieved.
>
> In Failure Case Analysis I tied this to the retrieval stage specifically: MiniLM's embedding of 'easy A' aligned with positive easy-class reviews rather than Thomas's negative usage. That's the kind of failure you'd miss if you only tested generation."

---

## Segment 6 — Close (~15 seconds)

**Say:**
> "The full README documents chunking — one review per chunk — embedding with MiniLM, grounding rules in the system prompt, and programmatic source attribution. Thanks for watching."

---

## Recording checklist

- [ ] Gradio UI visible for at least 3 queries
- [ ] Source citations visible in answer text (`Source: filename`)
- [ ] "Retrieved from" field visible below answer
- [ ] At least one query where retrieval + generation work well (Lewis or Farghally)
- [ ] One failure case narrated with pipeline stage identified (Thomas easy A)
- [ ] README evaluation report shown briefly
- [ ] Total length between 3 and 5 minutes

## Commands reference

```bash
source .venv/bin/activate
python embed.py          # build vector store (first time only)
python app.py            # launch Gradio UI
python evaluate.py       # run all 5 eval questions in terminal
python retrieve.py       # run 3 retrieval-only tests
python generate.py       # run 5 generation tests
```
