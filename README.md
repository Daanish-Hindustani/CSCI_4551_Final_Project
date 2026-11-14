# CSCI_4551_Final_Project
Csci 4551 final project

```bash
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src --rosdistro jazzy -y
colcon build --symlink-install
source install/setup.bash
ros2 launch so101_description display.launch.py
```
