#!/usr/bin/env python3  
"""  
Map the e/ch axis (PC2) across the entire Voynich manuscript.  
  
Questions addressed:  
1. Spatial structure: how does PC2 vary across folio order?  
2. Section correlation: does PC2 track illustration type?  
3. Currier language: does PC2 separate Currier A/B?  
4. Within-folio variation: can we detect PC2 shifts at line level?  
5. Extreme folios: which folios define the PC2 poles?  
6. Word-position conditioning: is e/ch driven by word structure?  
"""  
  
import sys  
import re  
import math  
import statistics  
import random  
from collections import defaultdict, Counter  
  
  
# ══════════════════════════════════════════════════════════════════  
# SECTION / CURRIER ASSIGNMENTS  
# ══════════════════════════════════════════════════════════════════  
  
def build_folio_section_map():  
    """Authoritative illustration-type assignments per folio page.  
    Source: Beinecke / Zandbergen consensus catalogue."""  
    raw = {  
        "f1r": "text", "f1v": "herbal",  
        "f2r": "herbal", "f2v": "herbal",  
        "f3r": "herbal", "f3v": "herbal",  
        "f4r": "herbal", "f4v": "herbal",  
        "f5r": "herbal", "f5v": "herbal",  
        "f6r": "herbal", "f6v": "herbal",  
        "f7r": "herbal", "f7v": "herbal",  
        "f8r": "herbal", "f8v": "herbal",  
        "f9r": "herbal", "f9v": "herbal",  
        "f10r": "herbal", "f10v": "herbal",  
        "f11r": "herbal", "f11v": "herbal",  
        "f13r": "herbal", "f13v": "herbal",  
        "f14r": "herbal", "f14v": "herbal",  
        "f15r": "herbal", "f15v": "herbal",  
        "f16r": "herbal", "f16v": "herbal",  
        "f17r": "herbal", "f17v": "herbal",  
        "f18r": "herbal", "f18v": "herbal",  
        "f19r": "herbal", "f19v": "herbal",  
        "f20r": "herbal", "f20v": "herbal",  
        "f21r": "herbal", "f21v": "herbal",  
        "f22r": "herbal", "f22v": "herbal",  
        "f23r": "herbal", "f23v": "herbal",  
        "f24r": "herbal", "f24v": "herbal",  
        "f25r": "herbal", "f25v": "herbal",  
        "f26r": "herbal", "f26v": "herbal",  
        "f27r": "herbal", "f27v": "herbal",  
        "f28r": "herbal", "f28v": "herbal",  
        "f29r": "herbal", "f29v": "herbal",  
        "f30r": "herbal", "f30v": "herbal",  
        "f31r": "herbal", "f31v": "herbal",  
        "f32r": "herbal", "f32v": "herbal",  
        "f33r": "herbal", "f33v": "herbal",  
        "f34r": "herbal", "f34v": "herbal",  
        "f35r": "herbal", "f35v": "herbal",  
        "f36r": "herbal", "f36v": "herbal",  
        "f37r": "herbal", "f37v": "herbal",  
        "f38r": "herbal", "f38v": "herbal",  
        "f39r": "herbal", "f39v": "herbal",  
        "f40r": "herbal", "f40v": "herbal",  
        "f41r": "herbal", "f41v": "herbal",  
        "f42r": "herbal", "f42v": "herbal",  
        "f43r": "herbal", "f43v": "herbal",  
        "f44r": "herbal", "f44v": "herbal",  
        "f45r": "herbal", "f45v": "herbal",  
        "f46r": "herbal", "f46v": "herbal",  
        "f47r": "herbal", "f47v": "herbal",  
        "f48r": "herbal", "f48v": "herbal",  
        "f49r": "herbal", "f49v": "herbal",  
        "f50r": "herbal", "f50v": "herbal",  
        "f51r": "herbal", "f51v": "herbal",  
        "f52r": "herbal", "f52v": "herbal",  
        "f53r": "herbal", "f53v": "herbal",  
        "f54r": "herbal", "f54v": "herbal",  
        "f55r": "herbal", "f55v": "herbal",  
        "f56r": "herbal", "f56v": "herbal",  
        "f57r": "herbal",  
        "f57v": "cosmo",  
        "f58r": "text", "f58v": "text",  
        "f65r": "herbal", "f65v": "herbal",  
        "f66r": "text", "f66v": "herbal",  
        "f67r": "astro",  # f67r1=Astronomical, f67r2=Astronomical  
        "f67v": "astro",  # f67v2=Cosmological, f67v1=Astronomical (mixed)  
        "f68r": "astro",  # f68r1-r3=Astronomical  
        "f68v": "astro",  # f68v3=Cosmological, f68v2-v1=Astronomical (mixed)  
        "f69r": "cosmo", "f69v": "cosmo",  
        "f70r": "cosmo",  # f70r1-r2=Cosmological  
        "f70v": "zodiac",  # f70v2-v1=Zodiac  
        "f71r": "zodiac", "f71v": "zodiac",  
        "f72r": "zodiac",  # f72r1-r3=Zodiac  
        "f72v": "zodiac",  # f72v3-v1=Zodiac  
        "f73r": "zodiac", "f73v": "zodiac",  
        "f75r": "bio", "f75v": "bio",  
        "f76r": "bio", "f76v": "bio",  
        "f77r": "bio", "f77v": "bio",  
        "f78r": "bio", "f78v": "bio",  
        "f79r": "bio", "f79v": "bio",  
        "f80r": "bio", "f80v": "bio",  
        "f81r": "bio", "f81v": "bio",  
        "f82r": "bio", "f82v": "bio",  
        "f83r": "bio", "f83v": "bio",  
        "f84r": "bio", "f84v": "bio",  
        "f85r": "cosmo",  # f85r1=Text, f85r2=Cosmological  
        "f86v": "cosmo",  # f86v4-v3=Cosmological  
        "f87r": "herbal", "f87v": "herbal",  
        "f88r": "pharma", "f88v": "pharma",  
        "f89r": "pharma", "f89v": "pharma",  
        "f90r": "herbal", "f90v": "herbal",  
        "f93r": "herbal", "f93v": "herbal",  
        "f94r": "herbal", "f94v": "herbal",  
        "f95r": "herbal", "f95v": "herbal",  
        "f96r": "herbal", "f96v": "herbal",  
        "f99r": "pharma", "f99v": "pharma",  
        "f100r": "pharma", "f100v": "pharma",  
        "f101r": "pharma", "f101v": "pharma",  
        "f102r": "pharma", "f102v": "pharma",  
        "f103r": "stars", "f103v": "stars",  
        "f104r": "stars", "f104v": "stars",  
        "f105r": "stars", "f105v": "stars",  
        "f106r": "stars", "f106v": "stars",  
        "f107r": "stars", "f107v": "stars",  
        "f108r": "stars", "f108v": "stars",  
        "f111r": "stars", "f111v": "stars",  
        "f112r": "stars", "f112v": "stars",  
        "f113r": "stars", "f113v": "stars",  
        "f114r": "stars", "f114v": "stars",  
        "f115r": "stars", "f115v": "stars",  
        "f116r": "stars",  
    }  
    return raw  
  
  
