import json
from collections import Counter
from typing import List

import requests
from bs4 import BeautifulSoup

URL = "https://www.cfcunderwriting.com"

# List of HTML tags that may contain a link to a reasource
LINKS_TAGS = ["link", "script", "a", "img"]


# List of HTML tag that contain text that is not readable by/visible to reader
TEXT_TAG_BLACKLIST = [
    "select",
    "button",
    "form",
    "meta",
    "[document]",
    "script",
    "option" 
]

def is_ext_link(link: str) -> bool:
    """Check if a link references an external source."""

    return not(link.startswith("/") or link.startswith(URL))


def get_ext_links(html_content: BeautifulSoup) -> List[str]:
    """Returns a list of all links to resource in content provided."""

    ext_links = []

    for l in html_content.find_all(LINKS_TAGS):
        href = l.attrs.get("href")
        src = l.attrs.get("src") 

        link = href or src

        if not link:
            continue
        
        if is_ext_link(link) and link.startswith("http"):
            ext_links.append(link)
        
    return ext_links

def remove_punctuation(text: str) -> str:
    """Removes punctuation from given text."""
    import re


    return re.sub(r"[^\w\s]", " ", text)

     
def get_page_text(html_content: BeautifulSoup) -> List[str]:
    """Returns all visible text from content provided, in lower case."""

    output = ""
    for t in html_content.find_all(text=True):
        if t.parent.name not in TEXT_TAG_BLACKLIST:
            output += t.lower()

    return output
    

def write_to_json(filename: str, content):
    """Write given content to a JSON file."""

    with open(filename, 'w') as json_file:
        json.dump(content, json_file)


def main():
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    ext_links = get_ext_links(soup)
    write_to_json("ext_links.json", ext_links)

    for a in soup.find_all("a"):
        if a.text == "Privacy policy":
            href = URL + a.attrs["href"] 
            response = requests.get(href)
            soup = BeautifulSoup(response.content, 'html.parser')

            text = get_page_text(soup)
            text = remove_punctuation(text).replace("\n", " ").replace("\r", " ").replace("\u00a0", " ")

            word_count = Counter(text.split(" "))
            del word_count[""]

            write_to_json("word_count.json", word_count)
            break

    
if __name__ == "__main__":
    main()