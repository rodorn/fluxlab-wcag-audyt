# Audyt dostepnosci WCAG 2.2 (axe + raport)

> Darmowy audyt strony w przeglądarce: [fluxlab.pl/audyt-strony](https://fluxlab.pl/audyt-strony?utm_source=github&utm_campaign=fluxlab-wcag-audyt)

Produktyzowane narzedzie do automatycznego audytu dostepnosci cyfrowej stron WWW pod katem
WCAG 2.2 (poziom A i AA), normy EN 301 549 oraz zgodnosci z Europejskim Aktem o Dostepnosci
(EAA) i polska ustawa wdrazajaca. Skanuje strony silnikiem axe-core (przez pa11y), mapuje bledy
na kryteria WCAG, priorytetyzuje je i generuje gotowy raport HTML/PDF dla klienta.

## Co robi

1. **Skan** (`src/scan.py`) uruchamia `pa11y --runner axe --reporter json <url>` na liscie adresow
   z throttlingiem i obsluga bledow. Gdy pa11y/Chrome sa niedostepne, dziala w trybie demo na
   wbudowanym, realistycznym wyniku axe (kontrast, braki alt, ARIA, etykiety, fokus).
2. **Mapowanie** (`src/map_wcag.py`) tlumaczy kody regul axe na kryteria WCAG 2.2 z poziomem
   zgodnosci, odnosnikiem EN 301 549 i priorytetem P1/P2/P3 (priorytet moze byc podniesiony
   przez wage `impact` z axe).
3. **Raport** (`src/report.py`) generuje HTML (i PDF, gdy dostepny wkhtmltopdf albo Chrome
   headless) ze streszczeniem dla zarzadu, ryzykiem kary EAA, tabela niezgodnosci i
   rekomendacjami z fragmentami poprawnego kodu.

## Wymagania

- Python 3.12 lub nowszy
- (opcjonalnie) `pa11y` + Chrome/Chromium do realnego skanu
- (opcjonalnie) `wkhtmltopdf` lub Chrome/Chromium do eksportu PDF

## Uruchomienie

```bash
pip install -r requirements.txt

# tryb demo (bez pa11y, na wbudowanym przykladzie)
python run.py

# realny skan konkretnych adresow (wymaga pa11y + Chrome)
python run.py https://twojafirma.pl https://twojafirma.pl/kontakt

# wymuszenie trybu demo mimo zainstalowanego pa11y
python run.py --demo https://twojafirma.pl
```

Po uruchomieniu sciezka do raportu wypisywana jest na koncu (katalog `raporty/`).

## Podpiecie pa11y i Chrome

```bash
# Node.js wymagany
npm install -g pa11y

# Arch Linux
sudo pacman -S --needed --noconfirm chromium
# lub Debian/Ubuntu
sudo apt-get install -y chromium-browser
```

Jesli pa11y nie znajdzie przegladarki, ustaw zmienna `PUPPETEER_EXECUTABLE_PATH` na sciezke
do Chromium. Bez tych narzedzi narzedzie automatycznie przechodzi w tryb demo, wiec caly
pipeline zawsze da sie uruchomic i przetestowac.

## Testy

```bash
pytest -q
```

CI (`.github/workflows/ci.yml`) uruchamia testy na Pythonie 3.12 oraz smoke run trybu demo.

## Oferta uslugi

Zobacz [oferta.md](oferta.md), pakiety audytu i model wspolpracy.

---

Narzedzie i usluga: **FluxLab** [https://fluxlab.pl](https://fluxlab.pl)