def get_section(fid):  
    """Look up illustration section from the authoritative folio map."""  
    section_map = build_folio_section_map()  
    return section_map.get(fid, 'unknown')  
  
  
def build_folio_language_map():  
    raw = {  
        "f1r": "A", "f1v": "A", "f2r": "A", "f2v": "A",  
        "f3r": "A", "f3v": "A", "f4r": "A", "f4v": "A",  
        "f5r": "A", "f5v": "A", "f6r": "A", "f6v": "A",  
        "f7r": "A", "f7v": "A", "f8r": "A", "f8v": "A",  
        "f9r": "A", "f9v": "A", "f10r": "A", "f10v": "A",  
        "f11r": "A", "f11v": "A",  
        "f13r": "A", "f13v": "A", "f14r": "A", "f14v": "A",  
        "f15r": "A", "f15v": "A", "f16r": "A", "f16v": "A",  
        "f17r": "A", "f17v": "A", "f18r": "A", "f18v": "A",  
        "f19r": "A", "f19v": "A", "f20r": "A", "f20v": "A",  
        "f21r": "A", "f21v": "A", "f22r": "A", "f22v": "A",  
        "f23r": "A", "f23v": "A", "f24r": "A", "f24v": "A",  
        "f25r": "A", "f25v": "A",  
        "f26r": "B", "f26v": "B",  
        "f27r": "A", "f27v": "A", "f28r": "A", "f28v": "A",  
        "f29r": "A", "f29v": "A", "f30r": "A", "f30v": "A",  
        "f31r": "B", "f31v": "B",  
        "f32r": "A", "f32v": "A",  
        "f33r": "B", "f33v": "B", "f34r": "B", "f34v": "B",  
        "f35r": "A", "f35v": "A", "f36r": "A", "f36v": "A",  
        "f37r": "A", "f37v": "A", "f38r": "A", "f38v": "A",  
        "f39r": "B", "f39v": "B", "f40r": "B", "f40v": "B",  
        "f41r": "B", "f41v": "B",  
        "f42r": "A", "f42v": "A",  
        "f43r": "B", "f43v": "B",  
        "f44r": "A", "f44v": "A", "f45r": "A", "f45v": "A",  
        "f46r": "B", "f46v": "B",  
        "f47r": "A", "f47v": "A",  
        "f48r": "B", "f48v": "B",  
        "f49r": "A", "f49v": "A",  
        "f50r": "B", "f50v": "B",  
        "f51r": "A", "f51v": "A", "f52r": "A", "f52v": "A",  
        "f53r": "A", "f53v": "A", "f54r": "A", "f54v": "A",  
        "f55r": "B", "f55v": "B",  
        "f56r": "A", "f56v": "A",  
        "f57r": "B",  
        "f58r": "A", "f58v": "A",  
        "f66r": "B", "f66v": "B",  
        "f75r": "B", "f75v": "B", "f76r": "B", "f76v": "B",  
        "f77r": "B", "f77v": "B", "f78r": "B", "f78v": "B",  
        "f79r": "B", "f79v": "B", "f80r": "B", "f80v": "B",  
        "f81r": "B", "f81v": "B", "f82r": "B", "f82v": "B",  
        "f83r": "B", "f83v": "B", "f84r": "B", "f84v": "B",  
        "f85r": "B",  
        "f86v": "B",  
        "f87r": "A", "f87v": "A", "f88r": "A", "f88v": "A",  
        "f89r": "A", "f89v": "A",  
        "f90r": "A", "f90v": "A",  
        "f93r": "A", "f93v": "A",  
        "f94r": "B", "f94v": "B",  
        "f95r": "B", "f95v": "B",  
        "f96r": "A", "f96v": "A",  
        "f99r": "A", "f99v": "A",  
        "f100r": "A", "f100v": "A",  
        "f101r": "A", "f101v": "A",  
        "f102r": "A", "f102v": "A",  
        "f103r": "B", "f103v": "B", "f104r": "B", "f104v": "B",  
        "f105r": "B", "f105v": "B", "f106r": "B", "f106v": "B",  
        "f107r": "B", "f107v": "B", "f108r": "B", "f108v": "B",  
        "f111r": "B", "f111v": "B", "f112r": "B", "f112v": "B",  
        "f113r": "B", "f113v": "B", "f114r": "B", "f114v": "B",  
        "f115r": "B", "f115v": "B", "f116r": "B", "f116v": "B",  
    }  
    return raw  
  
  
