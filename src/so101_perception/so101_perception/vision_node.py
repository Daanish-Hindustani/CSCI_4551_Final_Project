import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge, CvBridgeError
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


COLORS_RANGES = {
    'red': ((0, 100, 100), (10, 255, 255)),
    'green': ((50, 100, 100), (70, 255, 255)),
    'blue': ((100, 100, 100), (130, 255, 255)),
}


def identify_shape(frame: np.ndarray) -> str:
    approx = cv2.approxPolyDP(frame, 0.04 * cv2.arcLength(frame, True), True)
    if len(cv2.boundingRect(approx)) == 4:
        return 'rectangle'

    return 'unknown'


def process(frame: np.ndarray) -> np.ndarray:
    frame = cv2.GaussianBlur(frame, (5, 5), 0)

    for color, (lower, upper) in COLORS_RANGES.items():
        mask = cv2.inRange(cv2.cvtColor(
            frame, cv2.COLOR_BGR2HSV), lower, upper)
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < 100:
                continue

            shape = identify_shape(contour)
            if shape == 'rectangle':
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f'{color} {shape}', (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    annotated = frame.copy()
    cv2.putText(annotated, 'vision_node', (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return annotated


class VisionNode(Node):

    def __init__(self):
        super().__init__('vision_node')
        self.publish_debug_image = self.declare_parameter(
            'publish_debug_image', True).value

        self.bridge = CvBridge()
        # Topic names are generic; remap them in the launch file.
        self.image_sub = self.create_subscription(
            Image, 'image', self.on_image, qos_profile_sensor_data)
        self.debug_pub = self.create_publisher(Image, '~/debug_image', 1)

        self.get_logger().info('vision_node started')

    def on_image(self, msg: Image):
        try:
            # Convert from rgb8 to bgr8 so OpenCV colors are correct.
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except CvBridgeError as error:
            self.get_logger().error(f'cv_bridge conversion failed: {error}')
            return

        annotated = process(frame)

        if self.publish_debug_image and self.debug_pub.get_subscription_count() > 0:
            out = self.bridge.cv2_to_imgmsg(annotated, encoding='bgr8')
            out.header = msg.header
            self.debug_pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
