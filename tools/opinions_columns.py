import time
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

class Opinion(BaseModel):
    id: int
    title: str
    link: str
    date: Optional[datetime] = None
    is_today: bool
    description: str
    author: Optional[str] = None
    text: Optional[str] = None
    
class OpinionList(BaseModel):
    opinions: list[Opinion]
    

async def get_page_content(url: str, browser_context, timeout: int):
    """
    Get the content of a webpage using the provided browser context.
    
    Args:
        url: The URL of the webpage to fetch
        browser_context: The browser context to use
        timeout: The timeout in milliseconds
    
    Returns:
        The content of the webpage
    """
    page = await browser_context.new_page()
    await page.goto(url, timeout=timeout)
    content = await page.content()
    await page.close()
    return content

async def get_opinion_column_details(content: str):
    """
    Extract article details from the provided HTML content.
    
    Args:
        content: The HTML content of the webpage
        
    Returns:
        A list of Article objects
    """
    soup = BeautifulSoup(content, "lxml")
    opinions_obj = soup.find_all("div", class_="opinion-news-content")
    opinions = []
    
    for i, opinion in enumerate(opinions_obj):
        date_tag = opinion.select_one("div.news-writer-name span.opinion-date")
        date = datetime.strptime(date_tag.text, '%B %d, %Y') if date_tag else None
        
        author_tag = opinion.select_one("div.news-writer-name a")
        author = author_tag.text if author_tag else None
        
        title_tag = opinion.select_one("h4.o-opin-article__title a")
        title = title_tag.text if title_tag else None
        
        link_tag = opinion.select_one("h4.o-opin-article__title a")
        if not link_tag:
            continue
        link = link_tag["href"]
        
        description_tag = opinion.select_one("div.opinion-news-para")
        description = description_tag.text.strip() if description_tag else None
        
        # print(f"Title: {title}, type: {type(title)}")
        # print("\n"+str(article_details[0])+"\n")
        # print(f"Date: {date}, Author: {author}")
        # print(f"Description: {description}")
        # print(f"Link: {link}")
        opinion_obj = Opinion(
            id=i,
            title=title,
            author=author,
            date=date,
            is_today=(
                date.date() == datetime.now().date()
                or date.date() == (datetime.now() - timedelta(days=1)).date()
            ),
            description=description,
            link=link
        )
        if not opinion_obj.is_today:
            break
        opinions.append(opinion_obj)
    
    return OpinionList(opinions=opinions)
    
async def opinions_columns():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        content = await get_page_content("https://indianexpress.com/section/opinion/columns/", browser, 20000)
        opinions = await get_opinion_column_details(content)
        print(opinions)
        return opinions

if __name__ == "__main__":
    import asyncio
    asyncio.run(opinions_columns())