def get_currier_label(fid):  
    """Look up Currier A/B from the authoritative folio map."""  
    currier_map = build_folio_language_map()  
    return currier_map.get(fid, '?')  
  
  
# ══════════════════════════════════════════════════════════════════  
# PARSING  
# ══════════════════════════════════════════════════════════════════  
  
def parse_ivtff_lines(filename):  
    """Parse IVTFF returning per-line data for within-folio analysis."""  
    folios = defaultdict(list)  # fid -> list of (line_id, [words])  
  
    with open(filename, 'r') as f:  
        for line in f:  
            line = line.rstrip('\n')  
            if line.startswith('#') or line.startswith(';') or not line.strip():  
                continue  
  
            m = re.match(r'<(f\d+[rv]\d?)\.(\d+\w*)', line)  
            if not m:  
                continue  
  
            fid_raw = m.group(1)  
            line_id = m.group(2)  
            fid = re.match(r'(f\d+[rv])', fid_raw).group(1)  
  
            text = re.sub(r'<[^>]*>', '', line)  
            text = re.sub(r'\{[^}]*\}', '', text)  
            text = re.sub(r'@\d+;?', '', text)  
            text = re.sub(r'[!%*]', '', text)  
  
            words = [w.strip() for w in text.split('.') if w.strip()]  
            clean = []  
            for w in words:  
                w = re.sub(r'[^a-z]', '', w)  
                if w:  
                    clean.append(w)  
  
            if clean:  
                folios[fid].append((line_id, clean))  
  
    return folios  
  
  
def count_features(words):  
    """Count character features from word list."""  
    text = ''.join(words)  
    counts = {}  
  
    # Careful digraph counting  
    ch_count = 0  
    sh_count = 0  
    e_count = 0  
    i = 0  
    while i < len(text):  
        if i < len(text) - 1:  
            if text[i] == 'c' and text[i + 1] == 'h':  
                ch_count += 1  
                i += 2  
                continue  
            elif text[i] == 's' and text[i + 1] == 'h':  
                sh_count += 1  
                i += 2  
                continue  
        if text[i] == 'e':  
            e_count += 1  
        i += 1  
  
    counts['e'] = e_count  
    counts['ch'] = ch_count  
    counts['sh'] = sh_count  
  
    # ee counting  
    ee_count = 0  
    single_e = 0  
    i = 0  
    while i < len(text):  
        if text[i] == 'e':  
            run = 0  
            while i < len(text) and text[i] == 'e':  
                run += 1  
                i += 1  
            ee_count += run // 2  
            single_e += run % 2  
        else:  
            i += 1  
    counts['ee'] = ee_count  
    counts['single_e'] = single_e  
  
    for c in 'adklostyrpfqn':  
        counts[c] = text.count(c)  
  
    # Digraphs  
    for d1, d2 in [('o', 'r'), ('a', 'r'), ('o', 'l'), ('a', 'l')]:  
        key = d1 + d2  
        counts[key] = sum(1 for i in range(len(text) - 1)  
                          if text[i] == d1 and text[i + 1] == d2)  
  
    counts['n_chars'] = len(text)  
    counts['n_words'] = len(words)  
  
    # Word-position features  
    counts['e_initial'] = sum(1 for w in words if w and w[0] == 'e')  
    counts['ch_initial'] = sum(1 for w in words if len(w) >= 2  
                               and w[:2] == 'ch')  
    counts['e_final'] = sum(1 for w in words if w and w[-1] == 'e')  
    counts['y_final'] = sum(1 for w in words if w and w[-1] == 'y')  
  
    # Word-internal e vs ch  
    counts['e_medial'] = 0  
    counts['ch_medial'] = 0  
    for w in words:  
        if len(w) < 3:  
            continue  
        interior = w[1:-1]  
        j = 0  
        while j < len(interior):  
            if j < len(interior) - 1 and interior[j] == 'c' and interior[j + 1] == 'h':  
                counts['ch_medial'] += 1  
                j += 2  
            elif interior[j] == 'e':  
                counts['e_medial'] += 1  
                j += 1  
            else:  
                j += 1  
  
    return counts  
  
  
