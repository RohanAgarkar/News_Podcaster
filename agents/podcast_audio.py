from openai import OpenAI
import yaml
import datetime

CONFIG = yaml.safe_load(open("config.yaml"))

def podcast_audio(text: str, voice: str = "nova", output_path:str = "output_{}.mp3".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))):
    client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=CONFIG["openrouter_api_key"],
        )
    
    with client.audio.speech.with_streaming_response.create(
            #model="openai/gpt-4o-mini-tts-2025-12-15",
            # model="google/gemini-3.1-flash-tts-preview",
            model="x-ai/grok-voice-tts-1.0",
            input=text,
            voice=voice,
            response_format="mp3"
        ) as response:
        response.stream_to_file(output_path)


if __name__ == "__main__":
    podcast_audio("Hello, this is a test message.", output_path="test.mp3")