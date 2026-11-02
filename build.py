"""Clickless mājaslapas būvētājs.

Lapas glabājas src/pages/*.html (saturs bez galvenes un kājenes), kopīgās daļas
src/parts/*.html, piedāvājums dati/piedavajums.json. Palaiž:  python build.py
Rezultāts: *.html saknes mapē (tos publicē GitHub Pages) un ../lidu-karte.md aģentiem.

Lapā var lietot:  {{part:nosaukums}}  un  {{gen:generators}}.
risinajumi.html un nozares.html tiek ģenerētas pilnībā no datiem.
"""
import io, json, os, re, html, sys

try:
    sys.stdout.reconfigure(encoding='utf-8')   # Windows konsole citādi nevar izdrukāt ā, ū
except Exception:
    pass

SAKNE = os.path.dirname(os.path.abspath(__file__))
os.chdir(SAKNE)
D = json.load(io.open('dati/piedavajums.json', encoding='utf-8'))
SOL = {r['id']: r for r in D['risinajumi']}
PAKAS = {p['id']: p for p in D['pakas']}
JOMAS = {j['id']: j for j in D['jomas']}
e = html.escape


def part(n):
    return io.open('src/parts/%s.html' % n, encoding='utf-8').read().rstrip('\n')


NAV = [("boti.html", "Gatavie boti", "boti"), ("risinajumi.html", "Risinājumi", "risinajumi"),
       ("nozares.html", "Nozares", "nozares"), ("par-mums.html", "Par mums", "par")]

IKONAS = {
    "doc": '<path d="M7 3h7l5 5v13H7z" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M14 3v5h5M10 13h6M10 17h6" fill="none" stroke="currentColor" stroke-width="1.8"/>',
    "cart": '<path d="M3 4h2l2.4 11h10.2L20 8H6.2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="9" cy="19.5" r="1.5" fill="currentColor"/><circle cx="17" cy="19.5" r="1.5" fill="currentColor"/>',
    "play": '<rect x="3" y="5" width="18" height="14" rx="3" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M10 9.2v5.6l4.8-2.8z" fill="currentColor"/>',
    "team": '<circle cx="9" cy="8.5" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M3.5 19c.6-3.2 2.8-5 5.5-5s4.9 1.8 5.5 5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M15.5 6a3 3 0 010 5.6M17.5 14.3c1.6.6 2.7 2.2 3 4.7" fill="none" stroke="currentColor" stroke-width="1.8"/>',
}


def ikona(n):
    return '<svg viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % IKONAS[n]


def statuss(s):
    return '<span class="status status-%s">%s</span>' % (s, e(D['statusi'][s]['nosaukums']))


# ---------------------------------------------------------------- ģeneratori
def gen_jomas():
    o = ['      <div class="areas">']
    for j in D['jomas']:
        n = sum(1 for r in D['risinajumi'] if r['joma'] == j['id'])
        o.append('        <a class="area" href="risinajumi.html#%s">%s<h3>%s</h3><p>%s</p><span class="area-more">%d risinājumi →</span></a>'
                 % (j['id'], ikona(j['ikona']), e(j['nosaukums']), e(j['isi']), n))
    o.append('      </div>')
    return '\n'.join(o)


def zemaka_cena(p):
    for k, v in p['cenas']:
        if k.startswith('Mēnesī'):
            return v
    return p['cenas'][-1][1]


def gen_pakas_isi():
    o = ['      <div class="mini-products">']
    for pid in ['rekinu-bots', 'kases-zurnals', 'rezervaciju-bots']:
        p = PAKAS[pid]
        o.append('        <a class="mini-product" href="boti.html#%s"><h3>%s</h3><p>%s</p><span class="mini-price">%s mēnesī →</span></a>'
                 % (pid, e(p['nosaukums']), e(p['kam']), e(zemaka_cena(p).replace('+', ''))))
    o.append('      </div>')
    return '\n'.join(o)


def gen_nozares_saites():
    o = ['      <ul class="chips">']
    for n in D['nozares']:
        o.append('        <li><a href="nozares.html#%s">%s</a></li>' % (n['id'], e(n['nosaukums'])))
    o.append('      </ul>')
    return '\n'.join(o)


