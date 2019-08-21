#!/usr/bin/env python

import rospy
import time
from robot_ears.msg import speechTT


if __name__ == '__main__':
    rospy.init_node('one_message_node')

    message = speechTT()
    pub_stt =rospy.Publisher('/stt_topic', speechTT, queue_size=10)

    message.query = 'from'
    message.response = "the"
    message.intent = "script"

    for i in range(2):
        pub_stt.publish(message)
        time.sleep(0.2)

# import os
# os.system("rostopic pub /stt_topic robot_ears/speechTT \"query: 'ya' response: 'ya' intent: 'ya'\"" )
