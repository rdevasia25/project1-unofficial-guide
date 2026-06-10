# Document Sources — VT CS Professor Reviews

Domain: student reviews of CS professors at Virginia Tech.

Collected: 2026-06-09

| # | File | Source | Type | URL |
|---|------|--------|------|-----|
| 1 | `john_lewis_rmp.txt` | Rate My Professors | Professor profile (75 ratings) | https://www.ratemyprofessors.com/professor/2453636 |
| 2 | `mohammed_farghally_rmp.txt` | Rate My Professors | Professor profile (13 ratings) | https://www.ratemyprofessors.com/professor/2657788 |
| 3 | `margaret_ellis_rmp.txt` | Rate My Professors | Professor profile (41 ratings) | https://www.ratemyprofessors.com/professor/2049285 |
| 4 | `chris_thomas_rmp.txt` | Rate My Professors | Professor profile (5 ratings) | https://www.ratemyprofessors.com/professor/2891584 |
| 5 | `amun_kharel_rmp.txt` | Rate My Professors | Professor profile (3 ratings) | https://www.ratemyprofessors.com/professor/3052333 |
| 6 | `anuj_karpatne_rmp.txt` | Rate My Professors | Professor profile (4 ratings) | https://www.ratemyprofessors.com/professor/2722388 |
| 7 | `richard_charles_rmp.txt` | Rate My Professors | Professor profile (4 ratings) | https://www.ratemyprofessors.com/professor/2832708 |
| 8 | `shaddi_hasan_rmp.txt` | Rate My Professors | Professor profile (3 ratings) | https://www.ratemyprofessors.com/professor/2779797 |
| 9 | `heath_hillman_rmp.txt` | Rate My Professors | Professor profile (64 ratings) | https://www.ratemyprofessors.com/professor/2861248 |
| 10 | `cs1064_coursicle.txt` | Coursicle | Course review page (93 reviews) | https://www.coursicle.com/vt/courses/CS/1064/ |
| 11 | `cs2114_coursicle.txt` | Coursicle | Course review page (91 reviews) | https://www.coursicle.com/vt/courses/CS/2114/ |

## Sample questions this corpus should answer

1. Who do students recommend for CS1064 (Intro to Python), and what do they say about the workload?
2. Which CS2114 professor is considered the best, and what advice do students give about projects?
3. Does Mohammed Farghally offer test retakes or other grading accommodations?
4. What are the mixed opinions about Margaret Ellis vs. other CS2114 instructors?
5. How difficult are Chris Thomas's graduate ML/computer vision courses?
6. What is Amun Kharel's reputation for CS3724 (Intro to HCI)?
7. Why do some students strongly recommend avoiding Heath Hillman?

## Document structure notes (from skimming)

- **Rate My Professors pages** are short, self-contained review entries with metadata (course, date, quality/difficulty scores, tags). Most reviews are 1–4 sentences; a few are longer. Key facts (retakes, project advice, grading policies) are often buried in a single sentence.
- **Coursicle course pages** aggregate reviews across professors for one course. Reviews mention professor names inline and include student year/major context. Useful for comparing instructors teaching the same course.
- **Coverage spans** intro courses (CS1064, CS2114), upper-level (CS3114), electives (CS3724 HCI, CS2304 SQL), and graduate courses (CS5525, CS5814, CS5864, CS6204).
- **Polarized opinions** appear for Margaret Ellis and Heath Hillman — important for evaluation but risky for retrieval (similar course codes may pull wrong professor).
