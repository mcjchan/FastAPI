import requests
from bs4 import BeautifulSoup

stock_symbol = "MSFT"
# Send a request to the website and get the HTML response
url = "http://www.aastocks.com/tc/stocks/news/aafn/popular-news"
response = requests.get(url)

# Parse the HTML content using Beautiful Soup
soup = BeautifulSoup(response.content, 'html.parser')
print(soup)
# Find all the <div> tags with a class attribute that starts with "newshead" and ends with "lettersp2"
headers = soup.find_all("div", {"class": lambda x: x and x.startswith("newshead") and x.endswith("lettersp2")})

# Extract the text from each <div> tag and save it as a list of titles
headers = [title.text.strip() for title in headers]

# Find all the <div> tags with a class attribute that starts with "newscontent" and ends with "lettersp2"
contents = soup.find_all("div", {"class": lambda x: x and x.startswith("newscontent") and x.endswith("lettersp2")})

# Extract the text from each <div> tag and save it as a list of descriptions
contents = [description.text.strip().replace('\n', '').replace('"', '') for description in contents]

# Zip the titles and descriptions lists together
zipped_lists = zip(headers, contents)

news = ""
for header, content in zipped_lists:
    news += f"NewsTitle: {header}\nNewsContent: {content}\n"
