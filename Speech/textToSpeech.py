import gtts
from playsound import playsound
import threading
import os

# Text-to-speech
def labelClicked(text):
    try:
        # Specify the text, language, and gender
        language = "en"  # Language code for English
        accent = "us"

        # Create the gTTS object with speed control and male voice
        tts = gtts.gTTS(text, lang=language, slow=False, tld=accent)

        # Save the TTS output to a file
        tts.save("Readable.mp3")

        # Play the generated audio on a separate thread
        audio_thread = threading.Thread(target=playAudio)
        audio_thread.Daemon = True
        audio_thread.start()
    except Exception as e:
        print(f"Failed to play audio: {e}")


def playAudio():
    playsound("Readable.mp3")

    # Delete the file
    os.remove("Readable.mp3")