def safe_ratio(a, b, min_total=20):  
    t = a + b  
    if t < min_total:  
        return None  
    return a / t  
  
def pearson(x, y):  
    if len(x) < 3:  
        return float('nan')  
    mx, my = statistics.mean(x), statistics.mean(y)  
    sx, sy = statistics.stdev(x), statistics.stdev(y)  
    if sx == 0 or sy == 0:  
        return 0  
    n = len(x)  
    return sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / ((n - 1) * sx * sy)  
  
def cohens_d(a, b):  
    if len(a) < 2 or len(b) < 2:  
        return float('nan')  
    pooled = math.sqrt(  
        (statistics.variance(a) * (len(a) - 1) +  
         statistics.variance(b) * (len(b) - 1)) /  
        (len(a) + len(b) - 2))  
    if pooled == 0:  
        return 0  
    return (statistics.mean(a) - statistics.mean(b)) / pooled  
  
  
# ══════════════════════════════════════════════════════════════════  
# MAIN  
# ══════════════════════════════════════════════════════════════════  
  
def main():  
    if len(sys.argv) < 2:  
        print("Usage: python3 pc2_map.py <ivtff_file>")  
        sys.exit(1)  
  
    folio_lines = parse_ivtff_lines(sys.argv[1])  
  
    print("=" * 78)  
    print("PC2 (E/CH AXIS) -- FULL MANUSCRIPT MAP")  
    print("=" * 78)  
  
    # ──────────────────────────────────────────────────────────────  
    # Compute folio-level features  
    # ──────────────────────────────────────────────────────────────  
  
    folio_data = {}  
    for fid in sorted(folio_lines.keys()):  
        all_words = []  
        for _, words in folio_lines[fid]:  
            all_words.extend(words)  
        if len(all_words) < 15:  
            continue  
        counts = count_features(all_words)  
        folio_data[fid] = {  
            'counts': counts,  
            'words': all_words,  
            'section': get_section(fid),  
            'currier': get_currier_label(fid),  
        }  
  
    # Compute key ratios  
    ratio_pairs = [  
        ('ech', 'e', 'ch'),  
        ('eee', 'single_e', 'ee'),  
        ('dl', 'd', 'l'),  
        ('oa', 'o', 'a'),  
        ('kt', 'k', 't'),  
        ('sr', 's', 'r'),  
        ('orar', 'or', 'ar'),  
        ('olal', 'ol', 'al'),  
        ('shch', 'sh', 'ch'),  
    ]  
  
    for fid in folio_data:  
        c = folio_data[fid]['counts']  
        ratios = {}  
        for name, ca, cb in ratio_pairs:  
            ratios[name] = safe_ratio(c.get(ca, 0), c.get(cb, 0))  
        # Word-position ratios  
        ratios['e_init_ch_init'] = safe_ratio(  
            c.get('e_initial', 0), c.get('ch_initial', 0), min_total=10)  
        ratios['e_med_ch_med'] = safe_ratio(  
            c.get('e_medial', 0), c.get('ch_medial', 0), min_total=10)  
        folio_data[fid]['ratios'] = ratios  
  
    def folio_sort_key(fid):  
        m = re.match(r'f(\d+)([rv])', fid)  
        return (int(m.group(1)), 0 if m.group(2) == 'r' else 1)  
  
    ordered_folios = sorted(folio_data.keys(), key=folio_sort_key)  
    print(f"\n  Folios: {len(ordered_folios)}")  
  
    # ══════════════════════════════════════════════════════════════  
    # Q1: SPATIAL MAP  
    # ══════════════════════════════════════════════════════════════  
    print(f"\n{'=' * 78}")  
    print("Q1: SPATIAL MAP OF E/CH RATIO ACROSS MANUSCRIPT")  
    print(f"{'=' * 78}")  
  
    print(f"\n  {'Folio':<8} {'Sect':>7} {'A/B':>3} "  
          f"{'e/ch':>6} {'d/l':>6} {'s/r':>6} {'sh/ch':>6} "  
          f"{'e_i/ch_i':>8} {'e_m/ch_m':>8} {'Words':>5}")  
    print(f"  {'---'*8} {'---'*7} {'---'*3} "  
          f"{'---'*6} {'---'*6} {'---'*6} {'---'*6} "  
          f"{'---'*8} {'---'*8} {'---'*5}")  
  
    prev_section = None  
    for fid in ordered_folios:  
        d = folio_data[fid]  
        r = d['ratios']  
        section = d['section']  
  
        if section != prev_section:  
            print(f"  {'---' * 24}")  
            prev_section = section  
  
        def fmt(v):  
            return f"{v:.3f}" if v is not None else "  n/a"  
  
        print(f"  {fid:<8} {section:>7} {d['currier']:>3} "  
              f"{fmt(r['ech']):>6} {fmt(r['dl']):>6} {fmt(r['sr']):>6} "  
              f"{fmt(r['shch']):>6} {fmt(r.get('e_init_ch_init')):>8} "  
              f"{fmt(r.get('e_med_ch_med')):>8} {d['counts']['n_words']:>5}")  
  
    # ══════════════════════════════════════════════════════════════  
    # Q2: SECTION STATISTICS  
    # ══════════════════════════════════════════════════════════════  
    print(f"\n{'=' * 78}")  
    print("Q2: E/CH RATIO BY MANUSCRIPT SECTION")  
    print(f"{'=' * 78}")  
  
    sections_list = ['herbal', 'text', 'astro', 'cosmo', 'zodiac',  
                     'bio', 'pharma', 'stars']  
  
    print(f"\n  {'Section':<10} {'N':>4} {'e/ch mean':>9} {'e/ch sd':>8} "  
          f"{'d/l mean':>9} {'d/l sd':>8} {'s/r mean':>9} {'sh/ch mean':>10}")  
  
    section_ech = defaultdict(list)  
    for fid in ordered_folios:  
        d = folio_data[fid]  
        ech = d['ratios'].get('ech')  
        if ech is not None:  
            section_ech[d['section']].append(ech)  
  
    for sec in sections_list:  
        fids = [f for f in ordered_folios if folio_data[f]['section'] == sec]  
        if not fids:  
            continue  
  
        def sec_stats(ratio_name):  
            vals = [folio_data[f]['ratios'][ratio_name] for f in fids  
                    if folio_data[f]['ratios'].get(ratio_name) is not None]  
            if len(vals) < 2:  
                return float('nan'), float('nan')  
            return statistics.mean(vals), statistics.stdev(vals)  
  
        ech_m, ech_s = sec_stats('ech')  
        dl_m, dl_s = sec_stats('dl')  
        sr_m, _ = sec_stats('sr')  
        shch_m, _ = sec_stats('shch')  
  
        print(f"  {sec:<10} {len(fids):>4} {ech_m:>9.4f} {ech_s:>8.4f} "  
              f"{dl_m:>9.4f} {dl_s:>8.4f} {sr_m:>9.4f} {shch_m:>10.4f}")  
  
    # Pairwise section comparisons for e/ch  
    print(f"\n  Pairwise e/ch differences (Cohen's d):")  
    print(f"  {'':>10}", end='')  
    for s2 in sections_list:  
        print(f" {s2:>8}", end='')  
    print()  
    for s1 in sections_list:  
        print(f"  {s1:>10}", end='')  
        for s2 in sections_list:  
            v1 = section_ech.get(s1, [])  
            v2 = section_ech.get(s2, [])  
            if len(v1) >= 2 and len(v2) >= 2:  
                d = cohens_d(v1, v2)  
                print(f" {d:>+8.2f}", end='')  
            else:  
                print(f" {'n/a':>8}", end='')  
        print()  
  
    # ══════════════════════════════════════════════════════════════  
    # Q3: CURRIER A/B SEPARATION  
    # ══════════════════════════════════════════════════════════════  
    print(f"\n{'=' * 78}")  
    print("Q3: E/CH RATIO BY CURRIER LANGUAGE (A vs B)")  
    print(f"{'=' * 78}")  
  
    for cur_label in ['A', 'B']:  
        fids = [f for f in ordered_folios if folio_data[f]['currier'] == cur_label]  
        if not fids:  
            continue  
        for rname, rlabel in [('ech', 'e/ch'), ('dl', 'd/l'), ('sr', 's/r'),  
                               ('shch', 'sh/ch')]:  
            vals = [folio_data[f]['ratios'][rname] for f in fids  
                    if folio_data[f]['ratios'].get(rname) is not None]  
            if vals:  
                print(f"  Currier {cur_label}: {rlabel} = {statistics.mean(vals):.4f} "  
                      f"+/- {statistics.stdev(vals):.4f} (n={len(vals)})")  
  
    a_ech = [folio_data[f]['ratios']['ech'] for f in ordered_folios  
              if folio_data[f]['currier'] == 'A'  
              and folio_data[f]['ratios'].get('ech') is not None]  
    b_ech = [folio_data[f]['ratios']['ech'] for f in ordered_folios  
              if folio_data[f]['currier'] == 'B'  
              and folio_data[f]['ratios'].get('ech') is not None]  
  
    if a_ech and b_ech:  
        print(f"\n  Currier A vs B separation:")  
        print(f"    e/ch: Cohen's d = {cohens_d(a_ech, b_ech):+.3f}")  
  
        a_dl = [folio_data[f]['ratios']['dl'] for f in ordered_folios  
                 if folio_data[f]['currier'] == 'A'  
                 and folio_data[f]['ratios'].get('dl') is not None]  
        b_dl = [folio_data[f]['ratios']['dl'] for f in ordered_folios  
                 if folio_data[f]['currier'] == 'B'  
                 and folio_data[f]['ratios'].get('dl') is not None]  
        if a_dl and b_dl:  
            print(f"    d/l:  Cohen's d = {cohens_d(a_dl, b_dl):+.3f}")  
  
    # Currier A vs B within each section  
    print(f"\n  Currier effect within sections:")  
    for sec in sections_list:  
        a_vals = [folio_data[f]['ratios']['ech'] for f in ordered_folios  
                  if folio_data[f]['section'] == sec  
                  and folio_data[f]['currier'] == 'A'  
                  and folio_data[f]['ratios'].get('ech') is not None]  
        b_vals = [folio_data[f]['ratios']['ech'] for f in ordered_folios  
                  if folio_data[f]['section'] == sec  
                  and folio_data[f]['currier'] == 'B'  
                  and folio_data[f]['ratios'].get('ech') is not None]  
        if len(a_vals) >= 2 and len(b_vals) >= 2:  
            print(f"    Within {sec}: A e/ch = {statistics.mean(a_vals):.4f} "  
                  f"(n={len(a_vals)}), B = {statistics.mean(b_vals):.4f} (n={len(b_vals)}), "  
                  f"d = {cohens_d(a_vals, b_vals):+.3f}")  
        else:  
            print(f"    Within {sec}: insufficient data "  
                  f"(A={len(a_vals)}, B={len(b_vals)})")  
  
    # ══════════════════════════════════════════════════════════════  
    # Q4: WITHIN-FOLIO VARIATION  
    # ══════════════════════════════════════════════════════════════  
    print(f"\n{'=' * 78}")  
    print("Q4: WITHIN-FOLIO E/CH VARIATION (HALF-PAGE SPLITS)")  
    print(f"{'=' * 78}")  
  
    within_diffs = []  
    between_diffs = []  
  
    print(f"\n  {'Folio':<8} {'1st half':>8} {'2nd half':>8} {'D':>8} "  
          f"{'n1':>4} {'n2':>4}")  
  
    for fid in ordered_folios:  
        lines = folio_lines[fid]  
        if len(lines) < 6:  
            continue  
  
        mid = len(lines) // 2  
        first_words = []  
        second_words = []  
        for _, words in lines[:mid]:  
            first_words.extend(words)  
        for _, words in lines[mid:]:  
            second_words.extend(words)  
  
        c1 = count_features(first_words)  
        c2 = count_features(second_words)  
        r1 = safe_ratio(c1['e'], c1['ch'], min_total=15)  
        r2 = safe_ratio(c2['e'], c2['ch'], min_total=15)  
  
        if r1 is not None and r2 is not None:  
            diff = abs(r2 - r1)  
            within_diffs.append(diff)  
            print(f"  {fid:<8} {r1:>8.4f} {r2:>8.4f} {r2 - r1:>+8.4f} "  
                  f"{c1['e'] + c1['ch']:>4} {c2['e'] + c2['ch']:>4}")  
  
    # Between-folio differences for comparison  
    ech_ordered = [(fid, folio_data[fid]['ratios']['ech'])  
                   for fid in ordered_folios  
                   if folio_data[fid]['ratios'].get('ech') is not None]  
    for i in range(len(ech_ordered) - 1):  
        between_diffs.append(abs(ech_ordered[i + 1][1] - ech_ordered[i][1]))  
  
    if within_diffs and between_diffs:  
        print(f"\n  Mean within-folio |D(e/ch)|:  {statistics.mean(within_diffs):.4f} "  
              f"(n={len(within_diffs)})")  
        print(f"  Mean between-folio |D(e/ch)|: {statistics.mean(between_diffs):.4f} "  
              f"(n={len(between_diffs)})")  
        ratio = statistics.mean(within_diffs) / statistics.mean(between_diffs)  
        print(f"  Ratio (within/between): {ratio:.3f}")  
        print(f"  (If <1, e/ch is more stable within pages than between pages)")  
  
    # ══════════════════════════════════════════════════════════════  
    # Q5: WORD-POSITION CONDITIONING  
    # ══════════════════════════════════════════════════════════════  
    print(f"\n{'=' * 78}")  
    print("Q5: IS E/CH CONDITIONED BY WORD POSITION?")  
    print(f"{'=' * 78}")  
  
    # Global word-position analysis  
    all_words_global = []  
    for fid in ordered_folios:  
        all_words_global.extend(folio_data[fid]['words'])  
  
    # Classify e and ch by position in word  
    e_positions = Counter()  
    ch_positions = Counter()  
  
    for w in all_words_global:  
        if len(w) < 1:  
            continue  
        i = 0  
        while i < len(w):  
            if i < len(w) - 1 and w[i] == 'c' and w[i + 1] == 'h':  
                if i == 0:  
                    ch_positions['initial'] += 1  
                elif i >= len(w) - 2:  
                    ch_positions['final'] += 1  
                else:  
                    ch_positions['medial'] += 1  
                i += 2  
            elif w[i] == 'e':  
                if i == 0:  
                    e_positions['initial'] += 1  
                elif i == len(w) - 1:  
                    e_positions['final'] += 1  
                else:  
                    e_positions['medial'] += 1  
                i += 1  
            else:  
                i += 1  
  
    print(f"\n  Global e/ch by word position:")  
    print(f"  {'Position':<10} {'e count':>8} {'ch count':>9} {'e/(e+ch)':>9}")  
    for pos in ['initial', 'medial', 'final']:  
        e = e_positions[pos]  
        ch = ch_positions[pos]  
        r = e / (e + ch) if (e + ch) > 0 else float('nan')  
        print(f"  {pos:<10} {e:>8} {ch:>9} {r:>9.4f}")  
  
    # Per-section word-position analysis  
    print(f"\n  e/(e+ch) by position and section:")  
    print(f"  {'Section':<10} {'initial':>9} {'medial':>9} {'final':>9} {'all':>9}")  
  
    for sec in sections_list:  
        sec_words = []  
        for fid in ordered_folios:  
            if folio_data[fid]['section'] == sec:  
                sec_words.extend(folio_data[fid]['words'])  
  
        e_pos = Counter()  
        ch_pos = Counter()  
        for w in sec_words:  
            i = 0  
            while i < len(w):  
                if i < len(w) - 1 and w[i] == 'c' and w[i + 1] == 'h':  
                    if i == 0:  
                        ch_pos['initial'] += 1  
                    elif i >= len(w) - 2:  
                        ch_pos['final'] += 1  
                    else:  
                        ch_pos['medial'] += 1  
                    i += 2  
                elif w[i] == 'e':  
                    if i == 0:  
                        e_pos['initial'] += 1  
                    elif i == len(w) - 1:  
                        e_pos['final'] += 1  
                    else:  
                        e_pos['medial'] += 1  
                    i += 1  
                else:  
                    i += 1  
  
        vals = []  
        for pos in ['initial', 'medial', 'final']:  
            e = e_pos[pos]  
            ch = ch_pos[pos]  
            r = e / (e + ch) if (e + ch) > 0 else float('nan')  
            vals.append(f"{r:.4f}")  
  
        all_e = sum(e_pos.values())  
        all_ch = sum(ch_pos.values())  
        all_r = all_e / (all_e + all_ch) if (all_e + all_ch) > 0 else float('nan')  
        print(f"  {sec:<10} {vals[0]:>9} {vals[1]:>9} {vals[2]:>9} {all_r:>9.4f}")  
  
    # ══════════════════════════════════════════════════════════════  
    # Q6: EXTREME FOLIOS  
    # ══════════════════════════════════════════════════════════════  
    print(f"\n{'=' * 78}")  
    print("Q6: PC2-EXTREME FOLIOS")  
    print(f"{'=' * 78}")  
  
    ech_folios = [(fid, folio_data[fid]['ratios']['ech'])  
                  for fid in ordered_folios  
                  if folio_data[fid]['ratios'].get('ech') is not None]  
    ech_folios.sort(key=lambda x: x[1])  
  
    print(f"\n  10 LOWEST e/ch (most ch-dominant):")  
    print(f"  {'Folio':<8} {'e/ch':>6} {'Section':>8} {'A/B':>3} {'Words':>5}")  
    for fid, ech in ech_folios[:10]:  
        d = folio_data[fid]  
        print(f"  {fid:<8} {ech:>6.3f} {d['section']:>8} {d['currier']:>3} "  
              f"{d['counts']['n_words']:>5}")  
  
    print(f"\n  10 HIGHEST e/ch (most e-dominant):")  
    for fid, ech in ech_folios[-10:]:  
        d = folio_data[fid]  
        print(f"  {fid:<8} {ech:>6.3f} {d['section']:>8} {d['currier']:>3} "  
              f"{d['counts']['n_words']:>5}")  
  
    # ══════════════════════════════════════════════════════════════  
    # Q7: AUTOCORRELATION  
    # ══════════════════════════════════════════════════════════════  
    print(f"\n{'=' * 78}")  
    print("Q7: SPATIAL AUTOCORRELATION")  
    print(f"{'=' * 78}")  
  
    ech_series = [folio_data[fid]['ratios']['ech'] for fid in ordered_folios  
                  if folio_data[fid]['ratios'].get('ech') is not None]  
  
    if len(ech_series) > 10:  
        for lag in [1, 2, 3, 5, 10]:  
            if lag >= len(ech_series):  
                break  
            x = ech_series[:-lag]  
            y = ech_series[lag:]  
            r = pearson(x, y)  
            print(f"  Lag-{lag} autocorrelation: r = {r:+.3f}")  
  
        # Compare with d/l  
        dl_series = [folio_data[fid]['ratios']['dl'] for fid in ordered_folios  
                     if folio_data[fid]['ratios'].get('dl') is not None]  
        if len(dl_series) > 10:  
            print(f"\n  For comparison, d/l autocorrelation:")  
            for lag in [1, 2, 3, 5, 10]:  
                if lag >= len(dl_series):  
                    break  
                x = dl_series[:-lag]  
                y = dl_series[lag:]  
                r = pearson(x, y)  
                print(f"  Lag-{lag} autocorrelation: r = {r:+.3f}")  
  
    # ══════════════════════════════════════════════════════════════  
    # Q8: CONSECUTIVE FOLIO JUMPS  
    # ══════════════════════════════════════════════════════════════  
    print(f"\n{'=' * 78}")  
    print("Q8: LARGE E/CH JUMPS -- WHAT BOUNDARIES DO THEY OCCUR AT?")  
    print(f"{'=' * 78}")  
  
    ech_ms = [(fid, folio_data[fid]['ratios']['ech']) for fid in ordered_folios  
              if folio_data[fid]['ratios'].get('ech') is not None]  
  
    jumps = []  
    for i in range(len(ech_ms) - 1):  
        f1, e1 = ech_ms[i]  
        f2, e2 = ech_ms[i + 1]  
        jump = abs(e2 - e1)  
        d1 = folio_data[f1]  
        d2 = folio_data[f2]  
  
        same_section = d1['section'] == d2['section']  
        same_currier = d1['currier'] == d2['currier']  
  
        jumps.append({  
            'f1': f1, 'f2': f2, 'jump': jump,  
            'same_section': same_section,  
            'same_currier': same_currier,  
            'section_change': f"{d1['section']}->{d2['section']}",  
        })  
  
    jumps.sort(key=lambda x: -x['jump'])  
  
    print(f"\n  15 largest e/ch jumps:")  
    print(f"  {'From':<8} {'To':<8} {'|D|':>6} {'Same sect':>9} "  
          f"{'Same A/B':>8} {'Transition':<20}")  
    for j in jumps[:15]:  
        print(f"  {j['f1']:<8} {j['f2']:<8} {j['jump']:>6.3f} "  
              f"{'yes' if j['same_section'] else 'NO':>9} "  
              f"{'yes' if j['same_currier'] else 'NO':>8} "  
              f"{j['section_change']:<20}")  
  
    # Mean jump by boundary type  
    print(f"\n  Mean |D(e/ch)| by boundary type:")  
    for btype, label in [('same_section', 'Same section'),  
                          ('same_currier', 'Same Currier')]:  
        same = [j['jump'] for j in jumps if j[btype]]  
        diff = [j['jump'] for j in jumps if not j[btype]]  
        if same and diff:  
            print(f"    {label:<20} same={statistics.mean(same):.4f}(n={len(same)})  "  
                  f"diff={statistics.mean(diff):.4f}(n={len(diff)})  "  
                  f"ratio={statistics.mean(diff) / statistics.mean(same):.2f}")  
  
    # ══════════════════════════════════════════════════════════════  
    # SUMMARY  
    # ══════════════════════════════════════════════════════════════  
    print(f"\n{'=' * 78}")  
    print("SUMMARY")  
    print(f"{'=' * 78}")  
  
    all_ech = [folio_data[fid]['ratios']['ech'] for fid in ordered_folios  
               if folio_data[fid]['ratios'].get('ech') is not None]  
    print(f"\n  Global e/ch: mean={statistics.mean(all_ech):.4f}, "  
          f"sd={statistics.stdev(all_ech):.4f}, "  
          f"range=[{min(all_ech):.3f}, {max(all_ech):.3f}]")  
  
    print()  
  
if __name__ == '__main__':  
    main()  
