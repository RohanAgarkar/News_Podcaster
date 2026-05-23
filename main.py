from playwright.sync_api import sync_playwright
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
from pydub import AudioSegment

import subprocess
import asyncio
import datetime
import bs4
import yaml
import requests
import os
import tqdm
from dotenv import load_dotenv

load_dotenv()

from tools.editorials import EditorialList, editorials, Editorial
from tools.experts_explain import expert_explain, ArticleList, Article
from tools.law_explain import law_explain
from tools.global_explain import global_explain
from tools.opinions_columns import opinions_columns, OpinionList, Opinion

from agents.podcast_audio import podcast_audio
from agents.text_compiler import text_compiler

# check playwright browser
if not os.path.exists("browser"):
    subprocess.run(["playwright", "install", "chromium-headless-shell"])

CONFIG = yaml.safe_load(open("config.yaml"))

async def gather_data():
    tasks = await asyncio.gather(
        editorials(),
        expert_explain(),
        law_explain(),
        global_explain(),
        opinions_columns(),
    )
    return tasks

def extract_body(data: BaseModel):
    data_key = list(data.__pydantic_fields__.keys())[0]
    data = getattr(data, data_key)
    # prefix = "https://removepaywalls.com/"
    def extract_prefix_1(url):
        req = requests.get(f"https://archivejson-production.up.railway.app/api/json?q={url}&format=html")
        if req.status_code != 200:
            return None
        soup = bs4.BeautifulSoup(req.text, "lxml")
        title = soup.find("h1")
        text = soup.find_all("p")
        return f"{title.get_text().strip()}" + "\n".join([p.get_text().strip() for p in text])

    def extract_prefix_2(url):
        req = requests.get(f"https://accessarticlenow.com/api/c/js?q={url}")
        if req.status_code != 200:
            return None
        soup = bs4.BeautifulSoup(req.text, "lxml")
        title = soup.find("h1", class_="article-main-head")
        if title is None:
            title = soup.find("h1", id="main-heading-article")
        text = soup.find("div", id="pcl-full-content").find_all("p")
        return f"{title.get_text().strip()}" + "\n".join([p.get_text().strip() for p in text])

    for item in data:
        if item.text is None:
            try:
                item.text = extract_prefix_1(item.link)
            except:
                item.text = extract_prefix_2(item.link)
            finally:
                if item.text is None:
                    print(f"Failed to extract text for {item.link}")

    return data

def process_data(data):
    with ThreadPoolExecutor(max_workers=2) as executor:
        for item in data:
            executor.submit(extract_body, item)
        executor.shutdown(wait=True)
    text = ""
    for item in data:
        data_key = list(item.__pydantic_fields__.keys())[0]
        item = getattr(item, data_key)
        for l in item:
            text += l.text + "\n"

    return text

if __name__ == "__main__":
    data = asyncio.run(gather_data())

    # Main logic
    text = text_compiler(process_data(data))
    
    #create dirs
    for t in text.transcript:
        os.makedirs(f"audio/{t.title}", exist_ok=True)
    
    # Create audio files
    for t in text.transcript:
        root_path = f"audio/{t.title}"
        for i, segment in enumerate(tqdm.tqdm(t.chapters, desc=t.title)):
            podcast_audio(segment,voice="ara", output_path=f"{root_path}/segment_{i}.mp3")
            # podcast_audio(segment,voice="Leda", output_path=f"{root_path}/segment_{i}.pcm")

        segments_list = [os.path.join(root_path, segment) for segment in os.listdir(root_path)]
        segments_list.sort(
            key=lambda x: int(
                os.path.basename(x)
                .split("_")[1]
                .split(".")[0]
            )
        )

        combined = AudioSegment.empty()
        for segment in tqdm.tqdm(segments_list, desc=t.title):
            combined += AudioSegment.from_file(segment, format="mp3")
        combined.export(f"{root_path}/{t.title}.mp3", format="mp3")

        # Clean up segment files
        for segment in segments_list:
            os.remove(segment)
