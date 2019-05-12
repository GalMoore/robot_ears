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

myHome = os.path.expanduser('~')


THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 16000

isRobotSpeaking = False
message = speechTT()
pub =rospy.Publisher('/stt_topic', speechTT, queue_size=1)



# https://stackoverflow.com/questions/892199/detect-record-audio-in-python

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data



def record():
    """
    Record a word or words from the microphone and 
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the 
    start and end, and pads with 0.5 seconds of 
    blank sound to make sure VLC et al can play 
    it without getting chopped off.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')

    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True

        if snd_started and num_silent > 30:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    # r = add_silence(r, 0.1)
    return sample_width, r

# RECORDS 'filename.wav '
def record_to_file(path):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    data = pack('<' + ('h'*len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

def google():
    ''' PYTHON 3 CODE THAT CONVERTS WAV TO STRING AND QUERIES 
    DIALOGFLOW FOR INTENT & RESULT WHICH ARE PRINTED INTO TXT FILES in scropt dialogflowAPI'''
    python_bin = myHome + "/ToiBotEnv/bin/python"
    # # path to the script that must run under the virtualenv
    script_file = myHome + "/toibot_ws/src/ToiBot1/src/toi_bot_stt/src/dialogflowAPI.py"
    # Query Dialogflow, get string and response and write to txt file
    p = subprocess.Popen([python_bin, script_file])
    p_status = p.wait()
    # p.kill()

def recordSentenceToWav():
            # print("")           
            # print("START SPEAKING")
            # print("")
            # # play_wav("start")
            record_to_file(myHome + '/toibot_ws/src/ToiBot1/src/toi_bot_stt/speech_wavs/filename.wav')
            # print("")
            # print("SENDING WAV TO INTERNETS!")
            # print("")
            # play_wav("end")

def send_Wav_to_google_get_response_txt_file_and_publish():

            google()

            # get string from text file and publish it
            pathQuery = myHome + "/toibot_ws/src/ToiBot1/src/toi_bot_stt/text_files/query.txt"
            with open(pathQuery, 'r') as myfile:
                dataQ = myfile.read()
            message.query = dataQ

            pathResponse = myHome + "/toibot_ws/src/ToiBot1/src/toi_bot_stt/text_files/response.txt"
            with open(pathResponse, 'r') as myfile:
                dataR = myfile.read()
            message.response = dataR

             # ADD INTENT TO MESSAGE
            pathIntent = myHome + "/toibot_ws/src/ToiBot1/src/toi_bot_stt/text_files/intent.txt"
            with open(pathIntent, 'r') as myfile:
                dataI = myfile.read()
            message.intent = dataI

            pub.publish(message)
            # delete text files (by opening them in write mode)
            open(pathQuery, 'w').close()
            open(pathResponse, 'w').close()
            open(pathIntent, 'w').close()

# def write_to_file(path,text):
#     # only writes to file if string !empty
#     if text:
#         text_file = open(path, "w")
#         text_file.write(text)
#         text_file.close()


# def callback(data):
    # print("data:data in callback: " + data.data)
    # global isRobotSpeaking 
    # if str(data.data) == "speaking":
    #     isRobotSpeaking = True
    # else:
    #    isRobotSpeaking = False 

    # if (isRobotSpeaking == False):
    #     print("In while loop isRobotSpeaking: " + str(isRobotSpeaking))
    #     recordSentenceToWav()
    #     start = time.time()
    #     send_Wav_to_google_get_response_txt_file_and_publish()
    #     end = time.time()
    #     print("took this long to get response from google and publish to topic:")
    #     print(end-start)        
    # else:
    #     #nothing  
    #     print("nothing")  

    # isRobotSpeaking = data.data
    # print("isRobotSpeaking in callback: " + isRobotSpeaking)

    # write data.data to text file
    #path = "/home/gal/toibot_ws/src/ToiBot1/src/toi_bot_stt/text_files/speaking_or_not.txt"
    #write_to_file(path,data.data)

# def toi_bot_stt():

#         # pub = rospy.Publisher('what_robot_heard_last', String,queue_size=10)
#         # setup publisher
#         #  setup subscriber to check first if robot is speaking
#         # rospy.Subscriber("/is_robot_speaking_topic", String, callback)
#     rospy.Subscriber("/is_robot_speaking_topic", String, callback)
#     rospy.spin()

# def add_silence(snd_data, seconds):
#     "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
#     r = array('h', [0 for i in range(int(seconds*RATE))])
#     r.extend(snd_data)
#     r.extend([0 for i in range(int(seconds*RATE))])
#     return r

isRobotSpeaking 

def callback(data):


    global isRobotSpeaking

    if str(data.data) == "speaking":
        isRobotSpeaking = True
        print('speeeeeeking ')
        print('speeeeeeking ')
        print('speeeeeeking ')
        print('speeeeeeking ')
    else:
         isRobotSpeaking = False
         print('nooooooott   speeeeeeking ')
         print('nooooooott   speeeeeeking ')
         print('nooooooott   speeeeeeking ')




if __name__ == '__main__':
    rospy.init_node('toi_bot_stt_node')

    rospy.Subscriber("/is_robot_speaking_topic", String, callback)

    while(1):

        print(str(isRobotSpeaking))
        if isRobotSpeaking == True:
            print('not record')
        else:
           recordSentenceToWav()
           start = time.time()
           send_Wav_to_google_get_response_txt_file_and_publish()
           end = time.time()
           print("took this long to get response from google and publish to topic:")
           print(end-start)

       # recordSentenceToWav()
       # start = time.time()
       # send_Wav_to_google_get_response_txt_file_and_publish()
       # end = time.time()
       # print("took this long to get response from google and publish to topic:")
       # print(end-start)

        
       
