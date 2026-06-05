# Docker Environment Setup — Café VLA Robot

## Overview
ROS 2 Jazzy + OpenVLA-OFT inference pipeline running in Docker.
CPU-only on dev machine. GPU setup deferred to project machine.

## Folder Structure
```
TestingEnv/
├── Dockerfile
├── docker-compose.yml
├── DOCKER.md
└── ros2_ws/
    └── src/
        ├── vla_inference_node.py
        └── camera_stub_rand_node.py
```

## Prerequisites
- Docker Desktop for Windows installed and running
- WSL2 enabled with Ubuntu distro
- All commands run in Ubuntu WSL2 terminal

## First-Time Setup

### 1. Create workspace folders
```bash
mkdir -p ros2_ws/src
```

### 2. Place files
- `Dockerfile` and `docker-compose.yml` → `TestingEnv/`
- `vla_inference_node.py` and `camera_stub_rand_node.py` → `TestingEnv/ros2_ws/src/`

### 3. Build the image
```bash
docker compose build
```
Takes 5–10 minutes on first run (downloads torch, transformers, ROS 2).

### 4. Start the container
```bash
docker compose up -d
```

## Running the Pipeline

You need three terminals. In each one, exec into the container:
```bash
docker exec -it cafe_vla bash
```

### Terminal A — Camera stub (publishes fake frames)
```bash
source /opt/ros/jazzy/setup.bash
python3 /ros2_ws/src/camera_stub_rand_node.py
```

### Terminal B — VLA inference node
```bash
source /opt/ros/jazzy/setup.bash
python3 /ros2_ws/src/vla_inference_node.py
```
First run downloads ~15 GB of model weights from HuggingFace.
Weights are cached at `~/.cache/huggingface` (mounted from Windows host).

> **Note:** CPU inference is slow (~30–120s per frame). This is expected on the dev machine.
> The pipeline is correct when you see action vectors published to `/cafe/action`.

### Terminal C — Monitor output
```bash
source /opt/ros/jazzy/setup.bash
ros2 topic echo /cafe/action
```

Expected output:
```json
data: '{"frame_id": 1, "action": [0.312, 0.187, 0.445, 0.312, 0.187, 0.445, 0.312], "device": "cpu", "instruction": "Navigate to the delivery table without hitting obstacles."}'
```

## HuggingFace Login (required before first model download)
```bash
docker exec -it cafe_vla bash
pip install huggingface_hub
huggingface-cli login
```
Enter your HuggingFace token when prompted.
Get a token at: https://huggingface.co/settings/tokens

## Useful Commands

| Command | Description |
|---|---|
| `docker compose up -d` | Start container in background |
| `docker compose down` | Stop and remove container |
| `docker compose build` | Rebuild image after Dockerfile changes |
| `docker exec -it cafe_vla bash` | Open a shell in running container |
| `docker logs cafe_vla` | View container logs |
| `ros2 topic list` | List active ROS 2 topics |
| `ros2 topic echo /cafe/action` | Watch action output |
| `ros2 topic echo /cafe/camera` | Watch camera frames |

## GPU Setup (deferred — project machine only)
On the actual project machine (Linux with NVIDIA GPU):
- Switch to WSL2-native Docker (not Docker Desktop)
- Update Dockerfile torch install to `--index-url https://download.pytorch.org/whl/cu124`
- Add `--gpus all` to docker-compose deploy section
- Run `sudo nvidia-ctk runtime configure --runtime=docker`

## Troubleshooting

**`permission denied` on docker socket**
```bash
sudo usermod -aG docker $USER
# Close and reopen Ubuntu terminal
```

**Model download fails**
- Check HuggingFace login: `huggingface-cli whoami`
- Check disk space: need ~15 GB free

**ROS 2 topics not visible across terminals**
- Make sure `ROS_DOMAIN_ID=0` is set in all terminals
- It's set automatically via docker-compose environment

**Container exits immediately**
```bash
docker compose logs
```
