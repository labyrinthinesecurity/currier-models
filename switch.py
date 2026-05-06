#!/usr/bin/env python3  
"""  
"""  
  
import sys  
import re  
import math  
import random  
import statistics  
from collections import defaultdict, Counter  
  
  
def parse_ivtff(filename):  
    folios = defaultdict(list)  
    with open(filename, 'r') as f:  
        for line in f:  
            line = line.rstrip('\n')  
            if line.startswith('#') or line.startswith(';') or not line.strip():  
                continue  
            m = re.match(r'<(f\d+[rv]\d?)\.(\d+\w*)', line)  
            if not m:  
                continue  
            fid_raw = m.group(1)  
            fid = re.match(r'(f\d+[rv])', fid_raw).group(1)  
            text = re.sub(r'<->', '.', line)
            text = re.sub(r'<[^>]*>', '', text)  
            text = re.sub(r'\{[^}]*\}', '', text)  
            text = re.sub(r'@\d+;?', '', text)  
            text = re.sub(r'[!%*]', '', text)  
            words = [re.sub(r'[^a-z]', '', w.strip())  
                     for w in text.split('.') if w.strip()]  
            words = [w for w in words if w]  
            if words:  
                folios[fid].append(words)  
    return folios  
  
  
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
        "f67r": "astro",  
        "f67v": "astro",  
        "f68r": "astro",  
        "f68v": "astro",  
        "f69r": "cosmo", "f69v": "cosmo",  
        "f70r": "cosmo",  
        "f70v": "zodiac",  
        "f71r": "zodiac", "f71v": "zodiac",  
        "f72r": "zodiac",  
        "f72v": "zodiac",  
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
        "f85r": "cosmo",  
        "f86v": "cosmo",  
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
  
  
def folio_sort_key(fid):  
    m = re.match(r'f(\d+)([rv])', fid)  
    if not m:  
        return (999, 0)  
    return (int(m.group(1)), 0 if m.group(2) == 'r' else 1)  
  
  
def word_to_glyphs(word):  
    glyphs = []  
    i = 0  
    while i < len(word):  
        if i < len(word) - 1:  
            pair = word[i:i+2]  
            if pair in ('ch', 'sh'):  
                glyphs.append(pair)  
                i += 2  
                continue  
        glyphs.append(word[i])  
        i += 1  
    return glyphs  
  
  
def classify_word_cho(word):  
    """Returns 'cho', 'che', or None."""  
    glyphs = word_to_glyphs(word)  
    has_cho = False  
    has_che = False  
    for i in range(len(glyphs) - 1):  
        if glyphs[i] in ('ch', 'sh'):  
            if glyphs[i + 1] == 'o':  
                has_cho = True  
            elif glyphs[i + 1] == 'e':  
                has_che = True  
    if has_cho and not has_che:  
        return 'cho'  
    elif has_che and not has_cho:  
        return 'che'  
    return None  
  
  
def em_two_state(counts_list, max_iter=200, tol=1e-8):  
    """EM for two-state binomial mixture."""  
    p_a = 0.7  
    p_b = 0.2  
    pi_a = 0.5  
    n = len(counts_list)  
  
    for iteration in range(max_iter):  
        responsibilities = []  
        for k, c_total in counts_list:  
            if c_total == 0:  
                responsibilities.append(0.5)  
                continue  
            log_pa = k * math.log(max(p_a, 1e-15)) +   (c_total - k) * math.log(max(1 - p_a, 1e-15))  
            log_pb = k * math.log(max(p_b, 1e-15)) +   (c_total - k) * math.log(max(1 - p_b, 1e-15))  
            log_wa = math.log(pi_a + 1e-15) + log_pa  
            log_wb = math.log(1 - pi_a + 1e-15) + log_pb  
            max_log = max(log_wa, log_wb)  
            wa = math.exp(log_wa - max_log)  
            wb = math.exp(log_wb - max_log)  
            responsibilities.append(wa / (wa + wb))  
  
        sum_r = sum(responsibilities)  
        pi_a_new = sum_r / n  
        num_a = sum(r * k for r, (k, t) in zip(responsibilities, counts_list))  
        den_a = sum(r * t for r, (k, t) in zip(responsibilities, counts_list))  
        p_a_new = num_a / den_a if den_a > 0 else 0.5  
        num_b = sum((1 - r) * k for r, (k, t) in zip(responsibilities, counts_list))  
        den_b = sum((1 - r) * t for r, (k, t) in zip(responsibilities, counts_list))  
        p_b_new = num_b / den_b if den_b > 0 else 0.5  
  
        if (abs(p_a_new - p_a) < tol and abs(p_b_new - p_b) < tol  
                and abs(pi_a_new - pi_a) < tol):  
            break  
        p_a, p_b, pi_a = p_a_new, p_b_new, pi_a_new  
  
    if p_a < p_b:  
        p_a, p_b = p_b, p_a  
        pi_a = 1 - pi_a  
        responsibilities = [1 - r for r in responsibilities]  
  
    assignments = [1 if r > 0.5 else 0 for r in responsibilities]  
    return p_a, p_b, pi_a, responsibilities, assignments  
  
  
