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
from std_msgs.msg import String
from robot_ears.msg import speechTT
import os
import pyaudio
import wave
from array import array
import time
from pydub import AudioSegment
import random
volumes=[]
from os.path import expanduser
home = expanduser("~") + "/"

FORMAT=pyaudio.paInt16
CHANNELS=1
RATE=16000 
CHUNK=516 # CHUNK DETERMINES HOW MANY SAMPLES IN EACH FRAME. SO SMALL CHUNK SPEEDS UP I
ACCEPTED_QUITE_FRAMES=30
TIMEOUT=150 # 150 frames (i)
minimum_tresh_to_trigger_ears=6000 # MAKE SURE INPUT IS THE WEBACAM AND SET TO FULL
FILE_NAME= home + 'catkin_ws/src/robot_ears/speech_wavs/filename.wav'
NORMALIZED_FILE_NAME = home + 'catkin_ws/src/robot_ears/speech_wavs/normalized.wav'
audio=pyaudio.PyAudio() #instantiate the pyaudio
frames=[] 
has_reached_first_threshold = False
i = 0
tic = time.time()
boolSpeak = False
ignore_noise_above_thresh = 12000

def google():
    ''' PYTHON 3 CODE THAT CONVERTS WAV TO STRING AND QUERIES 
    DIALOGFLOW FOR INTENT & RESULT WHICH ARE PRINTED INTO TXT FILES in scropt dialogflowAPI'''
    python_bin = home + "ToiBotEnv/bin/python"
    # # path to the script that must run under the virtualenv
    script_file = home + "catkin_ws/src/robot_ears/src/dialogflowAPI.py"
    # Query Dialogflow, get string and response and write to txt file
    p = subprocess.Popen([python_bin, script_file])
    p_status = p.wait()

def record_sentence_to_wav():
    print("started record_sentence_to_wav()")
    #end of recording
    stream.stop_stream()
    stream.close()
    wavfile=wave.open(FILE_NAME,'wb') #writing to file
    wavfile.setnchannels(CHANNELS)
    wavfile.setsampwidth(audio.get_sample_size(FORMAT))
    wavfile.setframerate(RATE)
    wavfile.writeframes(b''.join(frames))#append frames recorded to file
    wavfile.close()
    print("finished creating wav")
    return

def set_threshold_for_speech_rec(current_vol_avg):
    global minimum_tresh_to_trigger_ears
    if 0<=current_vol_avg<=1000:
        minimum_tresh_to_trigger_ears = 3000
    elif 1000< current_vol_avg<2000:
        minimum_tresh_to_trigger_ears = 4000
    elif 2000<current_vol_avg<4000:
        minimum_tresh_to_trigger_ears = 6000
    else:
        minimum_tresh_to_trigger_ears = 10000

def get_index_of_default(): # select default input
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print "Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name')
            if(p.get_device_info_by_host_api_device_index(0, i).get('name')=="default"):
                return(i)

def write_to_file(path,text):
    # only writes to file if string !empty
    if text:
        text_file = open(path, "w")
        text_file.write(text)
        text_file.close()

