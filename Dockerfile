FROM ros:jazzy-ros-base-noble

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-dri \
    git \
    novnc \
    openbox \
    python3-colcon-common-extensions \
    python3-pip \
    python3-venv \
    ros-jazzy-joint-state-publisher-gui \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-rviz2 \
    websockify \
    x11-utils \
    x11vnc \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv --system-site-packages /opt/so101-ik && \
    /opt/so101-ik/bin/pip install --no-cache-dir 'placo==0.12.0' \
    'robokin[placo] @ git+https://github.com/legalaspro/robokin.git@8ae1ee6eb40095027c373b27e60f1d22f9667a99'

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-gz-ros2-control \
    ros-jazzy-joint-state-broadcaster \
    ros-jazzy-joint-trajectory-controller \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros2controlcli \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY src/ src/
RUN bash -c 'source /opt/ros/jazzy/setup.bash && colcon build'

COPY docker/start-desktop.sh /usr/local/bin/start-desktop
ENV DISPLAY=:1 LIBGL_ALWAYS_SOFTWARE=1 QT_X11_NO_MITSHM=1
CMD ["bash", "/usr/local/bin/start-desktop"]
