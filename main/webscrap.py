from urllib.parse import urlparse, urlunparse

import bs4
import requests


# Assuming definitions of cleaned_link and cleaned_image are provided like this:
def cleaned_link(url, link):
    # Dummy implementation: In reality, you'd process and return a cleaned link.
    return link['href']

def cleaned_image(url, img):
    # Dummy implementation: In reality, you'd process and return a cleaned image URL.
    return img['src']

def extract_docs(url, html):
    soup = bs4.BeautifulSoup(html)
    text = None

    title = soup.find("h1", class_="page").text.strip()

    parsed = urlparse(url)
    article = soup.find('article', class_='doc')
    links = article.find_all('a')

    cleaned_links = []

    for link in links:
        if link.get('href') != None and not link.get('href').startswith('#'):
            cleaned_links.append(cleaned_link(url, link))

    sections = []

    for section in soup.select('#preamble, .sect1'):
        header = section.find('h2')
        section_links = [cleaned_link(url, link) for link in section.find_all('a') if link.text != ""]

        anchor = section.find('a', class_='anchor')
        section_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query,
                                  anchor.get('href').replace('#', '') if anchor else 'preamble'))

        code_blocks = []
        for pre in section.find_all('pre'):
            language = pre.find('div', class_="code-inset")
            title = pre.find('div', class_='code-title')
            code = pre.find('code')

            if code:
                code_blocks.append({
                    "language": language.text.strip() if language is not None else None,
                    "title": title.text.strip() if title is not None else None,
                    "code": code.text
                })

    sections.append({
        "url": section_url,
        "title": header.text.strip() if header is not None else None,
        "text": section.text.strip(),
        "anchor": anchor.get('href') if anchor else None,
        "links": section_links,
        "images": [cleaned_image(url, img) for img in section.find_all('img')],
        "code": code_blocks
    })

    return {
        "url": url,
        "title": title,
        "links": cleaned_links,
        "sections": sections
    }

if __name__ == '__main__':
    url = 'https://neo4j.com/docs/cypher-manual/current/introduction/cypher_neo4j/'
    response = requests.get(url)
    # print(response.text)

    extracted_info = extract_docs(url, response.text)

    print(extracted_info)