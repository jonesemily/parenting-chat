import requests
from bs4 import BeautifulSoup
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'articles.json')

URL = 'https://www.parents.com/parenting/'


def scrape_articles():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []
    # This selector may need to be updated based on the actual site structure
    for item in soup.select('a.card-article-link'):
        title = item.get_text(strip=True)
        link = item['href']
        if not link.startswith('http'):
            link = 'https://www.parents.com' + link
        articles.append({'title': title, 'url': link})
    return articles


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    articles = scrape_articles()
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(articles, f, indent=2)
    print(f'Scraped {len(articles)} articles to {OUTPUT_FILE}')


if __name__ == '__main__':
    main() 