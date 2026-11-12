"""CLICKLESS mājaslapas būvētājs (latviešu un angļu valoda).

Lapas glabājas src/pages/*.html (saturs bez galvenes un kājenes), kopīgās daļas
src/parts/*.html, piedāvājums dati/piedavajums.json. Angļu versija: src/en/pages,
src/en/parts (ja daļas tur nav, ņem latviešu) un dati/piedavajums.en.json (tikai teksti,
ko pārklāj pēc id). Palaiž:  python build.py
Rezultāts: *.html saknes mapē un en/*.html (tos publicē GitHub Pages) un ../lidu-karte.md aģentiem.

Lapā var lietot:  {{part:nosaukums}}  un  {{gen:generators}}.
risinajumi.html un nozares.html tiek ģenerētas pilnībā no datiem.
"""
import copy, hashlib, io, json, os, re, html, sys

try:
    sys.stdout.reconfigure(encoding='utf-8')   # Windows konsole citādi nevar izdrukāt ā, ū
except Exception:
    pass

SAKNE = os.path.dirname(os.path.abspath(__file__))
os.chdir(SAKNE)
D_LV = json.load(io.open('dati/piedavajums.json', encoding='utf-8'))
e = html.escape

# Saskarnes teksti, kas nav lapu failos.
T_ALL = {
    'lv': {
        'nav': [("boti.html", "Gatavie boti", "boti"), ("risinajumi.html", "Risinājumi", "risinajumi"),
                ("nozares.html", "Nozares", "nozares"), ("par-mums.html", "Par mums", "par")],
        'sakums': 'Sākums', 'sazinaties': 'Sazināties', 'logo_aria': 'CLICKLESS sākums',
        'nav_aria': 'Galvenā navigācija', 'tema': 'Mainīt gaišo/tumšo režīmu', 'izvelne': 'Izvēlne',
        'valoda': 'English', 'valoda_isi': 'EN', 'valoda_kods': 'en',
        'kajene_apraksts': 'Automatizācija mazajiem uzņēmumiem Latvijā.',
        'kajene_firma': '© 2026 CLICKLESS · SIA "UNG STORE", reģ. Nr. 50203319651',
        'lapas': 'Lapas', 'informacija': 'Informācija', 'kontakti': 'Kontakti',
        'privatums': 'Privātuma politika', 'noteikumi': 'Lietošanas noteikumi', 'atsauksme': 'Atstāt atsauksmi',
        'risinajumi_n': '%d risinājumi →', 'menesi_saite': '%s mēnesī →', 'menesi_prefikss': 'Mēnesī',
        'individ_nos': 'Individuāls projekts', 'individ_kam': 'Ja jūsu process neiekļaujas gatavajos botos',
        'individ_punkti': ['Automatizācija starp jūsu programmām', 'Mājaslapas un e-veikali', 'Video satura ražošana'],
        'visi_risinajumi': 'Visi risinājumi →',
        'cenu_piezime': '<strong>Pirmais mēnesis bez maksas:</strong> nekas nav jāparaksta, un karte nav vajadzīga. Uzstādīšanas un mēneša maksa sākas tikai tad, ja izlemjat turpināt. Mēneša maksā iekļauti līdz 500 nolasītiem dokumentiem. Ja mēnesī to ir vairāk, katri nākamie 500 maksā 5 €. Līgumu var izbeigt ar viena mēneša brīdinājumu. Cenas norādītas bez PVN (21%).',
        'cta_h': 'Neatradāt savu gadījumu?',
        'cta_p': 'Pastāstiet, kuru darbu jūs atkārtojat katru dienu, nedēļu vai mēneša beigās. Pirmā saruna ir bez maksas.',
        'ris_title': 'Risinājumi – CLICKLESS',
        'ris_desc': 'Ko CLICKLESS var automatizēt: dokumenti un grāmatvedība, e-komercija, YouTube un sociālie tīkli, klienti un komanda.',
        'ris_eyebrow': 'Risinājumi', 'ris_h1': 'Ko varam automatizēt',
        'ris_lead': '%d risinājumi četrās jomās. Pie katra norādīts, kam tas der, un vai tas ir gatavs produkts, strādā mūsu pašu uzņēmumos vai tiek veidots pēc pasūtījuma.',
        'jomas_aria': 'Jomas', 'kam_der': 'Kam der:', 'cena_detalas': 'Cena un detaļas →',
        'noz_title': 'Nozares – CLICKLESS',
        'noz_desc': 'CLICKLESS risinājumi pēc nozares: ēdināšana, tirdzniecība, īres dzīvokļi, e-veikali, pakalpojumi, būvniecība, grāmatveži un satura veidotāji.',
        'noz_eyebrow': 'Nozares', 'noz_h1': 'Ko piedāvājam jūsu nozarei',
        'noz_lead': 'Atrodiet savu nozari: tipiskās problēmas un risinājumi, kas tās atrisina.',
        'noz_aria': 'Nozares', 'problemas': 'Biežākās problēmas', 'piedavajam': 'Ko piedāvājam',
        'ieteicams': 'Ieteicamais sākums: %s',
        'meta': {
            'privatuma-politika.html': 'title: CLICKLESS privātuma politika\ndescription: Kā CLICKLESS apstrādā personas datus un klientu dokumentus.\nnav: -',
            'noteikumi.html': 'title: CLICKLESS lietošanas noteikumi\ndescription: CLICKLESS pakalpojumu lietošanas noteikumi.\nnav: -',
            'atsauksme.html': 'title: CLICKLESS atsauksme\ndescription: Atsauksme par CLICKLESS pakalpojumu.\nnav: -\nrobots: noindex',
        },
    },
    'en': {
        'nav': [("boti.html", "Ready-made bots", "boti"), ("risinajumi.html", "Solutions", "risinajumi"),
                ("nozares.html", "Industries", "nozares"), ("par-mums.html", "About us", "par")],
        'sakums': 'Home', 'sazinaties': 'Contact us', 'logo_aria': 'CLICKLESS home',
        'nav_aria': 'Main navigation', 'tema': 'Switch light/dark mode', 'izvelne': 'Menu',
        'valoda': 'Latviski', 'valoda_isi': 'LV', 'valoda_kods': 'lv',
        'kajene_apraksts': 'Automation for small businesses in Latvia.',
        'kajene_firma': '© 2026 CLICKLESS · SIA "UNG STORE", reg. No. 50203319651',
        'lapas': 'Pages', 'informacija': 'Information', 'kontakti': 'Contact',
        'privatums': 'Privacy policy', 'noteikumi': 'Terms of use', 'atsauksme': None,
        'risinajumi_n': '%d solutions →', 'menesi_saite': '%s per month →', 'menesi_prefikss': 'Per month',
        'individ_nos': 'Custom project', 'individ_kam': 'When your process does not fit the ready-made bots',
        'individ_punkti': ['Automation between the tools you already use', 'Websites and online shops', 'Video content production'],
        'visi_risinajumi': 'All solutions →',
        'cenu_piezime': '<strong>First month free:</strong> nothing to sign and no card needed. The setup and monthly fees start only if you decide to continue. The monthly fee includes up to 500 documents read. If there are more in a month, each further 500 cost 5 €. You can end the agreement with one month’s notice. Prices exclude VAT (21%).',
        'cta_h': 'Didn’t find your case?',
        'cta_p': 'Tell us which task you repeat every day, every week or at the end of each month. The first call is free.',
        'ris_title': 'Solutions – CLICKLESS',
        'ris_desc': 'What CLICKLESS can automate: documents and bookkeeping, e-commerce, YouTube and social media, customers and team.',
        'ris_eyebrow': 'Solutions', 'ris_h1': 'What we can automate',
        'ris_lead': '%d solutions in four areas. Each one shows who it is for and whether it is a ready-made product, runs in our own companies or is built to order.',
        'jomas_aria': 'Areas', 'kam_der': 'Who it’s for:', 'cena_detalas': 'Price and details →',
        'noz_title': 'Industries – CLICKLESS',
        'noz_desc': 'CLICKLESS solutions by industry: food service, retail, rental apartments, online shops, services, construction, accountants and content creators.',
        'noz_eyebrow': 'Industries', 'noz_h1': 'What we offer your industry',
        'noz_lead': 'Find your industry: the typical problems and the solutions that fix them.',
        'noz_aria': 'Industries', 'problemas': 'Common problems', 'piedavajam': 'What we offer',
        'ieteicams': 'Recommended start: %s',
        'meta': {
            'privatuma-politika.html': 'title: CLICKLESS privacy policy\ndescription: How CLICKLESS processes personal data and client documents.\nnav: -',
            'noteikumi.html': 'title: CLICKLESS terms of use\ndescription: Terms of use for CLICKLESS services.\nnav: -',
        },
    },
}