def main():  
    if len(sys.argv) < 2:  
        print("Usage: python3 script.py <ivtff_file>")  
        sys.exit(1)  
  
    folio_lines = parse_ivtff(sys.argv[1])  
    ordered = sorted(folio_lines.keys(), key=folio_sort_key)  
  
    # ================================================================  
    # TEST 1: WORD-LEVEL INDEPENDENCE  
    # ================================================================  
    print(f"\n{'='*78}")  
    print("TEST 1: WORD-LEVEL INDEPENDENCE")  
    print("Testing within-folio transitions")  
    print(f"{'='*78}")  
  
    folio_cho_counts = {}  
    for fid in ordered:  
        cho = 0  
        che = 0  
        for words in folio_lines[fid]:  
            for word in words:  
                c = classify_word_cho(word)  
                if c == 'cho':  
                    cho += 1  
                elif c == 'che':  
                    che += 1  
        folio_cho_counts[fid] = (cho, cho + che)  
  
    counts_list = [(folio_cho_counts[f][0], folio_cho_counts[f][1])  
                   for f in ordered if folio_cho_counts[f][1] >= 5]  
    fids_valid = [f for f in ordered if folio_cho_counts[f][1] >= 5]  
    p_a, p_b, pi_a, resps, assigns = em_two_state(  
        [(folio_cho_counts[f][0], folio_cho_counts[f][1]) for f in fids_valid]  
    )  
    assign_map = {f: a for f, a in zip(fids_valid, assigns)}  
    resp_map = {f: r for f, r in zip(fids_valid, resps)}  
  
    # ---- Test A: Within-folio transitions ----  
    print(f"\n  Test A: WITHIN-FOLIO transitions")  
    print(f"  (Each transition pair comes from the same folio)")  
  
    wf_cho_cho = 0  
    wf_cho_che = 0  
    wf_che_cho = 0  
    wf_che_che = 0  
  
    for fid in ordered:  
        prev = None  
        for words in folio_lines[fid]:  
            for word in words:  
                curr = classify_word_cho(word)  
                if curr is None:  
                    prev = None  
                    continue  
                if prev is not None:  
                    if prev == 'cho' and curr == 'cho':  
                        wf_cho_cho += 1  
                    elif prev == 'cho' and curr == 'che':  
                        wf_cho_che += 1  
                    elif prev == 'che' and curr == 'cho':  
                        wf_che_cho += 1  
                    elif prev == 'che' and curr == 'che':  
                        wf_che_che += 1  
                prev = curr  
  
    total_after_cho = wf_cho_cho + wf_cho_che  
    total_after_che = wf_che_cho + wf_che_che  
    p_cho_after_cho = wf_cho_cho / total_after_cho if total_after_cho > 0 else 0  
    p_cho_after_che = wf_che_cho / total_after_che if total_after_che > 0 else 0  
    diff_wf = p_cho_after_cho - p_cho_after_che  
  
    se_wf = math.sqrt(  
        p_cho_after_cho * (1 - p_cho_after_cho) / total_after_cho +  
        p_cho_after_che * (1 - p_cho_after_che) / total_after_che  
    ) if total_after_cho > 0 and total_after_che > 0 else 1  
  
    print(f"\n  All folios combined:")  
    print(f"    P(cho|prev=cho) = {p_cho_after_cho:.4f} (n={total_after_cho})")  
    print(f"    P(cho|prev=che) = {p_cho_after_che:.4f} (n={total_after_che})")  
    print(f"    Difference: {diff_wf:+.4f}, Z={diff_wf/se_wf:+.2f}")  
  
    # ---- Test B: Within-folio, by folio state ----  
    print(f"\n  Test B: Within-folio transitions, BY FOLIO STATE")  
  
    for state_label, state_val in [("State A (cho-dom)", 1),  
                                    ("State B (che-dom)", 0)]:  
        s_cho_cho = 0  
        s_cho_che = 0  
        s_che_cho = 0  
        s_che_che = 0  
  
        state_fids = [f for f in fids_valid if assign_map[f] == state_val]  
        for fid in state_fids:  
            prev = None  
            for words in folio_lines[fid]:  
                for word in words:  
                    curr = classify_word_cho(word)  
                    if curr is None:  
                        prev = None  
                        continue  
                    if prev is not None:  
                        if prev == 'cho' and curr == 'cho':  
                            s_cho_cho += 1  
                        elif prev == 'cho' and curr == 'che':  
                            s_cho_che += 1  
                        elif prev == 'che' and curr == 'cho':  
                            s_che_cho += 1  
                        elif prev == 'che' and curr == 'che':  
                            s_che_che += 1  
                    prev = curr  
  
        t_ac = s_cho_cho + s_cho_che  
        t_ae = s_che_cho + s_che_che  
        if t_ac > 10 and t_ae > 10:  
            p1 = s_cho_cho / t_ac  
            p2 = s_che_cho / t_ae  
            d = p1 - p2  
            se = math.sqrt(p1 * (1 - p1) / t_ac + p2 * (1 - p2) / t_ae)  
            z = d / se if se > 0 else 0  
            print(f"\n    {state_label} ({len(state_fids)} folios):")  
            print(f"      P(cho|prev=cho) = {p1:.4f} (n={t_ac})")  
            print(f"      P(cho|prev=che) = {p2:.4f} (n={t_ae})")  
            print(f"      Difference: {d:+.4f}, Z={z:+.2f}")  
  
    # ---- Test C: Per-folio analysis ----  
    print(f"\n  Test C: Per-folio transition analysis")  
    print(f"  (Computing difference for each folio individually)")  
  
    folio_diffs = []  
    folio_diffs_weighted = []  
  
    for fid in ordered:  
        cc = 0  
        ce = 0  
        ec = 0  
        ee = 0  
        prev = None  
        for words in folio_lines[fid]:  
            for word in words:  
                curr = classify_word_cho(word)  
                if curr is None:  
                    prev = None  
                    continue  
                if prev is not None:  
                    if prev == 'cho' and curr == 'cho':  
                        cc += 1  
                    elif prev == 'cho' and curr == 'che':  
                        ce += 1  
                    elif prev == 'che' and curr == 'cho':  
                        ec += 1  
                    elif prev == 'che' and curr == 'che':  
                        ee += 1  
                prev = curr  
  
        t1 = cc + ce  
        t2 = ec + ee  
        if t1 >= 5 and t2 >= 5:  
            p1 = cc / t1  
            p2 = ec / t2  
            d = p1 - p2  
            w = min(t1, t2)  
            folio_diffs.append(d)  
            folio_diffs_weighted.append((d, w))  
  
    if folio_diffs:  
        mean_d = statistics.mean(folio_diffs)  
        total_w = sum(w for d, w in folio_diffs_weighted)  
        wmean_d = sum(d * w for d, w in folio_diffs_weighted) / total_w  
  
        n_pos = sum(1 for d in folio_diffs if d > 0)  
        n_neg = sum(1 for d in folio_diffs if d < 0)  
        n_zero = sum(1 for d in folio_diffs if d == 0)  
  
        se_mean = statistics.stdev(folio_diffs) / math.sqrt(len(folio_diffs))  
        t_stat = mean_d / se_mean if se_mean > 0 else 0  
  
        print(f"\n    Folios with sufficient data: {len(folio_diffs)}")  
        print(f"    Mean difference: {mean_d:+.4f}")  
        print(f"    Weighted mean: {wmean_d:+.4f}")  
        print(f"    t-statistic: {t_stat:+.2f}")  
        print(f"    Sign test: {n_pos} positive, {n_neg} negative, "  
              f"{n_zero} zero")  
        print(f"    Median difference: {statistics.median(folio_diffs):+.4f}")  
  
        print(f"\n    Distribution of per-folio P(cho|cho) - P(cho|che):")  
        bins = [(-1, -0.3), (-0.3, -0.1), (-0.1, 0.1),  
                (0.1, 0.3), (0.3, 1.0)]  
        for lo, hi in bins:  
            count = sum(1 for d in folio_diffs if lo <= d < hi)  
            bar = '#' * count  
            print(f"      [{lo:+.1f}, {hi:+.1f}): {count:>3} {bar}")  
  
    # ---- Test D: Within-section, controlling for folio state ----  
    print(f"\n  Test D: Within-section transitions, controlling for folio state")  
  
    for section in ['herbal', 'text', 'astro', 'cosmo', 'zodiac',  
                    'bio', 'pharma', 'stars']:  
        for state_label, state_val in [("cho-dom", 1), ("che-dom", 0)]:  
            sec_state_fids = [f for f in fids_valid  
                              if get_section(f) == section  
                              and assign_map.get(f) == state_val]  
            if len(sec_state_fids) < 5:  
                continue  
  
            s_cc = 0  
            s_ce = 0  
            s_ec = 0  
            s_ee = 0  
            for fid in sec_state_fids:  
                prev = None  
                for words in folio_lines[fid]:  
                    for word in words:  
                        curr = classify_word_cho(word)  
                        if curr is None:  
                            prev = None  
                            continue  
                        if prev is not None:  
                            if prev == 'cho' and curr == 'cho':  
                                s_cc += 1  
                            elif prev == 'cho' and curr == 'che':  
                                s_ce += 1  
                            elif prev == 'che' and curr == 'cho':  
                                s_ec += 1  
                            elif prev == 'che' and curr == 'che':  
                                s_ee += 1  
                        prev = curr  
  
            t1 = s_cc + s_ce  
            t2 = s_ec + s_ee  
            if t1 >= 10 and t2 >= 10:  
                p1 = s_cc / t1  
                p2 = s_ec / t2  
                d = p1 - p2  
                se = math.sqrt(p1*(1-p1)/t1 + p2*(1-p2)/t2)  
                z = d / se if se > 0 else 0  
                print(f"\n    {section.upper()} / {state_label} "  
                      f"({len(sec_state_fids)} folios):")  
                print(f"      P(cho|prev=cho) = {p1:.4f} (n={t1})")  
                print(f"      P(cho|prev=che) = {p2:.4f} (n={t2})")  
                print(f"      Diff: {d:+.4f}, Z={z:+.2f}")  
  
    # ================================================================  
    # TEST 2: BOOTSTRAP 
    # ================================================================  
    print(f"\n{'='*78}")  
    print("TEST 2: BOOTSTRAP")  
    print(f"{'='*78}")  
  
    random.seed(42)  
    n_boot = 500  
  
    cho_data = [(folio_cho_counts[f][0], folio_cho_counts[f][1])  
              for f in ordered if folio_cho_counts[f][1] >= 5]  
  
    boot_pa = []  
    boot_pb = []  
    boot_pia = []  
    boot_daic = []  
  
    for b in range(n_boot):  
        sample = [cho_data[random.randint(0, len(cho_data) - 1)]  
                  for _ in range(len(cho_data))]  
  
        try:  
            pa, pb, pia, _, _ = em_two_state(sample)  
        except Exception:  
            continue  
  
        total_k = sum(k for k, t in sample)  
        total_t = sum(t for k, t in sample)  
        ps = total_k / total_t if total_t > 0 else 0.5  
        ll1 = sum(  
            k * math.log(max(ps, 1e-15)) +  
            (t - k) * math.log(max(1 - ps, 1e-15))  
            for k, t in sample if t > 0  
        )  
  
        ll2 = 0  
        for k, t in sample:  
            if t == 0:  
                continue  
            lpa = k * math.log(max(pa, 1e-15)) +   (t - k) * math.log(max(1 - pa, 1e-15))  
            lpb = k * math.log(max(pb, 1e-15)) +   (t - k) * math.log(max(1 - pb, 1e-15))  
            lwa = math.log(pia + 1e-15) + lpa  
            lwb = math.log(1 - pia + 1e-15) + lpb  
            mx = max(lwa, lwb)  
            ll2 += mx + math.log(math.exp(lwa - mx) + math.exp(lwb - mx))  
  
        daic = (-2 * ll1 + 2) - (-2 * ll2 + 6)  
  
        boot_pa.append(pa)  
        boot_pb.append(pb)  
        boot_pia.append(pia)  
        boot_daic.append(daic)  
  
    boot_pa.sort()  
    boot_pb.sort()  
    boot_pia.sort()  
    boot_daic.sort()  
  
    ci = lambda arr: (arr[int(len(arr) * 0.025)], arr[int(len(arr) * 0.975)])  
  
    print(f"\n  cho/che bootstrap ({n_boot} resamples):")  
    lo, hi = ci(boot_pa)  
    print(f"    p_A: {statistics.mean(boot_pa):.3f} [{lo:.3f}, {hi:.3f}]")  
    lo, hi = ci(boot_pb)  
    print(f"    p_B: {statistics.mean(boot_pb):.3f} [{lo:.3f}, {hi:.3f}]")  
    lo, hi = ci(boot_pia)  
    print(f"    pi_A: {statistics.mean(boot_pia):.3f} [{lo:.3f}, {hi:.3f}]")  
    lo, hi = ci(boot_daic)  
    print(f"    dAIC: {statistics.mean(boot_daic):.0f} [{lo:.0f}, {hi:.0f}]")  
    print(f"    dAIC > 0 in {sum(1 for d in boot_daic if d > 0)}/{n_boot}")  
    print(f"    p_A range: {min(boot_pa):.3f} to {max(boot_pa):.3f}")  
    print(f"    p_B range: {min(boot_pb):.3f} to {max(boot_pb):.3f}")  
  
    # d/l bootstrap  
    dl_data = []  
    for fid in ordered:  
        d_count = 0  
        l_count = 0  
        for words in folio_lines[fid]:  
            for word in words:  
                d_count += word.count('d')  
                l_count += word.count('l')  
        total = d_count + l_count  
        if total >= 20:  
            dl_data.append((d_count, total))  
  
    boot_pa_dl = []  
    boot_pb_dl = []  
    boot_daic_dl = []  
  
    for b in range(n_boot):  
        sample = [dl_data[random.randint(0, len(dl_data) - 1)]  
                  for _ in range(len(dl_data))]  
        try:  
            pa, pb, pia, _, _ = em_two_state(sample)  
        except Exception:  
            continue  
  
        total_k = sum(k for k, t in sample)  
        total_t = sum(t for k, t in sample)  
        ps = total_k / total_t if total_t > 0 else 0.5  
        ll1 = sum(  
            k * math.log(max(ps, 1e-15)) +  
            (t - k) * math.log(max(1 - ps, 1e-15))  
            for k, t in sample if t > 0  
        )  
  
        ll2 = 0  
        for k, t in sample:  
            if t == 0:  
                continue  
            lpa = k * math.log(max(pa, 1e-15)) +  (t - k) * math.log(max(1 - pa, 1e-15))  
            lpb = k * math.log(max(pb, 1e-15)) +  (t - k) * math.log(max(1 - pb, 1e-15))  
            lwa = math.log(pia + 1e-15) + lpa  
            lwb = math.log(1 - pia + 1e-15) + lpb  
            mx = max(lwa, lwb)  
            ll2 += mx + math.log(math.exp(lwa - mx) + math.exp(lwb - mx))  
  
        daic = (-2 * ll1 + 2) - (-2 * ll2 + 6)  
        boot_pa_dl.append(pa)  
        boot_pb_dl.append(pb)  
        boot_daic_dl.append(daic)  
  
    boot_pa_dl.sort()  
    boot_pb_dl.sort()  
    boot_daic_dl.sort()  
  
    print(f"\n  d/l bootstrap ({n_boot} resamples):")  
    lo, hi = ci(boot_pa_dl)  
    print(f"    p_A: {statistics.mean(boot_pa_dl):.3f} [{lo:.3f}, {hi:.3f}]")  
    lo, hi = ci(boot_pb_dl)  
    print(f"    p_B: {statistics.mean(boot_pb_dl):.3f} [{lo:.3f}, {hi:.3f}]")  
    lo, hi = ci(boot_daic_dl)  
    print(f"    dAIC: {statistics.mean(boot_daic_dl):.0f} [{lo:.0f}, {hi:.0f}]")  
    print(f"    dAIC > 0 in {sum(1 for d in boot_daic_dl if d > 0)}/{n_boot}")  
  
    # ================================================================  
    # TEST 3: POSITIONAL EFFECT  
    # ================================================================  
    print(f"\n{'='*78}")  
    print("ISSUE 3: POSITIONAL EFFECT")  
    print("Is the position effect real, or a section/folio confound?")  
    print(f"{'='*78}")  
  
    cho_dom_fids = [f for f in fids_valid if assign_map.get(f) == 1]  
    che_dom_fids = [f for f in fids_valid if assign_map.get(f) == 0]  
  
    for label, fid_set in [("CHO-dominant folios", cho_dom_fids),  
                            ("CHE-dominant folios", che_dom_fids)]:  
        pos_cho = defaultdict(int)  
        pos_che = defaultdict(int)  
  
        for fid in fid_set:  
            for words in folio_lines[fid]:  
                for word_idx, word in enumerate(words):  
                    glyphs = word_to_glyphs(word)  
                    for i in range(len(glyphs) - 1):  
                        if glyphs[i] in ('ch', 'sh'):  
                            if glyphs[i + 1] == 'o':  
                                pos_cho[word_idx] += 1  
                            elif glyphs[i + 1] == 'e':  
                                pos_che[word_idx] += 1  
  
        print(f"\n  {label}:")  
        print(f"  {'Position':>10} {'cho':>6} {'che':>6} {'ratio':>8}")  
        for pos in range(12):  
            c = pos_cho.get(pos, 0)  
            e = pos_che.get(pos, 0)  
            total = c + e  
            if total >= 15:  
                ratio = c / total  
                print(f"  {pos:>10} {c:>6} {e:>6} {ratio:>8.3f}")  
  
    # ================================================================  
    # TEST 4: d/l BINARY OR GRADIENT  
    # ================================================================  
    print(f"\n{'='*78}")  
    print("TEST 4: d/l PARAMETER -- BINARY OR GRADIENT?")  
    print("Comparing 2-state, 3-state, and continuous models")  
    print(f"{'='*78}")  
  
    pa_dl, pb_dl, pia_dl, resps_dl, assigns_dl = em_two_state(dl_data)  
  
    residuals = []  
    for i, (k, t) in enumerate(dl_data):  
        if t == 0:  
            continue  
        r = resps_dl[i]  
        expected_p = r * pa_dl + (1 - r) * pb_dl  
        observed_p = k / t  
        residuals.append(observed_p - expected_p)  
  
    print(f"\n  d/l two-state model:")  
    print(f"    p_A = {pa_dl:.3f}, p_B = {pb_dl:.3f}")  
    print(f"    Separation: {pa_dl - pb_dl:.3f}")  
    print(f"    Residual std: {statistics.stdev(residuals):.4f}")  
  
    pa_cho, pb_cho, pia_cho, resps_cho, assigns_cho = em_two_state(cho_data)  
    residuals_cho = []  
    for i, (k, t) in enumerate(cho_data):  
        if t == 0:  
            continue  
        r = resps_cho[i]  
        expected_p = r * pa_cho + (1 - r) * pb_cho  
        observed_p = k / t  
        residuals_cho.append(observed_p - expected_p)  
  
    print(f"\n  cho/che two-state model:")  
    print(f"    p_A = {pa_cho:.3f}, p_B = {pb_cho:.3f}")  
    print(f"    Separation: {pa_cho - pb_cho:.3f}")  
    print(f"    Residual std: {statistics.stdev(residuals_cho):.4f}")  
  
    print(f"\n  d/l conditional on cho/che state (within Herbal):")  
    herbal_fids = [f for f in fids_valid if get_section(f) == 'herbal']  
    for cho_state, cho_label in [(1, "cho-dom"), (0, "che-dom")]:  
        subset = [f for f in herbal_fids if assign_map.get(f) == cho_state]  
        if len(subset) < 5:  
            continue  
        rd_vals = []  
        for f in subset:  
            d_count = 0  
            l_count = 0  
            for words in folio_lines[f]:  
                for word in words:  
                    d_count += word.count('d')  
                    l_count += word.count('l')  
            total = d_count + l_count  
            if total >= 20:  
                rd_vals.append(d_count / total)  
        if rd_vals:  
            print(f"    {cho_label} ({len(rd_vals)} folios): "  
                  f"mean r_d = {statistics.mean(rd_vals):.3f}, "  
                  f"std = {statistics.stdev(rd_vals):.3f}")  
  
    # ================================================================  
    # TEST 5: TEMPLATE SWITCHING  
    # ================================================================  
    print(f"\n{'='*78}")  
    print("TEST 5: TEMPLATE SWITCHING quantified")  
    print("What fraction of cho/che variation is folio-driven vs word-driven?")  
    print(f"{'='*78}")  
  
    template_data = defaultdict(lambda: {'A_cho': 0, 'A_che': 0,  
                                          'B_cho': 0, 'B_che': 0})  
  
    for fid in fids_valid:  
        state = 'A' if assign_map.get(fid) == 1 else 'B'  
        for words in folio_lines[fid]:  
            for word in words:  
                glyphs = word_to_glyphs(word)  
                template_parts = []  
                has_target = False  
                word_cho = 0  
                word_che = 0  
                for i in range(len(glyphs)):  
                    if (i > 0 and glyphs[i - 1] in ('ch', 'sh')  
                            and glyphs[i] in ('o', 'e')):  
                        template_parts.append('X')  
                        has_target = True  
                        if glyphs[i] == 'o':  
                            word_cho += 1  
                        else:  
                            word_che += 1  
                    else:  
                        template_parts.append(glyphs[i])  
  
                if has_target:  
                    template = ''.join(template_parts)  
                    if state == 'A':  
                        template_data[template]['A_cho'] += word_cho  
                        template_data[template]['A_che'] += word_che  
                    else:  
                        template_data[template]['B_cho'] += word_cho  
                        template_data[template]['B_che'] += word_che  
  
    a_rates = []  
    b_rates = []  
    a_totals = []  
    b_totals = []  
    template_names = []  
  
    for template, counts in template_data.items():  
        at = counts['A_cho'] + counts['A_che']  
        bt = counts['B_cho'] + counts['B_che']  
        if at >= 10 and bt >= 10:  
            ar = counts['A_cho'] / at  
            br = counts['B_cho'] / bt  
            a_rates.append(ar)  
            b_rates.append(br)  
            a_totals.append(at)  
            b_totals.append(bt)  
            template_names.append(template)  
  
    if a_rates:  
        mean_a = statistics.mean(a_rates)  
        mean_b = statistics.mean(b_rates)  
        std_a = statistics.stdev(a_rates) if len(a_rates) > 1 else 0  
        std_b = statistics.stdev(b_rates) if len(b_rates) > 1 else 0  
  
        if std_a > 0 and std_b > 0:  
            corr = sum(  
                (a_rates[i] - mean_a) * (b_rates[i] - mean_b)  
                for i in range(len(a_rates))  
            ) / ((len(a_rates) - 1) * std_a * std_b)  
        else:  
            corr = 0  
  
        print(f"\n  Templates with >= 10 instances in both states: "  
              f"{len(a_rates)}")  
        print(f"    Mean cho-rate in State A: {mean_a:.3f} (std={std_a:.3f})")  
        print(f"    Mean cho-rate in State B: {mean_b:.3f} (std={std_b:.3f})")  
        print(f"    Mean shift (A minus B): {mean_a - mean_b:+.3f}")  
        print(f"    Correlation(A-rate, B-rate): {corr:.3f}")  
  
        all_rates = a_rates + b_rates  
        total_var = statistics.variance(all_rates)  
        between_var = ((mean_a - statistics.mean(all_rates)) ** 2 +  
                       (mean_b - statistics.mean(all_rates)) ** 2) / 2  
        within_var_a = statistics.variance(a_rates) if len(a_rates) > 1 else 0  
        within_var_b = statistics.variance(b_rates) if len(b_rates) > 1 else 0  
        within_var = (within_var_a + within_var_b) / 2  
  
        print(f"\n    Variance decomposition:")  
        print(f"      Total variance: {total_var:.4f}")  
        print(f"      Between-state: {between_var:.4f} "  
              f"({between_var/total_var*100:.1f}%)")  
        print(f"      Within-state (template variation): {within_var:.4f} "  
              f"({within_var/total_var*100:.1f}%)")  
  
        # Classify and print ALL templates  
        print(f"\n    ALL {len(template_names)} TEMPLATES (sorted by class, then total count):")  
        print(f"    {'Template':<20} {'A_rate':>7} {'B_rate':>7} "  
              f"{'n_A':>5} {'n_B':>5} {'|Delta|':>7} {'Class':<12}")  
        print(f"    {'---'*20}")  
  
        # Classify each template  
        classified = []  
        for i in range(len(template_names)):  
            ar = a_rates[i]  
            br = b_rates[i]  
            delta = abs(ar - br)  
            na = a_totals[i]  
            nb = b_totals[i]  
            name = template_names[i]  
  
            if ar > 0.9 and br > 0.9:  
                cls = 'F1-fixed_cho'  
            elif ar < 0.1 and br < 0.1:  
                cls = 'F0-fixed_che'  
            elif delta >= 0.2:  
                cls = 'S-switchable'  
            else:  
                cls = 'I-intermediate'  
  
            classified.append((cls, name, ar, br, na, nb, delta))  
  
        # Sort by class then total count descending  
        class_order = {'F1-fixed_cho': 0, 'F0-fixed_che': 1,  
                       'S-switchable': 2, 'I-intermediate': 3}  
        classified.sort(key=lambda x: (class_order.get(x[0], 9),  
                                        -(x[4] + x[5])))  
  
        current_class = None  
        for cls, name, ar, br, na, nb, delta in classified:  
            if cls != current_class:  
                current_class = cls  
                print(f"\n    --- {cls} ---")  
            print(f"    {name:<20} {ar:>7.3f} {br:>7.3f} "  
                  f"{na:>5} {nb:>5} {delta:>7.3f} {cls:<12}")  
  
        # Summary counts  
        class_counts = Counter(c[0] for c in classified)  
        print(f"\n    Class summary:")  
        for cls in ['F1-fixed_cho', 'F0-fixed_che', 'S-switchable', 'I-intermediate']:  
            templates_in_class = [c for c in classified if c[0] == cls]  
            total_events = sum(c[4] + c[5] for c in templates_in_class)  
            print(f"      {cls}: {class_counts.get(cls, 0)} templates, "  
                  f"{total_events} total events")  
 
    # ================================================================  
    # TEST 6: d/l ASSESSMENT  
    # ================================================================  
    print(f"\n{'='*78}")  
    print("TEST 6: d/l ASSESSMENT")  
    print(f"{'='*78}")  
  
    cho_dom_herbal = [f for f in herbal_fids  
                      if assign_map.get(f) == 1]  
  
    rd_cho_herbal = []  
    for f in cho_dom_herbal:  
        d_count = 0  
        l_count = 0  
        for words in folio_lines[f]:  
            for word in words:  
                d_count += word.count('d')  
                l_count += word.count('l')  
        total = d_count + l_count  
        if total >= 20:  
            rd_cho_herbal.append((f, d_count / total, total))  
  
    if rd_cho_herbal:  
        vals = [v for _, v, _ in rd_cho_herbal]  
        bc = (lambda d: (  
            (sum((x - statistics.mean(d))**3 for x in d) /  
             (len(d) * statistics.stdev(d)**3))**2 + 1  
        ) / (  
            sum((x - statistics.mean(d))**4 for x in d) /  
            (len(d) * statistics.stdev(d)**4)  
        ))(vals) if len(vals) > 3 and statistics.stdev(vals) > 0 else None  
  
        print(f"\n  d/l within cho-dominant Herbal ({len(vals)} folios):")  
        print(f"    Mean: {statistics.mean(vals):.3f}")  
        print(f"    Std:  {statistics.stdev(vals):.3f}")  
        if bc:  
            print(f"    BC:   {bc:.3f} (>0.555 suggests bimodality)")  
  
        bins = [0, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.01]  
        print(f"    Histogram:")  
        for i in range(len(bins) - 1):  
            count = sum(1 for v in vals if bins[i] <= v < bins[i + 1])  
            bar = '#' * count  
            print(f"      [{bins[i]:.1f}-{bins[i+1]:.1f}): {count:>3} {bar}")  
  
    print(f"\n{'='*78}")  

    # ================================================================  
    # APPENDIX: HERBAL FOLIO DETAIL  
    # ================================================================  
    print(f"\n{'='*78}")  
    print("APPENDIX: HERBAL FOLIO DETAIL")  
    print(f"{'='*78}")  
  
    section_map = build_folio_section_map()  
    herbal_ordered = [f for f in ordered if section_map.get(f) == 'herbal']  
  
    print(f"\n  {'Folio':<8} {'sig':>3} {'n_cho':>5} {'n_che':>5} "  
          f"{'r_cho':>6} {'Conf':>6} {'e/ch':>6} {'d/l':>6} {'Words':>5}")  
    print(f"  {'-'*58}")  
  
    for fid in herbal_ordered:  
        # Boolean switch  
        sigma = assign_map.get(fid, -1)  
        post = resp_map.get(fid, float('nan'))  
        conf = post if sigma == 1 else (1 - post) if sigma == 0 else float('nan')  
  
        # cho/che counts  
        cho_c = 0  
        che_c = 0  
        for wline in folio_lines[fid]:  
            for w in wline:  
                c = classify_word_cho(w)  
                if c == 'cho':  
                    cho_c += 1  
                elif c == 'che':  
                    che_c += 1  
        total_cc = cho_c + che_c  
        r_cho = cho_c / total_cc if total_cc >= 5 else float('nan')  
  
        # e/ch and d/l from glyphs  
        e_ct = 0  
        ch_ct = 0  
        d_ct = 0  
        l_ct = 0  
        w_ct = 0  
        for wline in folio_lines[fid]:  
            for w in wline:  
                w_ct += 1  
                gl = word_to_glyphs(w)  
                for g in gl:  
                    if g == 'e':  
                        e_ct += 1  
                    elif g == 'ch':  
                        ch_ct += 1  
                    elif g == 'd':  
                        d_ct += 1  
                    elif g == 'l':  
                        l_ct += 1  
  
        ech = e_ct / (e_ct + ch_ct) if (e_ct + ch_ct) >= 10 else float('nan')  
        dl = d_ct / (d_ct + l_ct) if (d_ct + l_ct) >= 10 else float('nan')  
  
        sig_str = str(sigma) if sigma >= 0 else '?'  
        r_str = f'{r_cho:.3f}' if not math.isnan(r_cho) else 'n/a'  
        c_str = f'{conf:.3f}' if not math.isnan(conf) else 'n/a'  
        e_str = f'{ech:.3f}' if not math.isnan(ech) else 'n/a'  
        d_str = f'{dl:.3f}' if not math.isnan(dl) else 'n/a'  
  
        print(f"  {fid:<8} {sig_str:>3} {cho_c:>5} {che_c:>5} "  
              f"{r_str:>6} {c_str:>6} {e_str:>6} {d_str:>6} {w_ct:>5}")  
  
    # Summary  
    hv = [f for f in herbal_ordered if folio_cho_counts.get(f, (0,0))[1] >= 5]  
    h1 = [f for f in hv if assign_map.get(f) == 1]  
    h0 = [f for f in hv if assign_map.get(f) == 0]  
    print(f"\n  Summary:")  
    print(f"    Herbal folios: {len(herbal_ordered)}")  
    print(f"    Classifiable (>= 5 words): {len(hv)}")  
    print(f"    sigma=1 (cho-dom): {len(h1)}")  
    print(f"    sigma=0 (che-dom): {len(h0)}")  
    if h1:  
        r1 = [folio_cho_counts[f][0]/folio_cho_counts[f][1] for f in h1]  
        print(f"    Mean r_cho (sigma=1): {statistics.mean(r1):.3f} +/- {statistics.stdev(r1):.3f}")  
    if h0:  
        r0 = [folio_cho_counts[f][0]/folio_cho_counts[f][1] for f in h0]  
        print(f"    Mean r_cho (sigma=0): {statistics.mean(r0):.3f} +/- {statistics.stdev(r0):.3f}")  
  
if __name__ == '__main__':  
    main()  
