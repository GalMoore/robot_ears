#!/usr/bin/env python
# Software License Agreement (BSD License)

'''
SPEECH TO TEXT NODE
This node constantly listens for speech above THRESHOLD
if found, waits for end of sentence, and send resulting wav file to google to get:
A query in text
B intent
C response
'''

import subprocess
import rospy
from std_msgs.msg import String

from sys import byteorder
from array import array
from struct import pack
import pyaudio
import wave
import time
import sys, os
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
import pyaudio
import os
myHome = os.path.expanduser('~')


#!/usr/bin/env python
from os import environ, path

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

# MODELDIR = "pocketsphinx/model"
# DATADIR = "pocketsphinx/test/data"
def wake_word():
    # Create a decoder with certain model
    config = Decoder.default_config()
    config.set_string('-hmm', myHome+"/toibot_ws/src/ToiBot1/src/toi_bot_stt/model_files_for_wake_word/model/en-us/en-us")
    config.set_string('-lm', myHome+"/toibot_ws/src/ToiBot1/src/toi_bot_stt/model_files_for_wake_word/6204.lm")
    config.set_string('-dict', myHome+"/toibot_ws/src/ToiBot1/src/toi_bot_stt/model_files_for_wake_word/6204.dic")
    decoder = Decoder(config)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    stream.start_stream()

    in_speech_bf = False
    decoder.start_utt()
    while True:
        buf = stream.read(1024)
        if buf:
            decoder.process_raw(buf, False, False)
            if decoder.get_in_speech() != in_speech_bf:
                in_speech_bf = decoder.get_in_speech()
                if not in_speech_bf:
                    decoder.end_utt()
                    print 'Result:', decoder.hyp().hypstr
                    # if decoder.hyp().hypstr=="TOY BOT":
                    if "TOY BOT" in decoder.hyp().hypstr:
                        pub.publish("Wake_word_activated")

                    decoder.start_utt()
        else:
            break
    decoder.end_utt()

if __name__ == '__main__':

        rospy.init_node('wake_word_node')
        pub = rospy.Publisher('wake_word_triggered', String,queue_size=10)
        wake_word()