# Sīkdatņu rīki. Tukšs ID nozīmē, ka rīks netiek ielādēts vispār (arī pēc piekrišanas).
# Meta Pixel ID: Meta Events Manager → Data sources. GA4: Google Analytics → Admin → Data streams (G-...).
SIKDATNES = {'ga4': '', 'meta_pixel': '2250163739249788'}

T_ALL['lv'].update({
    'sik_aria': 'Sīkdatņu piekrišana', 'sik_virsraksts': 'Sīkdatnes',
    'sik_teksts': 'Nepieciešamās sīkdatnes vietnes darbībai izmantojam vienmēr. Analītikas un mārketinga sīkdatnes (Google Analytics, Meta Pixel) ielādējam tikai ar jūsu piekrišanu. <a href="privatuma-politika.html#sikdatnes" data-uz-politiku>Uzzināt vairāk</a>',
    'sik_noraidit': 'Noraidīt', 'sik_iestatijumi': 'Iestatījumi', 'sik_pienemt': 'Piekrītu visām',
    'sik_logs': 'Sīkdatņu iestatījumi', 'sik_aizvert': 'Aizvērt',
    'sik_noraidit_visas': 'Noraidīt visas', 'sik_pienemt_visas': 'Pieņemt visas',
    'sik_ievads': 'Nepieciešamās sīkdatnes nevar atslēgt, jo tās glabā tikai jūsu iestatījumus. Pārējās tiek ielādētas tikai ar jūsu piekrišanu, un izvēli varat mainīt jebkurā brīdī.',
    'sik_nep': 'Nepieciešamās', 'sik_vienmer': 'Vienmēr ieslēgtas',
    'sik_nep_apr': 'Gaišā/tumšā režīma un jūsu sīkdatņu izvēles iestatījumi. Glabājas tikai jūsu pārlūkā.',
    'sik_anal': 'Analītikas', 'sik_anal_apr': 'Google Analytics palīdz saprast, cik apmeklētāju ir vietnē un kuras lapas viņi lasa.',
    'sik_mark': 'Mārketinga', 'sik_mark_apr': 'Meta Pixel (Facebook un Instagram) ļauj mērīt mūsu reklāmu rezultātus un rādīt reklāmas cilvēkiem, kas apmeklējuši vietni.',
    'sik_saglabat': 'Saglabāt izvēli', 'sik_kajene': 'Sīkdatņu iestatījumi',
})
T_ALL['en'].update({
    'sik_aria': 'Cookie consent', 'sik_virsraksts': 'Cookies',
    'sik_teksts': 'We always use the cookies the site needs to work. Analytics and marketing cookies (Google Analytics, Meta Pixel) are loaded only with your consent. <a href="privatuma-politika.html#sikdatnes" data-uz-politiku>Learn more</a>',
    'sik_noraidit': 'Reject', 'sik_iestatijumi': 'Settings', 'sik_pienemt': 'Accept all',
    'sik_logs': 'Cookie settings', 'sik_aizvert': 'Close',
    'sik_noraidit_visas': 'Reject all', 'sik_pienemt_visas': 'Accept all',
    'sik_ievads': 'Necessary cookies cannot be switched off, as they only store your settings. The others are loaded only with your consent, and you can change your choice at any time.',
    'sik_nep': 'Necessary', 'sik_vienmer': 'Always on',
    'sik_nep_apr': 'Light/dark mode and your cookie choice. Stored only in your browser.',
    'sik_anal': 'Analytics', 'sik_anal_apr': 'Google Analytics helps us understand how many people visit the site and which pages they read.',
    'sik_mark': 'Marketing', 'sik_mark_apr': 'Meta Pixel (Facebook and Instagram) lets us measure our ads and show ads to people who have visited the site.',
    'sik_saglabat': 'Save choice', 'sik_kajene': 'Cookie settings',
})

