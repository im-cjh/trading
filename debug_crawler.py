import requests
from bs4 import BeautifulSoup

url = "https://finance.naver.com/news/mainnews.naver"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.encoding = 'EUC-KR'
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Print all classes to see what's available
    print("Classes found:")
    for tag in soup.find_all(True):
        if tag.get('class'):
            print(tag.get('class'))
            
    # Try to find news list
    news_list = soup.select('.mainNewsList li')
    print(f"\nFound {len(news_list)} items with .mainNewsList li")
    
    if not news_list:
        print("\nTrying other selectors...")
        # Print first 500 chars of body to see if it's blocked
        print(soup.body.text[:500] if soup.body else "No body")

except Exception as e:
    print(f"Error: {e}")
