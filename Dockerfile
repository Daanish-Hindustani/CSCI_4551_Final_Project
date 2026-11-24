FROM ros:jazzy-ros-base-noble

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-dri \
    novnc \
    openbox \
    python3-colcon-common-extensions \
    ros-jazzy-joint-state-publisher-gui \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-rviz2 \
    websockify \
    x11-utils \
    x11vnc \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-gz-ros2-control \
    ros-jazzy-joint-state-broadcaster \
    ros-jazzy-joint-trajectory-controller \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros2controlcli \
    && rm -rf /var/lib/apt/lists/*

# Perception (so101_perception). Keep in sync with its package.xml.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-numpy \
    python3-opencv \
    ros-jazzy-cv-bridge \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY src/ src/
RUN bash -c 'source /opt/ros/jazzy/setup.bash && colcon build --symlink-install'

COPY docker/start-desktop.sh /usr/local/bin/start-desktop
ENV DISPLAY=:1 LIBGL_ALWAYS_SOFTWARE=1 QT_X11_NO_MITSHM=1
CMD ["bash", "/usr/local/bin/start-desktop"]