# Google Consent Mode v2: noklusējums "viss liegts" pirms jebkura Google vai Meta skripta.
SIK_HEAD = '''<script>
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied', wait_for_update: 500 });
</script>'''


def sikdatnes_html():
    """Josla, iestatījumu logs un loģika (pēc pvnkalkulators.eu parauga, ar "Noraidīt" jau pirmajā līmenī)."""
    s = {k: T[k] for k in T if k.startswith('sik_')}
    sw = lambda i, n: '<button type="button" class="switch" id="%s" role="switch" aria-checked="false" aria-labelledby="%sNos"><span class="knob"></span></button>' % (i, i)
    return '''<div id="cookieBanner" role="dialog" aria-live="polite" aria-label="%(sik_aria)s">
  <div class="cookie-inner">
    <div class="cookie-text"><strong class="cookie-title">%(sik_virsraksts)s</strong> %(sik_teksts)s</div>
    <div class="cookie-actions"><button id="cookieReject" type="button">%(sik_noraidit)s</button><button id="cookieSettingsBtn" type="button">%(sik_iestatijumi)s</button><button id="cookieAccept" type="button">%(sik_pienemt)s</button></div>
  </div>
</div>
<div id="cookiePrefs" role="dialog" aria-modal="true" aria-labelledby="prefsTitle">
  <div class="prefs-card">
    <div class="prefs-head"><h2 id="prefsTitle">%(sik_logs)s</h2><button id="prefsClose" type="button" aria-label="%(sik_aizvert)s">✕</button></div>
    <div class="prefs-top-actions"><button id="prefsRejectAll" type="button">%(sik_noraidit_visas)s</button><button id="prefsAcceptAll" type="button">%(sik_pienemt_visas)s</button></div>
    <p class="prefs-intro">%(sik_ievads)s</p>
    <div class="prefs-cat"><div class="prefs-cat-row"><span class="prefs-cat-name">%(sik_nep)s</span><span class="prefs-always">%(sik_vienmer)s</span></div><p class="prefs-cat-desc">%(sik_nep_apr)s</p></div>
    <div class="prefs-cat"><div class="prefs-cat-row"><span class="prefs-cat-name" id="swAnalyticsNos">%(sik_anal)s</span>%(sw_a)s</div><p class="prefs-cat-desc">%(sik_anal_apr)s</p></div>
    <div class="prefs-cat"><div class="prefs-cat-row"><span class="prefs-cat-name" id="swMarketingNos">%(sik_mark)s</span>%(sw_m)s</div><p class="prefs-cat-desc">%(sik_mark_apr)s</p></div>
    <button id="prefsSave" type="button">%(sik_saglabat)s</button>
  </div>
</div>
''' % dict(s, sw_a=sw('swAnalytics', ''), sw_m=sw('swMarketing', '')) + part('js_sikdatnes').replace('__GA4__', SIKDATNES['ga4']).replace('__PIXEL__', SIKDATNES['meta_pixel'])


