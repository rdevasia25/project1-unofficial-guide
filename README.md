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

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
