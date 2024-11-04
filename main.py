import requests
from bs4 import BeautifulSoup

def znajdz_artykuly():
    kategoria = input("Wprowadź kategorię: ")
    adres_url = "https://pl.wikipedia.org/wiki/Kategoria:" + kategoria.replace(' ', '_')
    odpowiedz = requests.get(adres_url)

    if odpowiedz.status_code == 200:
        parser_html = BeautifulSoup(odpowiedz.text, "html.parser")
        sekcja_strony = parser_html.find("div", id="mw-pages")

        if sekcja_strony:
            artykuly = [
                {"link": link["href"], "nazwa": link["title"]}
                for link in sekcja_strony.find_all("a") if "title" in link.attrs
            ]

            for indeks, artykul in enumerate(artykuly[:2]):
                pelny_link_artykulu = "https://pl.wikipedia.org" + artykul["link"]
                odpowiedz_artykul = requests.get(pelny_link_artykulu)
                parser_artykul = BeautifulSoup(odpowiedz_artykul.text, "html.parser")

                naglowki = parser_artykul.find('div', id='mw-content-text')
                podtytuly = []
                if naglowki:
                    linki_wewn = naglowki.select('a:not(.extiw)')
                    podtytuly = [l.get('title') for l in linki_wewn if l.get('title') and l.get_text(strip=True)]
                    podtytuly = list(dict.fromkeys(podtytuly))[:5]

                sekcja_tresci = parser_artykul.find("div", class_="mw-content-ltr mw-parser-output")
                obrazy = []
                if sekcja_tresci:
                    obrazy = [img["src"] for img in sekcja_tresci.find_all("img", src=True)[:3]]

                przypisy = parser_artykul.find("ol", class_="references")
                odniesienia = []
                if przypisy:
                    odniesienia = [link.get('href') for link in przypisy.find_all('a', class_='external text') if link.get('href')]

                przypisy_tekstowe = parser_artykul.find_all("li", id=lambda x: x and x.startswith("cite"))
                for przypis in przypisy_tekstowe:
                    link = przypis.find('a', class_='external text')
                    if link and link.get('href'):
                        odniesienia.append(link.get('href'))

                odniesienia = list(dict.fromkeys(odniesienia))[:3]
                odniesienia = [url.replace("&", "&amp;") for url in odniesienia]

                kategorie_sekcja = parser_artykul.find("div", id="mw-normal-catlinks")
                kategorie = [kat.get_text() for kat in kategorie_sekcja.find_all("a")[1:4]] if kategorie_sekcja else []

                print("Tytuły:", " | ".join(podtytuly) if podtytuly else "Brak")
                print("Obrazy:", " | ".join(obrazy) if obrazy else "Brak")
                print("Odniesienia:", " | ".join(odniesienia) if odniesienia else "Brak")
                print("Kategorie:", " | ".join(kategorie) if kategorie else "Brak")
        else:
            print("Brak stron w wybranej kategorii.")
    else:
        print(f"Błąd połączenia: kod {odpowiedz.status_code}")

if __name__ == "__main__":
    znajdz_artykuly()