# Pašreizējā valoda: uzstāda iestatit_valodu().
VAL = 'lv'
T = T_ALL['lv']
D = D_LV
SOL = PAKAS = JOMAS = {}


def parklat(lv, en):
    """Angļu teksti pārklāj latviešu datus pēc id; struktūra un saites paliek kopīgas."""
    d = copy.deepcopy(lv)
    for k, v in en.items():
        if k.startswith('_'):
            continue
        if isinstance(v, list) and v and isinstance(v[0], dict) and 'id' in v[0]:
            pec_id = {x['id']: x for x in v}
            for x in d[k]:
                x.update({kk: vv for kk, vv in pec_id.get(x['id'], {}).items() if kk != 'id'})
        elif isinstance(v, dict) and isinstance(d.get(k), dict):
            for kk, vv in v.items():
                d[k].setdefault(kk, {}).update(vv) if isinstance(vv, dict) else d[k].__setitem__(kk, vv)
        else:
            d[k] = v
    return d


def iestatit_valodu(v):
    global VAL, T, D, SOL, PAKAS, JOMAS
    VAL, T = v, T_ALL[v]
    D = D_LV if v == 'lv' else parklat(D_LV, json.load(io.open('dati/piedavajums.en.json', encoding='utf-8')))
    SOL = {r['id']: r for r in D['risinajumi']}
    PAKAS = {p['id']: p for p in D['pakas']}
    JOMAS = {j['id']: j for j in D['jomas']}


