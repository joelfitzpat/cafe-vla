# Literature Review — Structure & Style Guide
## GENG5511 Engineering Research Project — UWA
## Joel Fitzpatrick (22736996)

---

## Context: Where the Lit Review Sits

The literature review is **Section 3.2** within the larger report structure:

```
3.  Introduction, Literature Review, and Project Objectives
    3.1  Introduction
    3.2  Literature Review (or Background)    <-- this document covers this
    3.3  Project Objectives
```

The full report word limit is **3,000–4,000 words** (introduction to progress to date,
excluding title page, summary, appendices, reference list, ToC).
Budget approximately **800–1,200 words** for 3.2 in the proposal submission.
The final report will have a more developed version — likely 1,500–2,500 words.
**Confirm exact limits with your supervisor.**

---

## UWA Formatting Requirements (non-negotiable)

| Element | Requirement |
|---|---|
| Font | 12-point Times or Times New Roman |
| Margins | 2 cm on all sides |
| Line spacing | 1.15 or 1.5 |
| Alignment | Left or justified |
| Page numbers | Footer, required |
| Paragraph separation | Single blank line between paragraphs |
| Section headings | 12-point Bold |
| Subsection headings | 12-point Underline |
| Sub-subsection headings | 12-point Italic |
| Citation style | APA 7th Edition |
| Person | 3rd person throughout — no "I", "we", or "you" |

---

## Academic Voice

### Always 3rd Person
UWA explicitly requires this for all technical reports.

| Avoid | Use instead |
|---|---|
| "I am testing whether..." | "This project investigates whether..." |
| "We found that..." | "Results indicate that..." |
| "Our robot uses..." | "The robot used in this project..." |
| "I chose OpenVLA-OFT because..." | "OpenVLA-OFT was selected due to..." |

### Tense
- **Present tense** for established facts and your claims:
  "OpenVLA-OFT uses action chunking to reduce inference frequency."
- **Past tense** for what specific studies did:
  "Kim et al. (2025) demonstrated that parallel decoding reduces latency by..."
- **Future tense** for your planned work (in the proposal):
  "Fine-tuning will be conducted using LoRA on the collected dataset."

### Hedging
Use hedging for claims not yet proven by your own data:
- "suggests", "indicates", "may", "appears to", "is likely to"
- "Evidence from simulation suggests X, though real-world validation is required."

---

## APA 7 Citation Format

### In-text citations
- One author: (Kim, 2025) or Kim (2025) demonstrated that...
- Two authors: (Kim & Finn, 2025)
- Three or more: (Kim et al., 2025)
- Direct quote: (Kim et al., 2025, p. 4) — include page number

### Reference list format (APA 7)

**Journal/preprint:**
> Kim, M. J., Finn, C., & Liang, P. (2025). Fine-tuning vision-language-action
> models: Optimizing speed and success. *arXiv preprint arXiv:2502.19645*.

**Conference paper:**
> Brohan, A., et al. (2023). RT-2: Vision-language-action models transfer web
> knowledge to robotic control. *arXiv preprint arXiv:2307.15818*.

**Website / documentation:**
> University Library. (2026). *Library guides*. University of Western Australia.
> Retrieved March 10, 2026, from https://guides.library.uwa.edu.au

**Note:** Your progress report used numbered references [1] — confirm with your
supervisor whether APA 7 (author-date) or IEEE (numbered) is required for
this submission. The proposal guide uses APA 7 in its own example.

---

## What a Good Lit Review Does (vs. What to Avoid)

The UWA guide distinguishes explicitly between a **review** and a **survey**:

| Survey (avoid) | Review (aim for) |
|---|---|
| Lists papers one by one | Groups papers by theme or finding |
| "Paper A says X. Paper B says Y." | "Multiple studies show X (A; B), though C argues Y under different conditions." |
| No indication of relative importance | Highlights which findings are most relevant to your project |
| Passive description | Critical analysis — what works, what doesn't, what's missing |

Every paragraph should advance an argument. A useful test: if you removed a
paragraph and the section still made sense, the paragraph isn't earning its place.

### Signposting
Open each section with a sentence stating its purpose:
> "This section reviews the development of Vision-Language-Action models and their
> application to service robotics, providing context for the system implemented in this project."

End each section with a bridge:
> "The limitations of current VLA deployments identified above — particularly inference
> latency and domain specificity — directly motivate the fine-tuning approach undertaken
> in this project."

---

## Connecting the Review to Your Project

Every section should contain at least one sentence explicitly linking reviewed
literature to your implementation. Examples of how to do this:

- "This latency limitation is relevant to the current project, where CPU inference
  on the KRYTN robot requires 30–120 seconds per frame..."
- "The LIBERO spatial benchmark (Kim et al., 2025) serves as the pre-training domain
  for the OpenVLA-OFT checkpoint used in this project, introducing a domain gap
  that motivates the fine-tuning phase described in Section 4."
- "The dual fixed-camera configuration adopted in this project — an entrance camera
  and a far camera — addresses the occlusion problem identified by [source] by
  ensuring continuous coverage of the action space."

---

## Figures

If you include a diagram (e.g., VLA architecture, system pipeline), follow these rules:
- Centre the figure on the page
- Caption: "Figure 3.1: [Description]." — below the figure, numbered by section
- Cite the source at the end of the caption if not your own: "Adapted from Kim et al. (2025)."
- Refer to it in the text before it appears: "...as illustrated in Figure 3.1."
- Do not copy figures from papers without attribution — UWA markers will check

---

## Quick Submission Checklist

- [ ] Written in 3rd person throughout
- [ ] 12pt Times New Roman, 2cm margins, 1.15 or 1.5 line spacing
- [ ] APA 7 citations in-text and in reference list
- [ ] Each paragraph synthesises, not just summarises
- [ ] Each section connects back to the KRYTN / OpenVLA-OFT project
- [ ] Section 3.2 is within the word budget for this submission
- [ ] No verbatim text copied from sources (quote if needed, cite with page number)
- [ ] AI use declared in the signed declaration (UWA policy)
- [ ] Figures captioned and cited
- [ ] Reference list matches all in-text citations exactly
