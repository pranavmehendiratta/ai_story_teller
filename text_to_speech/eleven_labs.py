from elevenlabs import generate, play, save, stream, voices
from elevenlabs.api.voice import Voices, Voice, VoiceSettings
from typing import List

VOICE = Voice(
    voice_id = "AZnzlk1XvdvUeBnXmlld",
    name = "Domi",
    settings = VoiceSettings(
        stability = 0.71, 
        similarity_boost = 0.5, 
        style = 0.0, 
        use_speaker_boost=True
    )
)

def generate_story_audio(text: str, file_path: str):
    audio = generate(
        text = text,
        voice = VOICE
    )
    save(audio, file_path)

def get_voices() -> List[Voice]:
    return voices().voices

def main():
    voices = get_voices()
    for voice in voices:
        print(voice)
        print()

"""
if __name__ == "__main__":
    main()
"""