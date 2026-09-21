import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("ELEVENLABS_VOICE_ID")

elevenlabs_client = ElevenLabs(api_key=api_key)

async def generate_audio(text):
      

    audio = elevenlabs_client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_v3"

    )  

    with open("output.mp3", "wb") as f:
        for chunk in audio:
            f.write(chunk)

    print("saved successfully")