def detect_and_record():
    global has_reached_first_threshold
    global i 
    global minimum_tresh_to_trigger_ears
    global stream
    global audio 
    global ignore_noise_above_thresh
    has_reached_first_threshold = False
    i = 0
    tic = time.time()
    audio=pyaudio.PyAudio() #instantiate the pyaudio

    DEVICE_ID = get_index_of_default()
    stream=audio.open(format=FORMAT,channels=CHANNELS,  #recording prerequisites
                  rate=RATE,
                  input=True,
                  frames_per_buffer=CHUNK,
                  input_device_index=DEVICE_ID)

    # DELETE PREVIOUS WAV FROM ARRAY OF SOUND DATA
    del frames[:]

    # START RECORDING LOGIC HERE
    while(True):
        data=stream.read(CHUNK) 
        data_chunk=array('h',data)
        vol=max(data_chunk)
        print("frames recorded: " + str(len(frames)) + " current volume:  "+  str(vol) + " thresh: " + str(minimum_tresh_to_trigger_ears))

        # Has not reached first threshold yet
        if(vol<minimum_tresh_to_trigger_ears and has_reached_first_threshold==False):
            frames.append(data)
            if(i>TIMEOUT):
                print("waited till i==" + str(TIMEOUT) + " and thresh not passed - so quitting")
                message.intent = "no words found"
                message.query = "no words found"
                message.response = "no words found"
                # delete the txt files
                write_to_file("/home/intel/catkin_ws/src/robot_ears/text_files/query.txt","")
                write_to_file("/home/intel/catkin_ws/src/robot_ears/text_files/response.txt","")
                write_to_file("/home/intel/catkin_ws/src/robot_ears/text_files/intent.txt","")
                pub_listening.publish("not listening")
                return False
            pass
        
        # reached threshold for the first time
        if(ignore_noise_above_thresh>vol>minimum_tresh_to_trigger_ears and has_reached_first_threshold==False):
            print("<<<past threshold once - started recording>>>")
            has_reached_first_threshold = True
            # delete everything up to 10 frames before beginning
            del frames[:len(frames)-20]
            frames.append(data) 

        # input sound does not reach thresh but first thresh alreadyreached
        if(vol<minimum_tresh_to_trigger_ears and has_reached_first_threshold==True):
            # allows some extra frames below thresh in case sentence not finished yet  
            frames.append(data) 
            if(i==ACCEPTED_QUITE_FRAMES):
                # and then finishes recording
                record_sentence_to_wav()
                return True

        # Threshold is being reached continously and first thresh reached - keep recording
        if(vol>minimum_tresh_to_trigger_ears and has_reached_first_threshold==True):
            frames.append(data) 
            # reset counter
            i = 0 

        i=i+1

def normalize(sound, target_dBFS):
    def match_target_amplitude(sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)

    sound = AudioSegment.from_file(sound, "wav")
    normalized_sound = match_target_amplitude(sound, target_dBFS)
    normalized_sound.export(NORMALIZED_FILE_NAME, format="wav")

def tell_user_acknowledged():

    command = 'python3 {}toibot_ws/src/ToiBot1/src/motors/src/move_eyes_script.py'.format(home)
    os.system(command)

def send_Wav_to_google_get_response_txt_file_and_publish():

            google() # runs dialogflowAPI.py 
            # get string from text file and publish it
            pathQuery = home + "catkin_ws/src/robot_ears/text_files/query.txt"
            with open(pathQuery, 'r') as myfile:
                dataQ = myfile.read()
            message.query = dataQ

            pathResponse = home + "catkin_ws/src/robot_ears/text_files/response.txt"
            with open(pathResponse, 'r') as myfile:
                dataR = myfile.read()
            message.response = dataR

            pathIntent = home + "catkin_ws/src/robot_ears/text_files/intent.txt"
            with open(pathIntent, 'r') as myfile:
                dataI = myfile.read()
            message.intent = dataI

            pub.publish(message)

def callback(data):
    global boolSpeak
    if (data.data=="speaking"):
        boolSpeak = True
    else:
        boolSpeak = False


if __name__ == '__main__':
    rospy.init_node('robot_ears_node_{}'.format(random.randint(0,100)))
    rospy.Subscriber('is_robot_speaking_topic', String, callback)
    message = speechTT()
    pub =rospy.Publisher('/stt_topic', speechTT, queue_size=10)
    pub_listening =rospy.Publisher('/is_robot_listening', String, latch=True,queue_size=10)
    message.query = "init"
    message.response = "init"
    message.intent = "init"
    pub.publish(message)
    pub_listening.publish("not listening")
    avg_vol_of_ambience = int(sys.argv[1])
    print("**********************")
    print("avg_vol_of_ambience is:" + str(avg_vol_of_ambience))
    print("**********************")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("SETTING UP SPEECH TO TEXT CHECK MIC INPUT CONFIG")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    set_threshold_for_speech_rec(avg_vol_of_ambience)
    print("AFTER DECIDING TRIGGER RANGE: MINIMUM_TRESH TO TRIGGER EARS IS: ")
    print(minimum_tresh_to_trigger_ears)

    if(boolSpeak == True):
        print("I AM SORRY I CAN NOT LISTEN NOW")
        time.sleep(2)
        pass

    else:
        pub_listening.publish("listening")
        hello = detect_and_record() # returns True or False 
        if hello==True:
            pub_listening.publish("not listening")
            normalize(FILE_NAME,-8)
            tell_user_acknowledged() # runs script to move robot eyes - so we know it heard something
            send_Wav_to_google_get_response_txt_file_and_publish()



