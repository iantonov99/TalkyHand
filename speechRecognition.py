# for Mac first: brew install portaudio then -> pip3 install pyaudio (use just this command if you are on windows)
#pip install SpeechRecognition
import speech_recognition as sr

with sr.Microphone() as source:
    # create a speech recognition object
    r = sr.Recognizer()
    print("Please talk now...")
    # read the audio data from the default microphone
    audio_data = r.record(source, duration=5, offset=1)
    print("Recognizing...")
    # convert speech to text
    text = r.recognize_google(audio_data)
    print(text)