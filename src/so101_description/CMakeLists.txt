cmake_minimum_required(VERSION 3.8)
project(so101_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config launch meshes rviz urdf worlds DESTINATION share/${PROJECT_NAME})
install(FILES LICENSE DESTINATION share/${PROJECT_NAME})
install(PROGRAMS scripts/pick_block DESTINATION lib/${PROJECT_NAME})

ament_package()
