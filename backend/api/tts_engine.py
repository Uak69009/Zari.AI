import asyncio
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_AUDIO_DIR = os.path.join(BASE_DIR, "temp_audio")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

async def generate_audio(text: str, message_id: str) -> str:
    """
    Converts Urdu text to spoken audio utilizing edge-tts if available.
    """
    try:
        import edge_tts
        voice = "ur-PK-AsadNeural"
        filepath = os.path.join(TEMP_AUDIO_DIR, f"{message_id}.mp3")
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(filepath)
        return filepath
    except Exception as e:
        print(f"Edge-TTS audio synthesis note: {e}")
        return None
