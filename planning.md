# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Student reviews of CS professors at Virginia Tech. Official course catalogs and department websites describe what a class covers, but they do not tell you which professor gives useful exam feedback, whether TAs grade slowly, or if a section is an "easy A" versus a grind. This knowledge lives in scattered student reviews on Rate My Professors and Coursicle — hard to search across professors and courses at once.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | John Lewis — CS1064 intro Python (75 ratings, highly recommended) | `documents/john_lewis_rmp.txt` · https://www.ratemyprofessors.com/professor/2453636 |
| 2 | Rate My Professors | Mohammed Farghally — CS2114/CS3114 (projects, test retakes) | `documents/mohammed_farghally_rmp.txt` · https://www.ratemyprofessors.com/professor/2657788 |
| 3 | Rate My Professors | Margaret Ellis — CS2104/CS2114 (polarized reviews, TA grading) | `documents/margaret_ellis_rmp.txt` · https://www.ratemyprofessors.com/professor/2049285 |
| 4 | Rate My Professors | Chris Thomas — graduate ML/computer vision (hard but rewarding) | `documents/chris_thomas_rmp.txt` · https://www.ratemyprofessors.com/professor/2891584 |
| 5 | Rate My Professors | Amun Kharel — CS3724 Intro to HCI (engaging, flexible) | `documents/amun_kharel_rmp.txt` · https://www.ratemyprofessors.com/professor/3052333 |
| 6 | Rate My Professors | Anuj Karpatne — CS5525 grad ML (caring but heavy workload) | `documents/anuj_karpatne_rmp.txt` · https://www.ratemyprofessors.com/professor/2722388 |
| 7 | Rate My Professors | Richard Charles — CS2304 SQL elective (easy 1-credit) | `documents/richard_charles_rmp.txt` · https://www.ratemyprofessors.com/professor/2832708 |
| 8 | Rate My Professors | Shaddi Hasan — grad courses, strong feedback | `documents/shaddi_hasan_rmp.txt` · https://www.ratemyprofessors.com/professor/2779797 |
| 9 | Rate My Professors | Heath Hillman — intro courses (polarized, sarcastic style) | `documents/heath_hillman_rmp.txt` · https://www.ratemyprofessors.com/professor/2861248 |
| 10 | Coursicle | CS1064 course page — cross-professor comparison (93 reviews) | `documents/cs1064_coursicle.txt` · https://www.coursicle.com/vt/courses/CS/1064/ |
| 11 | Coursicle | CS2114 course page — Ellis vs Farghally vs Hillman (91 reviews) | `documents/cs2114_coursicle.txt` · https://www.coursicle.com/vt/courses/CS/2114/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Who do students recommend for CS1064 (Intro to Python), and why? | John Lewis is widely recommended: accessible, clear assignments, ~1–3 hours outside class, lectures cover everything needed; some note boring lectures but good explanations and TAs handle most grading. |
| 2 | Does Mohammed Farghally offer test retakes in CS2114 or CS3114? | Yes — multiple reviews mention free test retakes; students also advise starting projects early and using the 10% early-submission bonus in CS3114. |
| 3 | What do students say about Margaret Ellis's CS2114 workload and grading? | Mixed: negative reviews cite heavy classwork/homework and slow TA grading that drops grades over weeks; positive reviews say exams are easy, projects are long but manageable if started early, and all CS2114 sections share the same format. |
| 4 | Is Chris Thomas's deep learning / computer vision class an easy A? | No — reviews say CS5814/CS5864 are math-heavy, intense exams and homework, but he curves generously, gives extra credit, and is worth it if you want to learn rather than an easy grade. |
| 5 | What is Amun Kharel's teaching style in CS3724 (Intro to HCI)? | Students describe him as engaging, approachable, flexible with extensions, reasonable grader; coursework includes 4 group reports and 1 personal report with plenty of time to complete. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Polarized reviews for the same professor** — Margaret Ellis and Heath Hillman have both glowing and harsh reviews. Retrieval may return only one side, causing the LLM to overstate a single opinion. Chunking per-review (not per-professor page) should help, but course-level queries ("best CS2114 professor") may still mix conflicting sources.

2. **Short, informal review text** — Reviews use slang ("goated," "my goat") and abbreviations. The embedding model may not reliably match queries like "who gives good feedback" to reviews that say "feedbacks are awesome." Metadata (professor name, course code) must be preserved in each chunk for filtering and attribution.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