def produkta_kartite(p):
    cls = 'product featured' if p.get('izcelts') else 'product'
    o = ['        <article class="%s" id="%s">' % (cls, p['id'])]
    if p.get('zime'):
        o.append('          <span class="badge">%s</span>' % e(p['zime']))
    o.append('          <h3>%s</h3>' % e(p['nosaukums']))
    o.append('          <p class="for">%s</p>' % e(p['kam']))
    o.append('          <ul>' + ''.join('<li>%s</li>' % e(x) for x in p['punkti']) + '</ul>')
    o.append('          <div class="price">' + ''.join('<span>%s</span><strong>%s</strong>' % (e(k), e(v)) for k, v in p['cenas']) + '</div>')
    o.append('        </article>')
    return '\n'.join(o)


def gen_pakas():
    o = ['      <div class="products">']
    o += [produkta_kartite(p) for p in D['pakas']]
    o.append('        <article class="product" id="individuali">')
    o.append('          <h3>Individuāls projekts</h3>')
    o.append('          <p class="for">Ja jūsu process neiekļaujas gatavajos botos</p>')
    o.append('          <ul><li>Automatizācija starp jūsu programmām</li><li>Mājaslapas un e-veikali</li><li>Video satura ražošana</li></ul>')
    o.append('          <div class="price">' + ''.join('<span>%s</span><strong>%s</strong>' % (e(k), e(v)) for k, v in D['individuali']) + '</div>')
    o.append('          <a class="link-more" href="risinajumi.html">Visi risinājumi →</a>')
    o.append('        </article>')
    o.append('      </div>')
    o.append('      <p class="price-note">Mēneša maksā iekļauti līdz 500 nolasītiem dokumentiem. Ja mēnesī to ir vairāk, katri nākamie 500 maksā 5 €. Līgumu var izbeigt ar viena mēneša brīdinājumu. Cenas norādītas bez PVN (21%).</p>')
    return '\n'.join(o)


def gen_cta():
    return '''  <section class="band cta-band">
    <div class="wrap cta">
      <div>
        <h2>Neatradāt savu gadījumu?</h2>
        <p class="lead">Pastāstiet, kuru darbu jūs atkārtojat katru dienu, nedēļu vai mēneša beigās. Pirmā saruna ir bez maksas.</p>
      </div>
      <a class="btn btn-primary" href="kontakti.html">Sazināties</a>
    </div>
  </section>'''


GEN = {'jomas': gen_jomas, 'pakas_isi': gen_pakas_isi, 'nozares_saites': gen_nozares_saites,
       'pakas': gen_pakas, 'cta': gen_cta}


# ---------------------------------------------------------------- pilnīgi ģenerētās lapas
def lapa_risinajumi():
    o = ['<!--meta', 'title: Risinājumi – Clickless',
         'description: Ko Clickless var automatizēt: dokumenti un grāmatvedība, e-komercija, YouTube un sociālie tīkli, klienti un komanda.',
         'nav: risinajumi', '-->', '<main>',
         '  <section class="page-hero">', '    <div class="wrap">',
         '      <span class="eyebrow">Risinājumi</span>',
         '      <h1>Ko varam automatizēt</h1>',
         '      <p class="lead">%d risinājumi četrās jomās. Pie katra norādīts, kam tas der, un vai tas ir gatavs produkts, strādā mūsu pašu uzņēmumos vai tiek veidots pēc pasūtījuma.</p>' % len(D['risinajumi']),
         '      <dl class="legend">']
    for k, s in D['statusi'].items():
        o.append('        <div><dt>%s</dt><dd>%s</dd></div>' % (statuss(k), e(s['apraksts'])))
    o += ['      </dl>', '    </div>', '  </section>', '',
          '  <nav class="subnav" aria-label="Jomas">', '    <div class="wrap">']
    o.append('      ' + ''.join('<a href="#%s">%s</a>' % (j['id'], e(j['nosaukums'])) for j in D['jomas']))
    o += ['    </div>', '  </nav>', '']
    for i, j in enumerate(D['jomas']):
        o.append('  <section class="band%s" id="%s">' % (' tint' if i % 2 else '', j['id']))
        o.append('    <div class="wrap">')
        o.append('      <div class="section-head"><h2 class="area-title">%s%s</h2><p class="lead">%s</p></div>' % (ikona(j['ikona']), e(j['nosaukums']), e(j['isi'])))
        o.append('      <div class="solutions">')
        for r in [r for r in D['risinajumi'] if r['joma'] == j['id']]:
            o.append('        <article class="solution" id="%s">' % r['id'])
            o.append('          %s' % statuss(r['statuss']))
            o.append('          <h3>%s</h3>' % e(r['nosaukums']))
            o.append('          <p class="sol-for"><span>Kam der:</span> %s</p>' % e(r['kam']))
            o.append('          <p>%s</p>' % e(r['apraksts']))
            if r.get('paka'):
                o.append('          <a class="link-more" href="boti.html#%s">Cena un detaļas →</a>' % r['paka'])
            o.append('        </article>')
        o += ['      </div>', '    </div>', '  </section>', '']
    o += ['{{gen:cta}}', '</main>']
    return '\n'.join(o)


