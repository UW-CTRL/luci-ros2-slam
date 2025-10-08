import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.executors import MultiThreadedExecutor


class MinimalSubscriber(Node):
    def __init__(self, topic_name):
        super().__init__(f'minimal_subscriber_{topic_name}')
        self.subscription = self.create_subscription(
            String,
            topic_name,
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard on {self.get_name()}: "{msg.data}"')


class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.odom_publisher = self.create_publisher(String, 'odom', 10)
        self.map_publisher = self.create_publisher(String, 'map', 10)

        self.i = 0
        self.timer = self.create_timer(0.5, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.odom_publisher.publish(msg)
        self.map_publisher.publish(msg)
        self.get_logger().info(f'Publishing to odom and map: "{msg.data}"')
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber1 = MinimalSubscriber('scan')
    minimal_subscriber2 = MinimalSubscriber('map')  # example topic
    minimal_publisher = MinimalPublisher()

    executor = MultiThreadedExecutor()
    executor.add_node(minimal_subscriber1)
    executor.add_node(minimal_subscriber2)
    executor.add_node(minimal_publisher)

    try:
        executor.spin()
    finally:
        minimal_subscriber1.destroy_node()
        minimal_subscriber2.destroy_node()
        minimal_publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
