# Project Handoff — Café Robot VLA Navigation (UWA GENG5511)

---

*Hey. I'm you — an earlier instance who worked through a lot of this with Joel. You're going to enjoy this one. It's a genuinely interesting project: a real café, a real robot, and a legitimately non-trivial architecture that doesn't fit the usual robotics mould. Joel knows what he's doing — trust him on the design decisions, they're well-reasoned. Your job is to help him execute. Good luck, kid.*

---

## Read this first — architectural constraints that override intuition

This is a robotics project but **do not recommend**:
- Onboard compute upgrades (the robot runs a Raspberry Pi — this is a hardware constraint, not a choice, but it's also not the bottleneck; all ML workload is offloaded to the external server)
- Robot-mounted cameras
- Nav2, SLAM, or map-based navigation stacks
- 7-DOF action spaces or manipulator arm framing

All of those are ruled out by design decisions already locked in. Recommendations that assume otherwise are not useful.

---

## What the system actually looks like

```
[Fixed PoE dome cameras] → RTSP stream
        ↓
[External inference server] — runs OpenVLA-OFT, ROS 2 Humble
        ↓
[4-wheel differential drive robot] — onboard Raspberry Pi
  action space: (linear_vel, angular_vel, stop) only
```

**Key facts:**
- Cameras are **externally mounted** in the café ceiling/walls — not on the robot
- Inference runs on an **external server**, not the robot
- The robot's Raspberry Pi only receives and executes nav commands — no ML workload
- Navigation is **reactive closed-loop replanning** via OpenVLA-OFT, not Nav2
- Training happens separately on a GPU workstation; the ROS 2 pipeline is inference-only

---

## Current hardware status

- **Inference server**: UNRESOLVED. Joel's Lenovo Yoga (Intel Core Ultra 7) is non-functional due to a hardware fault. A replacement or budget-approved machine is needed.
- **Robot**: Existing 4-wheel differential drive platform with Raspberry Pi onboard
- **Cameras**: Not yet purchased — selection is pending


---

## Project context (brief)

- UWA capstone project (GENG5511), 2-semester structure
- Semester 1: infrastructure, pipeline, data collection planning
- Semester 2: fine-tuning, evaluation
- Real café partner, privacy constraints on recording customers → volunteer sessions + simulation data
- Success metric: improvement over existing rule-based system on task completion rate, collision count, avg delivery time

## Dev environment

- ROS 2 Jazzy in Docker (ros:humble-ros-base)
- PyTorch, CPU-only currently
- Windows + WSL2 (Ubuntu 24.04), Docker Desktop
- Model: `moojink/openvla-oft` (HuggingFace, AutoModelForVision2Seq)
- Working stub pipeline validated end-to-end (camera stub → VLA inference node → action publisher)

## Working preferences

- Direct and concise, no hand-holding
- Flag problems immediately
- Code-first where applicable
- IEEE citation format for academic content
- Prioritise 2023–2026 papers when suggesting literature
