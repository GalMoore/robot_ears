#!/home/intel/ToiBotEnv/bin/python
from sys import byteorder
from array import array
from struct import pack
import dialogflow_v2 as dialogflow
import pyaudio
import wave
# from ohbot import ohbot
import time
import sys
# import rospy
import os
# myHome = os.path.expanduser('~')


from os.path import expanduser
home = expanduser("~") + "/"

''' PYTHON 3 CODE THAT CONVERTS WAV 
TO STRING AND QUERIES DIALOGFLOW FOR INTENT & RESULT which are printed into txt files'''

def detect_intent_audio():
    """Returns the result of detect intent with an audio file as input.
    Using the same `session_id` between requests allows continuation
    of the conversation."""
    audio_file_path = home+"catkin_ws/src/robot_ears/speech_wavs/normalized.wav"
    session_client = dialogflow.SessionsClient()

    # Note: hard coding audio_encoding and sample_rate_hertz for simplicity.
    audio_encoding = dialogflow.enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16
    sample_rate_hertz = 16000

    session = session_client.session_path("toibot-1549026967633", "gal1")
    print('Session path: {}\n'.format(session))

    with open(audio_file_path, 'rb') as audio_file:
        input_audio = audio_file.read()

    audio_config = dialogflow.types.InputAudioConfig(
        audio_encoding=audio_encoding, language_code="en",
        sample_rate_hertz=sample_rate_hertz)

    query_input = dialogflow.types.QueryInput(audio_config=audio_config)

    response = session_client.detect_intent(
        session=session, query_input=query_input,
        input_audio=input_audio)

    print('=' * 20)
    # print('Query text: {}'.format(response.query_result.query_text))

    # save string query text to query.txt in /home/gal/toibot_ws/src/ToiBot1/src/toi_bot_stt/text_files
    write_to_file(home+"catkin_ws/src/robot_ears/text_files/query.txt", response.query_result.query_text)
    print("query: " + response.query_result.query_text)
    
    # print('Detected intent: {} (confidence: {})\n'.format(
    #     response.query_result.intent.display_name,
    #     response.query_result.intent_detection_confidence))

    # save string intent to intent.txt in /home/gal/toibot_ws/src/ToiBot1/src/toi_bot_stt/text_files
    write_to_file(home+"catkin_ws/src/robot_ears/text_files/intent.txt", response.query_result.intent.display_name)
    print("response: " + response.query_result.intent.display_name)
    # print('Fulfillment text: {}\n'.format(
    #     response.query_result.fulfillment_text))
    # save string response.txt in /home/gal/toibot_ws/src/ToiBot1/src/toi_bot_stt/text_files
    write_to_file(home+"catkin_ws/src/robot_ears/text_files/response.txt", response.query_result.fulfillment_text)
    print("intent: " + response.query_result.fulfillment_text)

    print('=' * 20)

    # return response
    # return(response.query_result.fulfillment_text)
    # return("returned string from function DIA")

def write_to_file(path,text):
    # only writes to file if string !empty
    if text:
        text_file = open(path, "w")
        text_file.write(text)
        text_file.close()

def main():
    detect_intent_audio()

if __name__ == '__main__':
    main()
    
