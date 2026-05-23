from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

class Article(BaseModel):
    id: int
    title: str
    link: str
    date: datetime
    is_today: bool
    description: str
    text: Optional[str] = None
    
class ArticleList(BaseModel):
    articles: list[Article]
    

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

async def get_article_details(content: str):
    """
    Extract article details from the provided HTML content.
    
    Args:
        content: The HTML content of the webpage
        
    Returns:
        A list of Article objects
    """
    soup = BeautifulSoup(content, "lxml")
    article_details = soup.find_all("div", class_="img-context")
    articles = []
    for i, article in enumerate(article_details):
        date = datetime.strptime(article.find_all("p")[0].text, '%B %d, %Y %I:%M %p')
        article_obj = Article(
            id=i,
            title=article.h3.a.text,
            link=article.h3.a['href'],
            date=date,
            is_today=(
                date.date() == datetime.now().date()
                or date.date() == (datetime.now() - timedelta(days=1)).date()
            ),
            description=article.find_all("p")[1].text
        )
        if not article_obj.is_today:
            break
        articles.append(article_obj)
    return ArticleList(articles=articles)

async def law_explain():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        content = await get_page_content("https://indianexpress.com/about/explained-law/", browser, 20000)
        articles = await get_article_details(content)
        print(articles)
        return articles

if __name__ == "__main__":
    import asyncio
    asyncio.run(law_explain())