def part(n):
    if VAL != 'lv' and os.path.exists('src/%s/parts/%s.html' % (VAL, n)):
        return io.open('src/%s/parts/%s.html' % (VAL, n), encoding='utf-8').read().rstrip('\n')
    return io.open('src/parts/%s.html' % n, encoding='utf-8').read().rstrip('\n')


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
        o.append('        <a class="area" href="risinajumi.html#%s">%s<h3>%s</h3><p>%s</p><span class="area-more">%s</span></a>'
                 % (j['id'], ikona(j['ikona']), e(j['nosaukums']), e(j['isi']), T['risinajumi_n'] % n))
    o.append('      </div>')
    return '\n'.join(o)


def zemaka_cena(p, prefikss=None):
    for k, v in p['cenas']:
        if k.startswith(prefikss or T['menesi_prefikss']):
            return v
    return p['cenas'][-1][1]


def gen_pakas_isi():
    o = ['      <div class="mini-products">']
    for pid in ['rekinu-bots', 'kases-zurnals', 'rezervaciju-bots']:
        p = PAKAS[pid]
        o.append('        <a class="mini-product" href="boti.html#%s"><h3>%s</h3><p>%s</p><span class="mini-price">%s</span></a>'
                 % (pid, e(p['nosaukums']), e(p['kam']), e(T['menesi_saite'] % zemaka_cena(p).replace('+', ''))))
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
    o.append('          <h3>%s</h3>' % e(T['individ_nos']))
    o.append('          <p class="for">%s</p>' % e(T['individ_kam']))
    o.append('          <ul>' + ''.join('<li>%s</li>' % e(x) for x in T['individ_punkti']) + '</ul>')
    o.append('          <div class="price">' + ''.join('<span>%s</span><strong>%s</strong>' % (e(k), e(v)) for k, v in D['individuali']) + '</div>')
    o.append('          <a class="link-more" href="risinajumi.html">%s</a>' % T['visi_risinajumi'])
    o.append('        </article>')
    o.append('      </div>')
    o.append('      <p class="price-note">%s</p>' % T['cenu_piezime'])
    return '\n'.join(o)


def gen_cta():
    return '''  <section class="band cta-band">
    <div class="wrap cta">
      <div>
        <h2>%s</h2>
        <p class="lead">%s</p>
      </div>
      <a class="btn btn-primary" href="kontakti.html">%s</a>
    </div>
  </section>''' % (T['cta_h'], T['cta_p'], T['sazinaties'])


GEN = {'jomas': gen_jomas, 'pakas_isi': gen_pakas_isi, 'nozares_saites': gen_nozares_saites,
       'pakas': gen_pakas, 'cta': gen_cta}