def lapa_nozares():
    o = ['<!--meta', 'title: Nozares – Clickless',
         'description: Clickless risinājumi pēc nozares: ēdināšana, tirdzniecība, īres dzīvokļi, e-veikali, pakalpojumi, būvniecība, grāmatveži un satura veidotāji.',
         'nav: nozares', '-->', '<main>',
         '  <section class="page-hero">', '    <div class="wrap">',
         '      <span class="eyebrow">Nozares</span>',
         '      <h1>Ko piedāvājam jūsu nozarei</h1>',
         '      <p class="lead">Atrodiet savu nozari: tipiskās problēmas un risinājumi, kas tās atrisina.</p>',
         '    </div>', '  </section>', '',
         '  <nav class="subnav" aria-label="Nozares">', '    <div class="wrap">']
    o.append('      ' + ''.join('<a href="#%s">%s</a>' % (n['id'], e(n['nosaukums'])) for n in D['nozares']))
    o += ['    </div>', '  </nav>', '', '  <section class="band">', '    <div class="wrap industries">']
    for n in D['nozares']:
        o.append('      <article class="industry" id="%s">' % n['id'])
        o.append('        <h2>%s</h2>' % e(n['nosaukums']))
        o.append('        <div class="industry-cols">')
        o.append('          <div><h3>Biežākās problēmas</h3><ul class="problems">%s</ul></div>' % ''.join('<li>%s</li>' % e(x) for x in n['problemas']))
        o.append('          <div><h3>Ko piedāvājam</h3><ul class="offer">%s</ul></div>' % ''.join(
            '<li><a href="risinajumi.html#%s">%s</a>%s</li>' % (s, e(SOL[s]['nosaukums']), statuss(SOL[s]['statuss'])) for s in n['risinajumi']))
        o.append('        </div>')
        if n['pakas']:
            o.append('        <p class="industry-pack">Ieteicamais sākums: %s</p>' % ', '.join(
                '<a href="boti.html#%s">%s</a>' % (p, e(PAKAS[p]['nosaukums'])) for p in n['pakas']))
        o.append('      </article>')
    o += ['    </div>', '  </section>', '', '{{gen:cta}}', '</main>']
    return '\n'.join(o)


