import time
import openai
import yaml

from bs4 import BeautifulSoup
from pydantic import BaseModel

from .prompts import prompt

class Transcript(BaseModel):
    title: str
    chapters: list[str]

class Response(BaseModel):
    transcript: list[Transcript]

CONFIG = yaml.safe_load(open("config.yaml"))
client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=CONFIG["openrouter_api_key"],
      )

def extract_transcript(text: str) -> list[str]:
    """Extract transcript content from XML response"""
    soup = BeautifulSoup(text, "xml")
    transcripts = soup.find_all("transcript")
    all_chapters = []
    for transcript in transcripts:
        chapters = []
        for chapter in transcript.find_all("chapter"):
            chapters.append(chapter.get_text().replace("\n", " ").strip())
        all_chapters.append(chapters)
    return Response(transcript=[Transcript(title=transcript.get("title").replace(' ', '_'), chapters=chapters) for chapters in all_chapters])

def text_compiler(inputdata:str, max_retries: int = 3):     
    for _ in range(max_retries):
        completion = client.chat.completions.create(
                extra_body={},
                model="openai/gpt-4o-mini",
                messages=[
                {
                    "role": "user",
                    "content": [
                    {
                        "type": "text",
                        "text": prompt.format(articles=inputdata)
                    }
                    ]
                }
                ]
            )
        response = completion.choices[0].message.content
        print(len(response))
        print("\n\n")
        print(response)
        transcript = extract_transcript(response)
        print("\n\n")
        print(transcript)
        if "</transcript>" in response and len(transcript.transcript) > 0 and "</chapter>" in response:
            break
        if all(len(chapter) >= 3800 for chapter in transcript.transcript[0].chapters):
            break
        time.sleep(3)
    return transcript

if __name__ == "__main__":
    ...
