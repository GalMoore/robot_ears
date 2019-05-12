# #!/usr/bin/env python
# # Software License Agreement (BSD License)

# import subprocess
# import rospy
# import sys
# from sys import byteorder
# from array import array
# from struct import pack
# import pyaudio
# import wave
# import time
# from std_msgs.msg import String
# from toi_bot_stt.msg import speechTT
# import os
# import pyaudio
# import wave
# from array import array
# import time
# import matplotlib.pyplot as plt
# import numpy as np
# import wave
# import sys
# from pydub import AudioSegment


# myHome = os.path.expanduser('~')
# message = speechTT()
# pub =rospy.Publisher('/stt_topic', speechTT, queue_size=1)
# FORMAT=pyaudio.paInt16
# CHANNELS=1
# RATE=16000 # takes a few hundread samples per second 
# CHUNK=1024
# FILE_NAME= myHome + '/Desktop/test_ambience.wav'
# audio=pyaudio.PyAudio() #instantiate the pyaudio
# frames=[] #starting recording into this array
# volumes=[]
# i = 0
# tic = time.time()
# boolSpeak = False
# input_num_for_mic_device = None

# def find_avg_vol():

#     # WHEN ENTER FUNCTION RESTART ALL VARS 
#     global i 
#     global stream
#     global audio 
#     global input_num_for_mic_device
#     i = 0

#     # check which input currently in use and set it as input_device_index otherwise use default
#     audio=pyaudio.PyAudio() #instantiate the pyaudio
#     info = audio.get_host_api_info_by_index(0)
#     # print(info)
#     numdevices = info.get('deviceCount')
#     # print(numdevices)
#     for z in range(0, numdevices):
#         if (audio.get_device_info_by_host_api_device_index(0, z).get('maxInputChannels')) > 0:
#         	# print names of found input mic devices
#         	print(audio.get_device_info_by_host_api_device_index(0, z).get('name'))
#         	# if sysdefault found (webcam) set its number as input mic - otherwise remains None
#         	if(audio.get_device_info_by_host_api_device_index(0, z).get('name')=="sysdefault" or audio.get_device_info_by_host_api_device_index(0, z).get('name')=="HP Webcam HD 2300: USB Audio (hw:1,0)"):
#         		print("sysdefault OR HD WECAM found on number / setting mic input as: " + str(z))
#         		input_num_for_mic_device = z
#         	# find 'name' == sysdefault and remember its number and give its 'z' to input_device_index
#             # print "Input Device id ", z, " - ", audio.get_device_info_by_host_api_device_index(0, z).get('name')


#     stream=audio.open(format=FORMAT,channels=CHANNELS,  #recording config
#                   rate=RATE,
#                   input=True,
#                   frames_per_buffer=CHUNK,
#                   input_device_index=input_num_for_mic_device)

#     # AND DELETE PREVIOUS WAV FROM ARRAY OF SOUND DATA
#     del frames[:]

#     while(True):
# 	    # record for x seconds
# 	    data=stream.read(CHUNK)
# 	    data_chunk=array('h',data) #data_chunk is an array of 2048 numbers
# 	    vol=max(data_chunk)
# 	    # print(vol)
# 	    frames.append(data)
# 	    volumes.append(vol)
# 	    if(i==10):
# 	    	# check_avg_vol_in_frames(frames)
# 	    	print(volumes)
# 	    	sum_volumes = sum(volumes)
# 	    	print("sum: " + str(sum_volumes))
# 	    	avg_volume = sum_volumes/len(volumes)
# 	    	print("avg vol: " + str(avg_volume))
# 	    	i = 0 
# 	    	return

# 	    i=i+1
# 	    print(i)








# if __name__ == '__main__':
#     rospy.init_node('test_node')

#     # while(True):
#     find_avg_vol()
#     # normalize(FILE_NAME,-8)

#     # view_wav()



















# # def view_wav():
# # 	spf = wave.open(FILE_NAME,'r')

# # 	#Extract Raw Audio from Wav File
# # 	signal = spf.readframes(-1)
# # 	signal = np.fromstring(signal, 'Int16')
# # 	fs = spf.getframerate()

# # 	#If Stereo
# # 	if spf.getnchannels() == 2:
# # 	    print 'Just mono files'
# # 	    sys.exit(0)


# # 	Time=np.linspace(0, len(signal)/fs, num=len(signal))

# # 	plt.figure(1)
# # 	plt.title('Signal Wave...')
# # 	plt.plot(Time,signal)
# # 	# plt.show()
# # 	plt.draw()
# # 	plt.waitforbuttonpress(0) # this will wait for indefinite time
# # 	plt.close()