# ---------------------------------------------------------------- pilnīgi ģenerētās lapas
def lapa_risinajumi():
    o = ['<!--meta', 'title: ' + T['ris_title'], 'description: ' + T['ris_desc'],
         'nav: risinajumi', '-->', '<main>',
         '  <section class="page-hero">', '    <div class="wrap">',
         '      <span class="eyebrow">%s</span>' % T['ris_eyebrow'],
         '      <h1>%s</h1>' % T['ris_h1'],
         '      <p class="lead">%s</p>' % (T['ris_lead'] % len(D['risinajumi'])),
         '      <dl class="legend">']
    for k, s in D['statusi'].items():
        o.append('        <div><dt>%s</dt><dd>%s</dd></div>' % (statuss(k), e(s['apraksts'])))
    o += ['      </dl>', '    </div>', '  </section>', '',
          '  <nav class="subnav" aria-label="%s">' % T['jomas_aria'], '    <div class="wrap">']
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
            o.append('          <p class="sol-for"><span>%s</span> %s</p>' % (T['kam_der'], e(r['kam'])))
            o.append('          <p>%s</p>' % e(r['apraksts']))
            if r.get('paka'):
                o.append('          <a class="link-more" href="boti.html#%s">%s</a>' % (r['paka'], T['cena_detalas']))
            o.append('        </article>')
        o += ['      </div>', '    </div>', '  </section>', '']
    o += ['{{gen:cta}}', '</main>']
    return '\n'.join(o)


def lapa_nozares():
    o = ['<!--meta', 'title: ' + T['noz_title'], 'description: ' + T['noz_desc'],
         'nav: nozares', '-->', '<main>',
         '  <section class="page-hero">', '    <div class="wrap">',
         '      <span class="eyebrow">%s</span>' % T['noz_eyebrow'],
         '      <h1>%s</h1>' % T['noz_h1'],
         '      <p class="lead">%s</p>' % T['noz_lead'],
         '    </div>', '  </section>', '',
         '  <nav class="subnav" aria-label="%s">' % T['noz_aria'], '    <div class="wrap">']
    o.append('      ' + ''.join('<a href="#%s">%s</a>' % (n['id'], e(n['nosaukums'])) for n in D['nozares']))
    o += ['    </div>', '  </nav>', '', '  <section class="band">', '    <div class="wrap industries">']
    for n in D['nozares']:
        o.append('      <article class="industry" id="%s">' % n['id'])
        o.append('        <h2>%s</h2>' % e(n['nosaukums']))
        o.append('        <div class="industry-cols">')
        o.append('          <div><h3>%s</h3><ul class="problems">%s</ul></div>' % (T['problemas'], ''.join('<li>%s</li>' % e(x) for x in n['problemas'])))
        o.append('          <div><h3>%s</h3><ul class="offer">%s</ul></div>' % (T['piedavajam'], ''.join(
            '<li><a href="risinajumi.html#%s">%s</a>%s</li>' % (s, e(SOL[s]['nosaukums']), statuss(SOL[s]['statuss'])) for s in n['risinajumi'])))
        o.append('        </div>')
        if n['pakas']:
            o.append('        <p class="industry-pack">%s</p>' % (T['ieteicams'] % ', '.join(
                '<a href="boti.html#%s">%s</a>' % (p, e(PAKAS[p]['nosaukums'])) for p in n['pakas'])))
        o.append('      </article>')
    o += ['    </div>', '  </section>', '', '{{gen:cta}}', '</main>']
    return '\n'.join(o)


# ---------------------------------------------------------------- izkārtojums
def adrese(valoda, fails):
    """Lapas tīrā adrese: /par-mums, /en/par-mums, / un /en/."""
    pref = '' if valoda == 'lv' else '/' + valoda
    return pref + '/' if fails == 'index.html' else '%s/%s' % (pref, fails[:-5])


