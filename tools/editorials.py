from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

class Editorial(BaseModel):
    id: int
    title: str
    link: str
    date: Optional[datetime] = None
    is_today: bool
    description: str
    text: Optional[str] = None
    
class EditorialList(BaseModel):
    editorials: list[Editorial]
    

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

async def get_editorial_details(content: str):
    """
    Extract article details from the provided HTML content.
    
    Args:
        content: The HTML content of the webpage
        
    Returns:
        A list of Article objects
    """
    soup = BeautifulSoup(content, "lxml")
    editorial_obj = soup.find_all("div", class_="opinion-news-content")
    editorials = []
    
    for i, editorial in enumerate(editorial_obj):
        date_tag = editorial.select_one("div.news-writer-name span.opinion-date")
        date = datetime.strptime(date_tag.text, '%B %d, %Y') if date_tag else None
        
        title_tag = editorial.select_one("h4.o-opin-article__title a")
        title = title_tag.text if title_tag else None
        
        link_tag = editorial.select_one("h4.o-opin-article__title a")
        if not link_tag:
            continue
        link = link_tag["href"]
        
        description_tag = editorial.select_one("div.opinion-news-para")
        description = description_tag.text.strip() if description_tag else None
        
        # print(f"Title: {title}, type: {type(title)}")
        # print("\n"+str(article_details[0])+"\n")
        # print(f"Date: {date}")
        # print(f"Description: {description}")
        # print(f"Link: {link}")
        editorial_obj = Editorial(
            id=i,
            title=title,
            date=date,
            is_today=(
                date.date() == datetime.now().date()
                or date.date() == (datetime.now() - timedelta(days=1)).date()
            ),
            description=description,
            link=link
        )
        if not editorial_obj.is_today:
            break
        editorials.append(editorial_obj)
    
    return EditorialList(editorials=editorials)
    
async def editorials():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        content = await get_page_content("https://indianexpress.com/section/opinion/editorials/", browser, 20000)
        editorials = await get_editorial_details(content)
        print(editorials)
        return editorials

if __name__ == "__main__":
    import asyncio
    asyncio.run(editorials())
