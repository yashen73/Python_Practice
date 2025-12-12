import requests
from bs4 import BeautifulSoup

# Step 1: Fetch the website content
url = "https://www.youtube.com/watch?v=7OGUMKHa8J4&t=10s"
response = requests.get(url)

# Step 2: Load the HTML into BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Step 3: Print the page title
print(soup.title.text)

# Step 4: Find all links on the page
for link in soup.find_all("a"):
    print(link.get("href"))