def izkartot(saturs, fails, ir_otra_valoda):
    m = re.match(r'<!--meta\n(.*?)\n-->\n', saturs, re.S)
    meta = dict(l.split(': ', 1) for l in m.group(1).split('\n')) if m else {}
    saturs = saturs[m.end():] if m else saturs
    for _ in range(3):
        saturs = re.sub(r'\{\{part:(\w+)\}\}', lambda x: part(x.group(1)), saturs)
        saturs = re.sub(r'\{\{gen:(\w+)\}\}', lambda x: GEN[x.group(1)](), saturs)
    akt = meta.get('nav', '')
    nav = '\n'.join('      <a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if k == akt else '', t) for h, t, k in T['nav'])
    menu = '\n'.join('          <a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if k == akt else '', t) for h, t, k in T['nav'])
    robots = '\n<meta name="robots" content="noindex">' if meta.get('robots') else ''
    otra = T['valoda_kods']
    # Ja otrā valodā šīs lapas nav, pārslēdzējs ved uz tās sākumu.
    otra_adrese = adrese(otra, fails if ir_otra_valoda else 'index.html')
    alternate = ''
    if ir_otra_valoda:
        alternate = '\n' + '\n'.join('<link rel="alternate" hreflang="%s" href="https://clickless.lv%s">' % (v, adrese(v, fails)) for v in ('lv', 'en'))
        alternate += '\n<link rel="alternate" hreflang="x-default" href="https://clickless.lv%s">' % adrese('lv', fails)
    atsauksme = '\n      <a href="atsauksme.html">%s</a>' % T['atsauksme'] if T['atsauksme'] else ''
    valodas_saite = '<a class="lang-switch" href="%s" hreflang="%s" lang="%s" title="%s">%s</a>' % (otra_adrese, otra, otra, T['valoda'], T['valoda_isi'])
    return '''<!doctype html>
<html lang="%(lang)s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(title)s</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="%(desc)s">%(robots)s%(alternate)s
<meta name="facebook-domain-verification" content="85fq8s0f2z1rcaz5doer52un35b076">
%(sik_head)s
%(tema_head)s
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&family=Commissioner:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap">
<link rel="stylesheet" href="/style.css?v=%(css_v)s">
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <a class="logo" href="index.html" aria-label="%(logo_aria)s">
      %(logo)s
    </a>
    <nav class="nav" aria-label="%(nav_aria)s">
%(nav)s
      %(valodas_saite)s
      <button type="button" id="themeBtn" title="%(tema)s" aria-label="%(tema)s"></button>
      <a class="btn btn-primary btn-sm nav-cta" href="kontakti.html"%(cta_cur)s>%(sazinaties)s</a>
      <div class="menu" id="menuDropdown">
        <button type="button" id="menuBtn" title="%(izvelne)s" aria-label="%(izvelne)s" aria-haspopup="true" aria-expanded="false" aria-controls="menuList">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg>
        </button>
        <div class="menu-list" id="menuList" hidden>
          <a href="index.html">%(sakums)s</a>
%(menu)s
          <a class="btn btn-primary" href="kontakti.html">%(sazinaties)s</a>
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
      <p>%(kajene_apraksts)s</p>
      <p>%(kajene_firma)s</p>
    </div>
    <nav aria-label="%(lapas)s">
      <span>%(lapas)s</span>
%(kajene_nav)s
      <a href="kontakti.html">%(kontakti)s</a>
    </nav>
    <nav aria-label="%(informacija)s">
      <span>%(informacija)s</span>
      <a href="privatuma-politika.html">%(privatums)s</a>
      <a href="noteikumi.html">%(noteikumi)s</a>%(atsauksme)s
      <a href="#sikdatnes">%(sik_kajene)s</a>
      <span class="select">info@clickless.lv</span>
    </nav>
  </div>
</footer>

%(sikdatnes)s
%(js)s
</body>
</html>
''' % {'lang': VAL, 'title': e(meta.get('title', 'CLICKLESS')), 'desc': e(meta.get('description', '')), 'robots': robots,
       'alternate': alternate,
       'css_v': hashlib.md5(open(os.path.join(SAKNE, 'style.css'), 'rb').read()).hexdigest()[:8],
       'tema_head': part('head_theme').strip(), 'logo': part('logo.svg'), 'nav': nav, 'menu': menu,
       'cta_cur': ' aria-current="page"' if akt == 'kontakti' else '',
       'valodas_saite': valodas_saite, 'sik_head': SIK_HEAD, 'sikdatnes': sikdatnes_html(), 'sik_kajene': T['sik_kajene'],
       'kajene_nav': '\n'.join('      <a href="%s">%s</a>' % (h, t) for h, t, k in T['nav']),
       'atsauksme': atsauksme,
       'saturs': saturs.strip('\n'), 'js': part('js_tema') + '\n' + part('js_izvelne'), **{k: T[k] for k in (
           'logo_aria', 'nav_aria', 'tema', 'izvelne', 'sakums', 'sazinaties', 'kajene_apraksts', 'kajene_firma',
           'lapas', 'informacija', 'kontakti', 'privatums', 'noteikumi')}}


def lidu_karte():
    o = ['# CLICKLESS līdu karte', '',
         'Ģenerēts no `clickless-web/dati/piedavajums.json` ar `python clickless-web/build.py`. Nelabot ar roku.', '',
         'Katrai nozarei: kā atrast uzņēmumus (NACE, atslēgvārdi), ko piedāvāt un pirmais teikums uzrunai.', '']
    sol = {r['id']: r for r in D_LV['risinajumi']}
    pakas = {p['id']: p for p in D_LV['pakas']}
    for n in D_LV['nozares']:
        a = n['agentiem']
        o += ['## ' + n['nosaukums'], '',
              '- **NACE:** ' + ', '.join(a['nace']),
              '- **Meklēšanas vārdi:** ' + ', '.join(a['atslegvardi']),
              '- **Uzruna:** ' + a['uzruna'],
              '- **Problēmas:** ' + '; '.join(n['problemas']),
              '- **Piedāvāt:** ' + ', '.join('%s (%s)' % (sol[s]['nosaukums'], D_LV['statusi'][sol[s]['statuss']]['nosaukums']) for s in n['risinajumi']),
              '- **Sākuma paka:** ' + (', '.join(pakas[p]['nosaukums'] + ' (' + zemaka_cena(pakas[p], 'Mēnesī') + '/mēn.)' for p in n['pakas']) or '— individuāls piedāvājums'),
              '']
    io.open(os.path.join('..', 'lidu-karte.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(o))


def tiras_saites(html, valoda):
    # GitHub Pages atver /par-mums tāpat kā /par-mums.html, tāpēc saitēs .html nerādām
    pref = '' if valoda == 'lv' else '/' + valoda
    html = re.sub(r'href="index\.html(#[^"]*)?"', lambda m: 'href="%s/%s"' % (pref, m.group(1) or ''), html)
    return re.sub(r'href="([a-z0-9-]+)\.html(#[^"]*)?"', lambda m: 'href="%s/%s%s"' % (pref, m.group(1), m.group(2) or ''), html)


def lapu_saraksts(valoda):
    mape = 'src/pages' if valoda == 'lv' else 'src/%s/pages' % valoda
    lapas = {f: io.open(mape + '/' + f, encoding='utf-8').read() for f in os.listdir(mape) if f.endswith('.html')}
    lapas['risinajumi.html'] = lapa_risinajumi()
    lapas['nozares.html'] = lapa_nozares()
    return lapas


def main():
    visas = {}
    for v in ('lv', 'en'):
        iestatit_valodu(v)
        visas[v] = lapu_saraksts(v)
    for v in ('lv', 'en'):
        iestatit_valodu(v)
        otra = 'en' if v == 'lv' else 'lv'
        izvade = '.' if v == 'lv' else v
        os.makedirs(izvade, exist_ok=True)
        for f, s in visas[v].items():
            if not s.startswith('<!--meta') and f in T['meta']:
                s = '<!--meta\n%s\n-->\n' % T['meta'][f] + s
            io.open(os.path.join(izvade, f), 'w', encoding='utf-8', newline='\n').write(
                tiras_saites(izkartot(s, f, f in visas[otra]), v))
        print('Uzbūvētas lapas (%s):' % v, ', '.join(sorted(visas[v])))
    lidu_karte()


if __name__ == '__main__':
    main()
