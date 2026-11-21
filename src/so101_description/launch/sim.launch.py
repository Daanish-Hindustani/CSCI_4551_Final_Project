import xml.etree.ElementTree as ET
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, Shutdown
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def simulation_description(package_share):
    robot = ET.parse(package_share / "urdf" / "so101.urdf").getroot()

    for mesh in robot.iter("mesh"):
        filename = mesh.attrib["filename"]
        mesh.set("filename", str(package_share / filename.removeprefix("package://so101_description/")))

    ET.SubElement(robot, "link", name="world")
    anchor = ET.SubElement(robot, "joint", name="world_to_base", type="fixed")
    ET.SubElement(anchor, "parent", link="world")
    ET.SubElement(anchor, "child", link="base_link")
    control = ET.SubElement(robot, "ros2_control", name="SO101", type="system")
    hardware = ET.SubElement(control, "hardware")
    ET.SubElement(hardware, "plugin").text = "gz_ros2_control/GazeboSimSystem"
    for joint in robot.findall("joint[@type='revolute']"):
        controlled_joint = ET.SubElement(control, "joint", name=joint.attrib["name"])
        ET.SubElement(controlled_joint, "command_interface", name="position")
        position = ET.SubElement(controlled_joint, "state_interface", name="position")
        ET.SubElement(position, "param", name="initial_value").text = "0.0"
        ET.SubElement(controlled_joint, "state_interface", name="velocity")

    gazebo = ET.SubElement(robot, "gazebo")
    plugin = ET.SubElement(
        gazebo,
        "plugin",
        filename="libgz_ros2_control-system.so",
        name="gz_ros2_control::GazeboSimROS2ControlPlugin",
    )
    ET.SubElement(plugin, "parameters").text = str(package_share / "config/controllers.yaml")
    return ET.tostring(robot, encoding="unicode")


def generate_launch_description():
    package_share = Path(get_package_share_directory("so101_description"))
    description = ParameterValue(simulation_description(package_share), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument("gui", default_value="true"),
        ExecuteProcess(
            cmd=["gz", "sim", "-s", "-r", str(package_share / "worlds/bench.sdf")],
            output="screen",
            on_exit=Shutdown(reason="Gazebo server stopped"),
        ),
        ExecuteProcess(
            cmd=["gz", "sim", "-g"],
            condition=IfCondition(LaunchConfiguration("gui")),
            output="screen",
        ),
        Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            arguments=[
                "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
                "/overhead_camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image",
                "/overhead_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
            ],
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{"robot_description": description, "use_sim_time": True}],
        ),
        Node(
            package="ros_gz_sim",
            executable="create",
            arguments=["-world", "bench", "-name", "so101", "-topic", "robot_description"],
            output="screen",
        ),
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "joint_state_broadcaster", "arm_controller", "gripper_controller",
                "--controller-manager-timeout", "60",
            ],
            output="screen",
        ),
    ])
