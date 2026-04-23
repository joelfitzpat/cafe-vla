FROM ros:humble-ros-base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# CPU-only torch — fine for pipeline verification on dev machine
# Switch to cu124 wheel on the actual project GPU machine
RUN pip3 install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu

RUN git clone https://github.com/moojink/openvla-oft.git /opt/openvla-oft

# Install openvla-oft dependencies (custom transformers fork required for bidirectional attn)
RUN pip3 install --no-cache-dir \
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
    tensorflow==2.15.0 \
    tensorflow-datasets==4.9.3 \
    git+https://github.com/moojink/dlimp_openvla
ENV PYTHONPATH="/opt/openvla-oft:${PYTHONPATH}"

RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc

WORKDIR /ros2_ws
CMD ["/bin/bash"]
