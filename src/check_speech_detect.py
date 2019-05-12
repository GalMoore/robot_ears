import subprocess
import rospy
import sys
from sys import byteorder
from array import array
from struct import pack
import pyaudio
import wave
import time
from std_msgs.msg import String
from toi_bot_stt.msg import speechTT
import os
import pyaudio
import wave
from array import array
import time




# def finished_speaking():
#     print("finished speaking")
#     #end of recording
#     stream.stop_stream()
#     stream.close()
#     audio.terminate()
#     #writing to file
#     wavfile=wave.open(FILE_NAME,'wb')
#     wavfile.setnchannels(CHANNELS)
#     wavfile.setsampwidth(audio.get_sample_size(FORMAT))
#     wavfile.setframerate(RATE)
#     wavfile.writeframes(b''.join(frames))#append frames recorded to file
#     wavfile.close()

# def detect_and_record():

#     print("here")

#     global has_reached_first_threshold
#     global i 
#     global minimum_tresh_to_trigger_ears

#     while(True):
#         data=stream.read(CHUNK)
#         data_chunk=array('h',data) #data_chunk is an array of 2048 numbers
#         vol=max(data_chunk)

#         # Has not reached first threshold yet
#         if(vol<minimum_tresh_to_trigger_ears and has_reached_first_threshold==False):
#             print("not recording yet - less than vol minimum_tresh_to_trigger_ears!")
        
#         # reached threshold first time
#         if(vol>minimum_tresh_to_trigger_ears and has_reached_first_threshold==False):
#             print("something said - past first thresh - started recording")
#             # set boolean to True for i=84 counts
#             has_reached_first_threshold = True
#             frames.append(data) 

#         if(vol<minimum_tresh_to_trigger_ears and has_reached_first_threshold==True):
#             # allows two second beneath threshold
#             frames.append(data) 
#             if(i==30):
#                 # and then finishes recording
#                 finished_speaking()
#                 return

#         if(vol>minimum_tresh_to_trigger_ears and has_reached_first_threshold==True):
#             frames.append(data) 
#             # reset counter
#             i = 0 

#         i=i+1

print("hey")
# detect_and_record()