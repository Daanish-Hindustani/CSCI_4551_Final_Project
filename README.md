# CSCI_4551_Final_Project
Csci 4551 final project

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch so101_description display.launch.py
```

## Run the SO-101 in Gazebo on your Mac(WILL BE REMOVED PRIOR TO SUBMISSION) - MAC ONLY

Open Docker Desktop and run these commands from the project root:

```bash
docker build -t so101-jazzy .
docker run --rm --init -d --name so101-jazzy -p 127.0.0.1:6080:6080 so101-jazzy
```

If an older `so101-jazzy` container is already running, stop it with
`docker stop so101-jazzy` before starting the new one.

Open [Gazebo in your browser](http://localhost:6080/vnc.html?autoconnect=true).
The SO-101 is fixed to the floor. Gazebo simulates the joints, and the ROS
controllers accept position trajectories in radians.

In a second Mac terminal:

```bash
docker exec -it so101-jazzy bash
source /workspace/install/setup.bash
ros2 control list_controllers
ros2 action send_goal /arm_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory \
  '{trajectory: {joint_names: [shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll], points: [{positions: [0.4, -0.3, 0.4, 0.0, 0.0], time_from_start: {sec: 3}}]}}'
ros2 action send_goal /gripper_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory \
  '{trajectory: {joint_names: [gripper], points: [{positions: [0.7], time_from_start: {sec: 2}}]}}'
```

Stop the container with `docker stop so101-jazzy`. To use the RViz slider
viewer, run the same container command with
`bash /usr/local/bin/start-desktop display.launch.py` after the image name.

The simulated overhead RGB camera publishes images at
`/overhead_camera/image_raw` and calibration information at
`/overhead_camera/camera_info`. It uses 640 × 480 resolution at 15 Hz.
To check that frames are arriving inside the container, run:

```bash
ros2 topic hz /overhead_camera/image_raw
```

## Experimental inverse-kinematics pickup

Rebuild the Docker image after pulling these changes and start the simulation as
above. In another terminal run:

```bash
docker exec -it so101-jazzy bash
source /workspace/install/setup.bash
ros2 run so101_description pick_block
```

The node uses robokin with Placo to solve approach, grasp and lift waypoints for
the green block's initial position. It then sends trajectories to the existing
controllers. To try another position (meters in the robot base frame):

```bash
ros2 run so101_description pick_block --ros-args -p x:=0.18 -p y:=-0.06
```

`grasp_z`, `approach_height`, `open`, and `closed` are also ROS parameters.
The script assumes the block has not moved and does not detect collisions or verify
that the gripper holds it. In a headless Gazebo test, the motion completed but the
green block stayed on the floor; the grasp and simulated contact need tuning. Watch the
simulation and stop it if the arm approaches an obstacle. The Docker image
installs the IK dependencies in `/opt/so101-ik`; a native installation needs the
same Python environment and ROS packages.
