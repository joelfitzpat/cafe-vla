FROM ros:jazzy-ros-base

ENV DEBIAN_FRONTEND=noninteractive

# Add OSRF apt repository for Gazebo Harmonic.
# ros:jazzy-ros-base only has the ROS repo pre-configured — Gazebo Harmonic
# lives in the separate OSRF repo.
RUN apt-get update && apt-get install -y curl \
    && curl -sSL https://packages.osrfoundation.org/gazebo.gpg \
       -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] \
       http://packages.osrfoundation.org/gazebo/ubuntu-stable noble main" \
       > /etc/apt/sources.list.d/gazebo-stable.list \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    git \
    wget \
    libgl1 \
    gz-harmonic \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-cv-bridge \
    ros-jazzy-xacro \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-ament-cmake-auto \
    ros-jazzy-launch-param-builder \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-slam-toolbox \
    ros-jazzy-ros2-control \
    ros-jazzy-ros2-controllers \
    ros-jazzy-gz-ros2-control \
    ros-jazzy-realsense2-description \
    ros-jazzy-rqt-robot-steering \
    ros-jazzy-tf2-ros \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# GPU torch (cu124) — switch to CPU wheel on machines without NVIDIA
# --break-system-packages is required on Ubuntu 24.04 (PEP 668) and is safe inside Docker
RUN pip3 install --no-cache-dir --break-system-packages \
    torch torchvision --index-url https://download.pytorch.org/whl/cu124

RUN git clone https://github.com/moojink/openvla-oft.git /opt/openvla-oft

# Stub training-only modules so the inference import chain doesn't pull in
# dataset loaders (tensorflow_graphics, dlimp, RLDS, etc.) that aren't needed.
RUN echo "# Inference only — training imports stubbed" > /opt/openvla-oft/prismatic/__init__.py \
    && echo "# Inference only — training imports stubbed" > /opt/openvla-oft/prismatic/vla/__init__.py \
    && echo "# Inference only — training imports stubbed" > /opt/openvla-oft/prismatic/training/__init__.py \
    && echo "# Inference only — training imports stubbed" > /opt/openvla-oft/prismatic/vla/datasets/__init__.py \
    && echo "# Inference only — training imports stubbed" > /opt/openvla-oft/prismatic/vla/datasets/rlds/oxe/__init__.py

# Install openvla-oft dependencies (custom transformers fork required for bidirectional attn)
# NOTE: tensorflow pinned to >=2.16.0 — 2.15.x does not support Python 3.12 (Ubuntu 24.04)
RUN pip3 install --no-cache-dir --break-system-packages \
    git+https://github.com/moojink/transformers-openvla-oft.git \
    huggingface_hub \
    accelerate \
    timm==0.9.10 \
    einops \
    pillow \
    draccus \
    json-numpy \
    jsonlines \
    rich \
    sentencepiece==0.1.99 \
    peft==0.11.1 \
    protobuf \
    requests \
    "tensorflow>=2.16.0" \
    "tensorflow-datasets>=4.9.4"

# dlimp declares tensorflow==2.15.0 but that version doesn't support Python 3.12.
# --no-deps skips that check — dlimp's data-loading code is not used during inference.
RUN pip3 install --no-cache-dir --break-system-packages --no-deps \
    git+https://github.com/moojink/dlimp_openvla

RUN pip3 install --no-cache-dir --break-system-packages "diffusers==0.30.3" bitsandbytes

ENV PYTHONPATH="/opt/openvla-oft:${PYTHONPATH}"

# Gazebo needs to know where installed package share dirs live so it can
# resolve model:// URIs and SDF includes after a colcon build.
ENV GZ_SIM_RESOURCE_PATH="/ros2_ws/install/share:/opt/ros/jazzy/share"
ENV SDF_PATH="/ros2_ws/install/share:/opt/ros/jazzy/share"

RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc \
    && echo "source /ros2_ws/install/setup.bash 2>/dev/null || true" >> /root/.bashrc \
    && echo "export GZ_SIM_RESOURCE_PATH=/ros2_ws/install/share:/opt/ros/jazzy/share" >> /root/.bashrc \
    && echo "export SDF_PATH=/ros2_ws/install/share:/opt/ros/jazzy/share" >> /root/.bashrc

WORKDIR /ros2_ws
CMD ["/bin/bash"]
