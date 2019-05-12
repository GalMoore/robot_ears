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
import time
from std_msgs.msg import String
# from toi_bot_stt.msg import speechTT
from robot_ears.msg import speechTT
import os
import pyaudio
import wave
from array import array
import time
from pydub import AudioSegment
volumes=[]


myHome = os.path.expanduser('~')
message = speechTT()
pub =rospy.Publisher('/stt_topic', speechTT, queue_size=1)
FORMAT=pyaudio.paInt16
CHANNELS=1
RATE=16000 # takes a few hundread samples per second 
CHUNK=1024
minimum_tresh_to_trigger_ears=6000 # MAKE ASURE INPUT IS THE WEBACAM AND SET TO FULL
FILE_NAME= myHome + '/catkin_ws/src/robot_ears/speech_wavs/filename.wav'
NORMALIZED_FILE_NAME = myHome + '/catkin_ws/src/robot_ears/speech_wavs/normalized.wav'
audio=pyaudio.PyAudio() #instantiate the pyaudio
frames=[] #starting recording into this array
has_reached_first_threshold = False
i = 0
tic = time.time()
boolSpeak = False
input_num_for_mic_device = None




def google():
    ''' PYTHON 3 CODE THAT CONVERTS WAV TO STRING AND QUERIES 
    DIALOGFLOW FOR INTENT & RESULT WHICH ARE PRINTED INTO TXT FILES in scropt dialogflowAPI'''
    python_bin = myHome + "/ToiBotEnv/bin/python"
    # # path to the script that must run under the virtualenv
    script_file = myHome + "/catkin_ws/src/robot_ears/src/dialogflowAPI.py"
    # Query Dialogflow, get string and response and write to txt file
    p = subprocess.Popen([python_bin, script_file])
    p_status = p.wait()
    # p.kill()

def record_sentence_to_wav():
    print("started record_sentence_to_wav()")
    #end of recording
    stream.stop_stream()
    stream.close()
    #writing to file
    wavfile=wave.open(FILE_NAME,'wb')
    wavfile.setnchannels(CHANNELS)
    wavfile.setsampwidth(audio.get_sample_size(FORMAT))
    wavfile.setframerate(RATE)
    wavfile.writeframes(b''.join(frames))#append frames recorded to file
    wavfile.close()
    print("finished creating wav")
    return


def set_threshold_for_speech_rec(current_vol_avg):
    global minimum_tresh_to_trigger_ears

    if 0<current_vol_avg<1000:
        minimum_tresh_to_trigger_ears = 2000
    elif 1000< current_vol_avg<2000:
        minimum_tresh_to_trigger_ears = 4000
    elif 2000<current_vol_avg<4000:
        minimum_tresh_to_trigger_ears = 6000
    else:
        minimum_tresh_to_trigger_ears = 10000





def get_avg_ambient_noise(length_of_Ambient_recording):
    global stream
    global audio 
    global input_num_for_mic_device
    global volumes

    n = 0
    audio=pyaudio.PyAudio() #instantiate the pyaudio

    # # GET THE RIGHT MICROPHONE INPUT (IF NOT PLUGGED IN WILL BE DEFAULT)
    # info = audio.get_host_api_info_by_index(0)
    # numdevices = info.get('deviceCount')
    # for z in range(0, numdevices):
    #     if (audio.get_device_info_by_host_api_device_index(0, z).get('maxInputChannels')) > 0:
    #         # print names of found input mic devices
    #         print(audio.get_device_info_by_host_api_device_index(0, z).get('name'))
    #         # if sysdefault found (webcam) set its number as input mic - otherwise remains None
    #         if(audio.get_device_info_by_host_api_device_index(0, z).get('name')=="sysdefault" or audio.get_device_info_by_host_api_device_index(0, z).get('name')=="HP Webcam HD 2300: USB Audio (hw:1,0)"):
    #             print("sysdefault OR HD WECAM found on number / setting mic input as: " + str(z))
    #             input_num_for_mic_device = z

    stream=audio.open(format=FORMAT,channels=CHANNELS,  #recording prerequisites
                  rate=RATE,
                  input=True,
                  frames_per_buffer=CHUNK)
                  # input_device_index=input_num_for_mic_device)

    while(True):
        # record for x seconds
        data=stream.read(CHUNK)
        data_chunk=array('h',data) #data_chunk is an array of 2048 numbers
        vol=max(data_chunk)
        # print(vol)
        frames.append(data)
        volumes.append(vol)
        if(n==length_of_Ambient_recording):
            # check_avg_vol_in_frames(frames)
            print(volumes)
            sum_volumes = sum(volumes)
            print("sum: " + str(sum_volumes))
            avg_volume = sum_volumes/len(volumes)
            print("avg vol: " + str(avg_volume))
            n = 0 
            # set average volume as average volume (threshold should be 70% louder ??)
            return avg_volume

        n=n+1
        print(n)




