#!/usr/bin/env python
# Software License Agreement (BSD License)

import subprocess
import rospy
import sys
from sys import byteorder
from array import array
from struct import pack
import pyaudio
import wave
from std_msgs.msg import String, Int16
from robot_ears.msg import speechTT
import os
import pyaudio
import wave
from array import array
import time
from pydub import AudioSegment
from os.path import expanduser
home = expanduser("~") + "/"

volumes=[]
message = speechTT()
# pub =rospy.Publisher('/stt_topic', speechTT, queue_size=1)
# pub_listening =rospy.Publisher('/is_robot_listening', String, queue_size=1)
pub_sound_calib_bool = rospy.Publisher('/is_calibrating', String,latch=True, queue_size=1)
pub_sound_calib_vol = rospy.Publisher('/avg_ambience_vol', Int16,latch=True, queue_size=1)
FORMAT=pyaudio.paInt16
CHANNELS=1
RATE=16000 
CHUNK=516 # CHUNK DETERMINES HOW MANY SAMPLES IN EACH FRAME. SO SMALL CHUNK SPEEDS UP
ACCEPTED_QUITE_FRAMES=30
TIMEOUT=150 # 150 frames (i)
minimum_tresh_to_trigger_ears=6000 # init only
FILE_NAME= home + '/catkin_ws/src/robot_ears/speech_wavs/filename.wav'
NORMALIZED_FILE_NAME = home + '/catkin_ws/src/robot_ears/speech_wavs/normalized.wav'
audio=pyaudio.PyAudio() #instantiate the pyaudio
frames=[] #starting recording into this array
has_reached_first_threshold = False
i = 0
tic = time.time()
boolSpeak = False
input_num_for_mic_device = None
ignore_noise_above_thresh = 12000

def get_avg_ambient_noise(length_of_Ambient_recording):
    global stream
    global audio 
    global input_num_for_mic_device
    global volumes

    n = 0
    audio=pyaudio.PyAudio() #instantiate the pyaudio
    DEVICE_ID = get_index_of_default()
    stream=audio.open(format=FORMAT,channels=CHANNELS,  #recording prerequisites
                  rate=RATE,
                  input=True,
                  frames_per_buffer=CHUNK,
                  input_device_index=DEVICE_ID)

    while(True):
        # record for x seconds
        data=stream.read(CHUNK)
        data_chunk=array('h',data)
        vol=max(data_chunk)
        frames.append(data)
        volumes.append(vol)
        if(n==length_of_Ambient_recording):
            volumes[0] = 300 # can often be a crackly jump so set to modest 300
            print(volumes)
            sum_volumes = sum(volumes)
            avg_volume = sum_volumes/len(volumes)
            print("avg vol: " + str(avg_volume))
            n = 0 
            return avg_volume

        n=n+1
        print("calibrating mic: " + str(n) + " of /" + str(length_of_Ambient_recording))

# select default input
def get_index_of_default():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print "Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name')
            if(p.get_device_info_by_host_api_device_index(0, i).get('name')=="default"):
                return(i)

def write_to_file(path,text):
    if text:
        text_file = open(path, "w")
        text_file.write(text)
        text_file.close()

if __name__ == '__main__':

    rospy.init_node('robot_ears_calibration_node')
    pub_sound_calib_bool = rospy.Publisher('/is_calibrating', String,latch=True, queue_size=1)
    pub_sound_calib_vol = rospy.Publisher('/avg_ambience_vol', Int16,latch=True, queue_size=1)
    path_to_save_txt_vol = "/home/intel/catkin_ws/src/robot_ears/text_files/volume_calib.txt" 

    length_for_calib_from_state = sys.argv[1]
    print(20*"^")
    print("SOUND CALIBRATION >> FINDING AVERAGE VOLUME FOR THRESHOLD")
    print(20* "&")

    pub_sound_calib_bool.publish("True")
    avg_vol_of_ambience = get_avg_ambient_noise(int(length_for_calib_from_state))
    pub_sound_calib_bool.publish("False")

    write_to_file(path_to_save_txt_vol,str(avg_vol_of_ambience))
