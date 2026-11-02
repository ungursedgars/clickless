# clickless.lv

Clickless mājaslapa: statiska vietne, publicēta ar GitHub Pages uz domēna `clickless.lv`.

## Kā mainīt
Saknes `*.html` failus **nelabot ar roku**, tos ģenerē `build.py`:

```bash
python build.py
```

| Kur | Kas |
|---|---|
| `dati/piedavajums.json` | viss piedāvājums: jomas, risinājumi (ar statusu), gatavās pakas un cenas, nozares |
| `src/pages/*.html` | lapu saturs: sākums, boti, par mums, kontakti, juridiskās lapas, atsauksme |
| `src/parts/*.html` | kopīgās daļas (sākuma bloks, BUJ, jūsu dati, skripti, logo) |
| `style.css` | stils, gaišā un tumšā tēma |
| `savienot/index.html` | Google OAuth atgriešanās lapa (atsevišķa, neģenerē) |

`risinajumi.html` un `nozares.html` tiek ģenerētas pilnībā no datiem. `build.py` arī izveido
`../lidu-karte.md`: katrai nozarei NACE kodi, meklēšanas vārdi, uzruna un ko piedāvāt (līdu aģentiem).

Jauns risinājums vai nozare: pievieno ierakstu `dati/piedavajums.json` un palaid `python build.py`.

Formas sūta caur Web3Forms. Atsauksmju sadaļa `par-mums.html` ir paslēpta (`hidden`), līdz ir vismaz 3 īstas atsauksmes.