# ---------------------------------------------------------------- izkārtojums
def izkartot(saturs, fails):
    m = re.match(r'<!--meta\n(.*?)\n-->\n', saturs, re.S)
    meta = dict(l.split(': ', 1) for l in m.group(1).split('\n')) if m else {}
    saturs = saturs[m.end():] if m else saturs
    for _ in range(3):
        saturs = re.sub(r'\{\{part:(\w+)\}\}', lambda x: part(x.group(1)), saturs)
        saturs = re.sub(r'\{\{gen:(\w+)\}\}', lambda x: GEN[x.group(1)](), saturs)
    akt = meta.get('nav', '')
    nav = '\n'.join('      <a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if k == akt else '', t) for h, t, k in NAV)
    menu = '\n'.join('          <a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if k == akt else '', t) for h, t, k in NAV)
    robots = '\n<meta name="robots" content="noindex">' if meta.get('robots') else ''
    return '''<!doctype html>
<html lang="lv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(title)s</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="%(desc)s">%(robots)s
%(tema_head)s
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&family=Commissioner:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap">
<link rel="stylesheet" href="style.css">
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <a class="logo" href="index.html" aria-label="Clickless sākums">
      %(logo)s
    </a>
    <nav class="nav" aria-label="Galvenā navigācija">
%(nav)s
      <button type="button" id="themeBtn" title="Mainīt gaišo/tumšo režīmu" aria-label="Mainīt gaišo/tumšo režīmu"></button>
      <a class="btn btn-primary btn-sm nav-cta" href="kontakti.html"%(cta_cur)s>Sazināties</a>
      <div class="menu" id="menuDropdown">
        <button type="button" id="menuBtn" title="Izvēlne" aria-label="Izvēlne" aria-haspopup="true" aria-expanded="false" aria-controls="menuList">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg>
        </button>
        <div class="menu-list" id="menuList" hidden>
          <a href="index.html">Sākums</a>
%(menu)s
          <a class="btn btn-primary" href="kontakti.html">Sazināties</a>
        </div>
      </div>
    </nav>
  </div>
</header>

%(saturs)s

<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <strong>CLICKLESS</strong>
      <p>Automatizācija mazajiem uzņēmumiem Latvijā.</p>
      <p>© 2026 CLICKLESS · SIA "UNG STORE", reģ. Nr. 50203319651</p>
    </div>
    <nav aria-label="Lapas">
      <span>Lapas</span>
      <a href="boti.html">Gatavie boti</a>
      <a href="risinajumi.html">Risinājumi</a>
      <a href="nozares.html">Nozares</a>
      <a href="par-mums.html">Par mums</a>
      <a href="kontakti.html">Kontakti</a>
    </nav>
    <nav aria-label="Informācija">
      <span>Informācija</span>
      <a href="privatuma-politika.html">Privātuma politika</a>
      <a href="noteikumi.html">Lietošanas noteikumi</a>
      <a href="atsauksme.html">Atstāt atsauksmi</a>
      <span class="select">info@clickless.lv</span>
    </nav>
  </div>
</footer>

%(js)s
</body>
</html>
''' % {'title': e(meta.get('title', 'Clickless')), 'desc': e(meta.get('description', '')), 'robots': robots,
       'tema_head': part('head_theme').strip(), 'logo': part('logo.svg'), 'nav': nav, 'menu': menu,
       'cta_cur': ' aria-current="page"' if akt == 'kontakti' else '',
       'saturs': saturs.strip('\n'), 'js': part('js_tema') + '\n' + part('js_izvelne')}


def lidu_karte():
    o = ['# Clickless līdu karte', '',
         'Ģenerēts no `clickless-web/dati/piedavajums.json` ar `python clickless-web/build.py`. Nelabot ar roku.', '',
         'Katrai nozarei: kā atrast uzņēmumus (NACE, atslēgvārdi), ko piedāvāt un pirmais teikums uzrunai.', '']
    for n in D['nozares']:
        a = n['agentiem']
        o += ['## ' + n['nosaukums'], '',
              '- **NACE:** ' + ', '.join(a['nace']),
              '- **Meklēšanas vārdi:** ' + ', '.join(a['atslegvardi']),
              '- **Uzruna:** ' + a['uzruna'],
              '- **Problēmas:** ' + '; '.join(n['problemas']),
              '- **Piedāvāt:** ' + ', '.join('%s (%s)' % (SOL[s]['nosaukums'], D['statusi'][SOL[s]['statuss']]['nosaukums']) for s in n['risinajumi']),
              '- **Sākuma paka:** ' + (', '.join(PAKAS[p]['nosaukums'] + ' (' + zemaka_cena(PAKAS[p]) + '/mēn.)' for p in n['pakas']) or '— individuāls piedāvājums'),
              '']
    io.open(os.path.join('..', 'lidu-karte.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(o))


def main():
    lapas = {f: io.open('src/pages/' + f, encoding='utf-8').read() for f in os.listdir('src/pages') if f.endswith('.html')}
    lapas['risinajumi.html'] = lapa_risinajumi()
    lapas['nozares.html'] = lapa_nozares()
    meta_noklusejums = {
        'privatuma-politika.html': 'title: Clickless privātuma politika\ndescription: Kā Clickless apstrādā personas datus un klientu dokumentus.\nnav: -',
        'noteikumi.html': 'title: Clickless lietošanas noteikumi\ndescription: Clickless pakalpojumu lietošanas noteikumi.\nnav: -',
        'atsauksme.html': 'title: Clickless atsauksme\ndescription: Atsauksme par Clickless pakalpojumu.\nnav: -\nrobots: noindex',
    }
    for f, s in lapas.items():
        if not s.startswith('<!--meta') and f in meta_noklusejums:
            s = '<!--meta\n%s\n-->\n' % meta_noklusejums[f] + s
        io.open(f, 'w', encoding='utf-8', newline='\n').write(izkartot(s, f))
    lidu_karte()
    print('Uzbūvētas lapas:', ', '.join(sorted(lapas)))


if __name__ == '__main__':
    main()
