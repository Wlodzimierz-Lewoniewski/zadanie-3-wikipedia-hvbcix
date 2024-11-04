import requests
from bs4 import BeautifulSoup

def search():
    category_name = input()
    wiki_url = "https://pl.wikipedia.org/wiki/Kategoria:" + category_name.replace(' ', '_')
    response = requests.get(wiki_url)

    if response.status_code == 200:
        page = BeautifulSoup(response.text, "html.parser")
        pages_div = page.find("div", id="mw-pages")

        if pages_div:
            wiki_articles = [
                {
                    "url": link["href"], 
                    "title": link["title"]
                }
                for link in pages_div.find_all("a") 
                if "title" in link.attrs
            ]

            for i in range(2):
                if i < len(wiki_articles):
                    current_article = wiki_articles[i]
                    full_url = "https://pl.wikipedia.org" + current_article["url"]
                    article_response = requests.get(full_url)
                    article_page = BeautifulSoup(article_response.text, "html.parser")

                    content = article_page.find('div', {'id': 'mw-content-text'})
                    article_titles = []
                    
                    if content:
                        link_tags = content.select('a:not(.extiw)')
                        article_titles = [
                            link.get('title') 
                            for link in link_tags 
                            if link.get('title') and link.get_text(strip=True)
                        ]
                        article_titles = list(dict.fromkeys(article_titles))[:5]

                    content_div = article_page.find("div", {"class": "mw-content-ltr mw-parser-output"})
                    image_urls = []
                    
                    if content_div:
                        img_tags = content_div.find_all("img", src=True)
                        image_urls = [img["src"] for img in img_tags[:3]]

                    refs_div = article_page.find("ol", {"class": "references"})
                    reference_urls = []
                    
                    if refs_div:
                        ref_links = refs_div.find_all('a', class_='external text')
                        reference_urls.extend([
                            link.get('href') 
                            for link in ref_links 
                            if link.get('href')
                        ])

                    citations = article_page.find_all("li", {"id": lambda x: x and x.startswith("cite")})
                    for citation in citations:
                        ref_link = citation.find('a', class_='external text')
                        if ref_link and ref_link.get('href'):
                            reference_urls.append(ref_link.get('href'))

                    reference_urls = list(dict.fromkeys(reference_urls))[:3]
                    reference_urls = [url.replace("&", "&amp;") for url in reference_urls]

                    categories_div = article_page.find("div", {"id": "mw-normal-catlinks"})
                    category_names = []
                    
                    if categories_div:
                        category_links = categories_div.find_all("a")
                        category_names = [cat.get_text() for cat in category_links[1:4]]

                    titles_output = " | ".join(article_titles) if article_titles else ""
                    images_output = " | ".join(image_urls) if image_urls else ""
                    refs_output = " | ".join(reference_urls) if reference_urls else ""
                    cats_output = " | ".join(category_names) if category_names else ""

                    print(titles_output)
                    print(images_output)
                    print(refs_output)
                    print(cats_output)
        else:
            print("Nie znaleziono stron w tej kategorii.")
    else:
        print(f"Kod statusu: {response.status_code}")

if __name__ == "__main__":
    search()