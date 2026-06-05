# Literature Review — Fillable Template
## GENG5511 Engineering Research Project — UWA
## Joel Fitzpatrick (22736996)

**Note:** This template is for Section 3.2 (Literature Review) of your proposal/final report.
Sections 3.1 and 3.3 stubs are included so you can see where 3.2 sits in context.
Delete all prompt text and [WRITE HERE] placeholders before submitting.
See `lit_review_style_guide.md` for formatting rules.

---

## 3. Introduction, Literature Review, and Project Objectives

---

### 3.1 Introduction

> Introduce the problem: service robots operating in dynamic, human-populated
> environments. Identify the specific limitation of the current system — predetermined
> maps and fixed visual coordinates with no intelligent decision-making. State the
> research hypothesis clearly. End with a signpost sentence describing the structure
> of this section.
>
> Your hypothesis from the progress report is a good starting point:
> "The hypothesis is that replacing the current rule-based system with a fine-tuned
> VLA model will improve navigation fluidity and reduce task failures."
> Sharpen this into a formal research question for the final report.

[WRITE HERE — approximately 200-300 words]

---

### 3.2 Literature Review

> Opening signpost sentence for the whole review — one sentence, tells the reader
> what this section covers and why.

[WRITE HERE — one sentence, e.g., "This section reviews the development of
autonomous navigation systems and Vision-Language-Action models, contextualising
the replacement of rule-based navigation with a fine-tuned OpenVLA-OFT system
in a café service environment."]

---

#### 3.2.1 Autonomous Navigation in Dynamic Indoor Environments

> Start here because it frames the problem your project solves.
> Cover:
> - Why indoor navigation in dynamic, human-populated spaces is hard: partial
>   observability, moving obstacles, unpredictable layouts
> - Current dominant approaches: SLAM, occupancy grids, Nav2/ROS 2 navigation stack
> - Their limitation: rigid, require reprogramming for layout changes, no semantic
>   understanding of the environment
> - Bridge to VLA: why learning-based approaches are being explored as an improvement
>
> Your existing reference is a strong opener here:
> Shanks et al. (2025) argue that "robust navigation in complex, dynamic indoor
> environments remains a central challenge in robotics, requiring agents to make
> adaptive decisions in real time under partial observability and uncertain obstacle
> motion" (p. X). Cite this and build on it.
>
> Add 2-3 more sources on SLAM, Nav2, or indoor navigation challenges.

[WRITE HERE — approximately 150-250 words]

---

#### 3.2.2 Foundation Models and Their Transition to Robotics

> Bridge from traditional navigation to the class of models your project uses.
> Cover:
> - What foundation models are: large models pre-trained on broad data, adaptable
>   via fine-tuning to downstream tasks
> - The progression from language models (LLMs) to vision-language models (VLMs)
>   to action-producing models (VLAs)
> - Early robotics applications: SayCan (Ahn et al., 2022), PaLM-E, RT-2 — what
>   they demonstrated and what remained limited
> - Why language as a task interface suits service robots: flexible instruction
>   ("navigate to the counter") without hard-coded goal states

[WRITE HERE — approximately 150-200 words]

---

#### 3.2.3 Vision-Language-Action Models

> Define VLAs and describe the architectural pattern.
> Cover:
> - Input: visual observations + natural language instruction → output: robot actions
> - Architecture: vision encoder + language backbone + action head
> - RT-2 (Brohan et al., 2023) as the foundational VLA — what it contributed and
>   its limitations (proprietary, high compute, slow inference)
> - OpenVLA as an open-source alternative — trained on Open X-Embodiment dataset,
>   7B parameter Prismatic VLM backbone
> - Trade-offs for service robotics: generalisation vs. latency vs. hardware requirements
>
> End by bridging to the next section: "These limitations motivated the development
> of OpenVLA-OFT, the model deployed in this project."

[WRITE HERE — approximately 200-300 words]

---

#### 3.2.4 OpenVLA-OFT and Fine-Tuning for Deployment

> This is the core of your review — go into the most detail here.
> Cover:
>
> OpenVLA-OFT (Kim, Finn, & Liang, 2025):
> - What OFT (Optimized Fine-Tuning) adds over base OpenVLA:
>   * Action chunking: predicting multiple future timesteps simultaneously,
>     reducing inference call frequency
>   * Parallel decoding: all action tokens decoded at once (not autoregressively),
>     improving speed
>   * Continuous action regression via MLP action head (L1 loss) instead of
>     discretised token prediction — more accurate for smooth motion
>   * Proprioceptive projector: maps robot state into the language embedding space
> - Fine-tuning methodology: LoRA (Low-Rank Adaptation) — describe what this is
>   and why it is appropriate for resource-constrained settings (parameter-efficient,
>   trainable on consumer-grade GPU)
> - LIBERO benchmark: the simulation suite used to fine-tune the checkpoint in this
>   project; describe its scope and note the domain gap introduced by fine-tuning
>   on tabletop manipulation before deploying in a café navigation context
>
> Connect explicitly to your implementation:
> "In this project, the openvla-7b-oft-finetuned-libero-spatial checkpoint is deployed
> with 4-bit quantisation to enable inference on CPU hardware during development,
> with two fixed external cameras providing the dual-image input required by the model."

[WRITE HERE — approximately 300-400 words]

---

#### 3.2.5 Service and Hospitality Robotics

> Contextualise your project within the existing landscape of café/service robots.
> Cover:
> - Existing commercial systems (Servi by Bear Robotics, Keenon robots, Relay by Savioke)
>   — how they navigate and what their limitations are (rule-based, require structured
>   environments, cannot adapt to novel instructions)
> - The gap: no current deployed service robot uses a large VLA model for navigation
>   decision-making
> - Why this matters: smaller operators (like a university café) cannot afford custom
>   programming for every layout change — a language-instructable system is operationally
>   appealing
> - Link to your evaluation metrics: task completion rate, collisions/unplanned stops,
>   average navigation time — explain why these were chosen as meaningful for the
>   service context

[WRITE HERE — approximately 150-200 words]

---

#### 3.2.6 Gaps in Existing Literature

> Synthesise the review into a clear statement of what has NOT been done.
> This earns marks — it justifies why your project is worth doing.
>
> Suggested gaps to discuss (select those most relevant):
> - Large VLA models (7B+) have not been widely deployed in resource-constrained
>   settings (CPU-only, low-VRAM); most published work assumes high-end GPU clusters
> - The LIBERO fine-tuning domain (tabletop manipulation) differs substantially from
>   mobile navigation in dynamic service environments — the transfer challenge is
>   underexplored
> - Fixed external camera setups are underexplored relative to wrist/ego-centric
>   cameras in the VLA literature, despite being more practical for café deployment
> - Real-time action latency for CPU inference remains a barrier not addressed in
>   the published benchmarks
> - Integration of VLA end-to-end control with classical Nav2 navigation planners
>   has not been formally evaluated
>
> Close with a direct statement of how your project addresses these gaps:
> "This project contributes a proof-of-concept integration of OpenVLA-OFT within a
> ROS 2 environment, evaluating the feasibility of VLA-driven navigation in a café
> context and providing a foundation for future fine-tuning on domain-specific data."

[WRITE HERE — approximately 150-250 words]

---

### 3.3 Project Objectives

> Restate and refine your five objectives from the progress report here.
> They should flow naturally from the gaps identified in 3.2.6.
> Make each one specific and measurable (UWA rubric requirement).

[WRITE HERE — your five objectives, as bullet points or numbered list]

---

## References

> APA 7th edition. All sources cited in 3.2 must appear here.
> Starter list below — add all sources you use.

Brohan, A., Brown, N., Carbajal, J., Chebotar, Y., Chen, X., Choromanski, K.,
... & Zeng, A. (2023). RT-2: Vision-language-action models transfer web knowledge
to robotic control. *arXiv preprint arXiv:2307.15818*.

Kim, M. J., Finn, C., & Liang, P. (2025). Fine-tuning vision-language-action
models: Optimizing speed and success. *arXiv preprint arXiv:2502.19645*.

Shanks, S., Embley-Riches, J., Liu, J., Delfaki, A. M., Ciliberto, C., &
Kanoulas, D. (2025). DreamerNav: Learning-based autonomous navigation in dynamic
indoor environments using world models. *Frontiers in Robotics and AI, 12*,
1655171. https://doi.org/10.3389/frobt.2025.1655171

[ADD FURTHER REFERENCES HERE — aim for 8-12 sources in the final report]

---

*Template generated for GENG5511 — Café VLA Robot project, May 2026.*
*Delete all prompt text and placeholders before submitting.*
*Declare AI tool use in your signed declaration per UWA policy.*
