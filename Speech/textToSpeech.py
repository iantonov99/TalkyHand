import gtts
from playsound import playsound

# Specify the text, language, and gender
text = "Hello world"
language = 'en'  # Language code for English
accent = 'us'

# Create the gTTS object with speed control and male voice
tts = gtts.gTTS(text, lang=language, slow=False, tld=accent)

# Save the TTS output to a file
tts.save("Readable.mp3")

# Play the generated audio
playsound("Readable.mp3")