def detect_and_record():

    # WHEN ENTER FUNCTION RESTART ALL VARS 
    global has_reached_first_threshold
    global i 
    global minimum_tresh_to_trigger_ears
    global stream
    global audio 
    global input_num_for_mic_device

    has_reached_first_threshold = False
    i = 0
    tic = time.time()

    audio=pyaudio.PyAudio() #instantiate the pyaudio

    stream=audio.open(format=FORMAT,channels=CHANNELS,  #recording prerequisites
                  rate=RATE,
                  input=True,
                  frames_per_buffer=CHUNK)

    # AND DELETE PREVIOUS WAV FROM ARRAY OF SOUND DATA
    del frames[:]

    while(True):
        data=stream.read(CHUNK)
        data_chunk=array('h',data) #data_chunk is an array of 2048 numbers
        vol=max(data_chunk)
        print("frames recorded: " + str(len(frames)) + " current volume:  "+  str(vol) + " thresh: " + str(minimum_tresh_to_trigger_ears))


        # Has not reached first threshold yet
        if(vol<minimum_tresh_to_trigger_ears and has_reached_first_threshold==False):
            # print("not recording yet - less than vol minimum_tresh_to_trigger_ears!")
            pass
        
        # reached threshold for the first time
        if(vol>minimum_tresh_to_trigger_ears and has_reached_first_threshold==False):
            print("past threshold once - started recording")
            has_reached_first_threshold = True
            frames.append(data) 

        # input sound does not reach thresh but first tresh reached
        if(vol<minimum_tresh_to_trigger_ears and has_reached_first_threshold==True):
            # allows some extra time so not to cut you off mid sentence
            frames.append(data) 
            if(i==20):
                # and then finishes recording
                record_sentence_to_wav()
                return

        if(vol>minimum_tresh_to_trigger_ears and has_reached_first_threshold==True):
            frames.append(data) 
            # reset counter
            i = 0 

        i=i+1

def normalize(sound, target_dBFS):

    print("sound is: " + sound)
    print("target_dBFS is: " + str(target_dBFS))

    def match_target_amplitude(sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)

    sound = AudioSegment.from_file(sound, "wav")
    normalized_sound = match_target_amplitude(sound, target_dBFS)
    normalized_sound.export(NORMALIZED_FILE_NAME, format="wav")

def tell_user_acknowledged():

    command = 'python3 /home/gal/toibot_ws/src/ToiBot1/src/motors/src/move_eyes_script.py'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

# # m = motor 
# 0 HEADNOD   (1= down // 9=up)
# 1 HEADTURN  (1= MY left // 9=MY right)
# 2 EYETURN   (1= MY left // 9=MY right)
# 3 LIDBLINK  (1= closed // 9= open)
# 4 TOPLIP    (5= middle // 9= up)
# 5 BOTTOMLIP (5 = middle // 9= down)
# 6 EYETILT   (1 = up // 9= down)



def send_Wav_to_google_get_response_txt_file_and_publish():

            # runs dialogflowAPI.py 
            google()

            # get string from text file and publish it
            pathQuery = myHome + "/catkin_ws/src/robot_ears/text_files/query.txt"
            with open(pathQuery, 'r') as myfile:
                dataQ = myfile.read()
            message.query = dataQ

            pathResponse = myHome + "/catkin_ws/src/robot_ears/text_files/response.txt"
            with open(pathResponse, 'r') as myfile:
                dataR = myfile.read()
            message.response = dataR

            pathIntent = myHome + "/catkin_ws/src/robot_ears/text_files/intent.txt"
            with open(pathIntent, 'r') as myfile:
                dataI = myfile.read()
            message.intent = dataI

            pub.publish(message)

            # after publishing messages delete text files (by opening them in write mode)
            open(pathQuery, 'w').close()
            open(pathResponse, 'w').close()
            open(pathIntent, 'w').close()

def callback(data):
    global boolSpeak
    if (data.data=="speaking"):
        boolSpeak = True
        # print("speaking!!!!")
    else:
        # print("not speaking now at all!")
        boolSpeak = False


if __name__ == '__main__':
    rospy.init_node('robot_ears_node')
    # pub = rospy.Publisher('is_robot_speaking_topic', String,queue_size=1)
    rospy.Subscriber('is_robot_speaking_topic', String, callback)

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("SETTING UP SPEECH TO TEXT CHECK MIC INPUT CONFIG")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


    # record 5 seconds of ambient noise and set treshold for speech recognition
    avg_vol_of_ambience = get_avg_ambient_noise(50)
    set_threshold_for_speech_rec(avg_vol_of_ambience)

    while(True):

        if(boolSpeak == True):
            print("I AM SORRY I CAN NOT LISTN NOW")
            time.sleep(2)
            pass

        else:
            detect_and_record()
            normalize(FILE_NAME,-8)
            # start = time.time()
            tell_user_acknowledged() # runs script to move robot eyes - so we know it heard something
            send_Wav_to_google_get_response_txt_file_and_publish()
            # time.sleep()
            # end = time.time()
            # print("took this long to get response from google and publish to topic:")
            # print(end-start)

