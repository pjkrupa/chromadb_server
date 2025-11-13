from markdownify import markdownify as md
from bs4 import BeautifulSoup
import re

with open("/home/peter/data_projects/chromadb_server/CELEX_32016R0679_EN_TXT.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

for tag in soup(["script", "style", "nav", "footer", "header"]):
    tag.decompose()

for table in soup.find_all("table"):
    text = " ".join(table.stripped_strings)
    table.replace_with(text)

for p in soup.find_all("p"):
    text = p.get_text(strip=True)

    # Detect "Article X", "Section Y", "(1)", "(a)", etc.
    if re.match(r'^(Article|Section)\s+\d+', text, re.I):
        new_tag = soup.new_tag("h2")
        new_tag.string = text
        p.replace_with(new_tag)
    elif re.match(r'^\(\d+\)\s+', text):
        new_tag = soup.new_tag("h3")
        new_tag.string = text
        p.replace_with(new_tag)

clean_html = str(soup)

with open("intermediate.html", "w", encoding="utf-8") as i:
    i.write(clean_html)

markdown = md(clean_html)

with open("/home/peter/data_projects/chromadb_server/CELEX_32016R0679_EN_TXT.md", "w", encoding="utf-8") as md:
    md.write(markdown)
