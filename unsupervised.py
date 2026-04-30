#!/usr/bin/env python3  
"""  
Blind Clustering Test  
=====================  
Can unsupervised methods recover the Currier A/B split  
from folio-level pair ratios alone, without seeing labels?  
  
Methods:  
  1. K-means (k=2) on ratio vectors  
  2. Gaussian Mixture Model (k=2)  
  3. Hierarchical clustering (Ward, k=2)  
  4. Spectral clustering (k=2)  
  5. PCA visualization with true labels revealed after  
  
Agreement measured by Adjusted Rand Index (ARI):  
  ARI = 1.0  -> perfect agreement  
  ARI = 0.0  -> chance-level agreement  
  ARI < 0.0  -> worse than chance  
  
Bootstrap stability: repeat clustering on resampled features  
to measure how stable the recovered partition is.  
"""  
  
import re  
import math  
import sys  
from collections import Counter, defaultdict  
  
import numpy as np  
from scipy import stats as sp_stats  
from scipy.cluster.hierarchy import linkage, fcluster  
from scipy.spatial.distance import pdist  
  
from sklearn.cluster import KMeans, SpectralClustering  
from sklearn.mixture import GaussianMixture  
from sklearn.metrics import (  
    adjusted_rand_score,  
    normalized_mutual_info_score,  
    silhouette_score,  
    confusion_matrix,  
)  
from sklearn.decomposition import PCA  
from sklearn.preprocessing import StandardScaler  
  
# ====================================================================  
# EVA TOKENIZER (same as main analysis)  
# ====================================================================  
  
EVA_MULTIGRAPHS = sorted([  
    "cth", "cph", "cfh", "ckh",  
    "sh", "ch", "ck", "ct", "cp", "cf",  
    "ii", "ee", "ai", "ei", "oi",  
    "in", "ir", "ar", "or", "al", "ol",  
    "an", "am", "dy", "dl", "dm", "ds",  
    "ed", "es", "ey",  
    "ly", "ry", "ny", "my",  
], key=lambda x: (-len(x), x))  
  
CONFUSABLE_PAIRS = [  
    ("k", "t", "k/t"),  
    ("ch", "sh", "ch/sh"),  
    ("o", "a", "o/a"),  
    ("d", "l", "d/l"),  
    ("f", "p", "f/p"),  
    ("e", "ch", "e/ch"),  
    ("e", "ee", "e/ee"),  
    ("or", "ar", "or/ar"),  
    ("ol", "al", "ol/al"),  
    ("y", "dy", "y/dy"),  
    ("s", "r", "s/r"),  
]  
  
MIN_TOKENS = 20  
  
  
def eva_tokenize(word):  
    tokens = []  
    i = 0  
    while i < len(word):  
        matched = False  
        for g in EVA_MULTIGRAPHS:  
            if word[i:i + len(g)] == g:  
                tokens.append(g)  
                i += len(g)  
                matched = True  
                break  
        if not matched:  
            tokens.append(word[i])  
            i += 1  
    return tokens  
  
  
# ====================================================================  
# PARSER  
# ====================================================================  
  
def parse_ivtff(filepath):  
    words_by_folio = defaultdict(list)  
    line_re = re.compile(r"<(f\d+[rv]\d*)\.\d+,[^>]*>")  
    with open(filepath, "r", encoding="utf-8", errors="replace") as fh:  
        for raw in fh:  
            raw = raw.rstrip("\n\r")  
            if not raw or raw.startswith("#"):  
                continue  
            m = line_re.search(raw)  
            if not m:  
                continue  
            raw_folio_id = m.group(1)  
            folio_m = re.match(r"(f\d+[rv])", raw_folio_id)  
            if not folio_m:  
                continue  
            folio_id = folio_m.group(1)  
            gt_pos = raw.index(">", raw.index(m.group(0))) + 1  
            text = raw[gt_pos:].strip()  
            if not text:  
                continue  
            text = re.sub(r"\{[^}]*\}", "", text)  
            text = re.sub(r"@\w*;?", "", text)  
            text = re.sub(r"[?!*]", "", text)  
            for tok in text.split("."):  
                tok = tok.strip()  
                if "," in tok:  
                    tok = tok.split(",")[0].strip()  
                if tok and re.fullmatch(r"[a-z2]+", tok):  
                    words_by_folio[folio_id].append(tok)  
    return dict(words_by_folio)  
  
  
# ====================================================================  
# LANGUAGE MAP  
# ====================================================================  
  
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
  
  
# ====================================================================  
# BUILD FEATURE MATRIX  
# ====================================================================  
  
def folio_sort_key(fid):  
    m = re.search(r'(\d+)', fid)  
    num = int(m.group(1)) if m else 0  
    return (num, fid)  
  
  
def build_feature_matrix(words_by_folio, folio_lang):  
    """  
    Build folio x pair ratio matrix.  
    Folios with too many missing pairs are excluded.  
    Missing values are imputed with column median.  
    Returns: X (n_folios x n_pairs), folio_ids, true_labels,  
             pair_labels, raw_ratios (before imputation)  
    """  
    folio_order = sorted(  
        [f for f in words_by_folio if f in folio_lang],  
        key=folio_sort_key)  
  
    target_tokens = set()  
    for sa, sb, _ in CONFUSABLE_PAIRS:  
        target_tokens.add(sa)  
        target_tokens.add(sb)  
  
    # Compute ratios  
    raw_ratios = {}  
    for fid in folio_order:  
        token_counts = Counter()  
        for w in words_by_folio[fid]:  
            for t in eva_tokenize(w):  
                if t in target_tokens:  
                    token_counts[t] += 1  
  
        raw_ratios[fid] = {}  
        for sa, sb, label in CONFUSABLE_PAIRS:  
            ca = token_counts[sa]  
            cb = token_counts[sb]  
            total = ca + cb  
            if total >= MIN_TOKENS:  
                raw_ratios[fid][label] = ca / total  
            else:  
                raw_ratios[fid][label] = float('nan')  
  
    pair_labels = [p[2] for p in CONFUSABLE_PAIRS]  
  
    # Filter folios: require at least 6 of 11 pairs present  
    MIN_PAIRS = 6  
    valid_folios = []  
    for fid in folio_order:  
        n_valid = sum(1 for lb in pair_labels  
                      if not math.isnan(raw_ratios[fid][lb]))  
        if n_valid >= MIN_PAIRS:  
            valid_folios.append(fid)  
  
    # Build matrix  
    n = len(valid_folios)  
    p = len(pair_labels)  
    X_raw = np.full((n, p), np.nan)  
    for i, fid in enumerate(valid_folios):  
        for j, lb in enumerate(pair_labels):  
            X_raw[i, j] = raw_ratios[fid][lb]  
  
    # Impute missing values with column median  
    X = X_raw.copy()  
    for j in range(p):  
        col = X_raw[:, j]  
        valid_mask = ~np.isnan(col)  
        if valid_mask.sum() > 0:  
            median_val = np.median(col[valid_mask])  
            X[~valid_mask, j] = median_val  
  
    true_labels = np.array(  
        [0 if folio_lang[f] == "A" else 1 for f in valid_folios])  
  
    return X, valid_folios, true_labels, pair_labels, X_raw  
  
  
# ====================================================================  
# CLUSTERING METHODS  
# ====================================================================  
  
def run_kmeans(X, k, seed=42):  
    km = KMeans(n_clusters=k, n_init=50, random_state=seed)  
    return km.fit_predict(X)  
  
  
def run_gmm(X, k, seed=42):  
    gmm = GaussianMixture(  
        n_components=k, n_init=10, random_state=seed)  
    gmm.fit(X)  
    return gmm.predict(X), gmm.bic(X), gmm.aic(X)  
  
  
def run_hierarchical(X, k, method='ward'):  
    Z = linkage(X, method=method)  
    return fcluster(Z, k, criterion='maxclust') - 1  # 0-indexed  
  
  
def run_spectral(X, k, seed=42):  
    sc = SpectralClustering(  
        n_clusters=k, affinity='rbf', random_state=seed,  
        n_init=20)  
    return sc.fit_predict(X)  
  
  
# ====================================================================  
# EVALUATION  
# ====================================================================  
  
def evaluate_clustering(true_labels, pred_labels, name, X=None):  
    ari = adjusted_rand_score(true_labels, pred_labels)  
    nmi = normalized_mutual_info_score(true_labels, pred_labels)  
  
    # Compute accuracy (best label alignment)  
    cm = confusion_matrix(true_labels, pred_labels)  
    # Try both label assignments  
    n = len(true_labels)  
    if cm.shape == (2, 2):  
        acc1 = (cm[0, 0] + cm[1, 1]) / n  
        acc2 = (cm[0, 1] + cm[1, 0]) / n  
        acc = max(acc1, acc2)  
        # Identify misclassified count  
        misclass = n - int(acc * n + 0.5)  
    else:  
        acc = float('nan')  
        misclass = -1  
  
    sil = silhouette_score(X, pred_labels) if X is not None else float('nan')  
  
    return {  
        'name': name,  
        'ari': ari,  
        'nmi': nmi,  
        'accuracy': acc,  
        'misclassified': misclass,  
        'silhouette': sil,  
    }  
  
  
def find_misclassified(true_labels, pred_labels, folio_ids):  
    """Return list of folios where blind clustering disagrees  
    with Currier."""  
    cm = confusion_matrix(true_labels, pred_labels)  
    if cm.shape != (2, 2):  
        return []  
  
    acc1 = (cm[0, 0] + cm[1, 1]) / len(true_labels)  
    acc2 = (cm[0, 1] + cm[1, 0]) / len(true_labels)  
  
    if acc2 > acc1:  
        # Flip predicted labels  
        pred_labels = 1 - pred_labels  
  
    mismatches = []  
    for i, fid in enumerate(folio_ids):  
        if true_labels[i] != pred_labels[i]:  
            true_str = "A" if true_labels[i] == 0 else "B"  
            pred_str = "A" if pred_labels[i] == 0 else "B"  
            mismatches.append((fid, true_str, pred_str))  
    return mismatches  
  
  
# ====================================================================  
# BOOTSTRAP STABILITY  
# ====================================================================  
  
def bootstrap_ari(X, true_labels, n_boot=500, seed=42):  
    """Resample features (columns) and re-cluster, measure ARI  
    stability."""  
    rng = np.random.default_rng(seed)  
    n_samples, n_features = X.shape  
    aris = []  
  
    for _ in range(n_boot):  
        # Resample features with replacement  
        feat_idx = rng.choice(n_features, size=n_features,  
                              replace=True)  
        X_boot = X[:, feat_idx]  
        X_boot_scaled = StandardScaler().fit_transform(X_boot)  
  
        km = KMeans(n_clusters=2, n_init=20, random_state=42)  
        pred = km.fit_predict(X_boot_scaled)  
        ari = adjusted_rand_score(true_labels, pred)  
        aris.append(ari)  
  
    return np.array(aris)  
  
  
# ====================================================================  
# PERMUTATION TEST FOR ARI  
# ====================================================================  
  
def permutation_test_ari(X, true_labels, n_perm=1000, seed=42):  
    """Permute true labels, re-compute ARI to get null  
    distribution."""  
    rng = np.random.default_rng(seed)  
  
    # Observed ARI  
    km = KMeans(n_clusters=2, n_init=50, random_state=42)  
    pred = km.fit_predict(X)  
    obs_ari = adjusted_rand_score(true_labels, pred)  
  
    null_aris = []  
    for _ in range(n_perm):  
        perm_labels = true_labels.copy()  
        rng.shuffle(perm_labels)  
        ari = adjusted_rand_score(perm_labels, pred)  
        null_aris.append(ari)  
  
    null_aris = np.array(null_aris)  
    p_value = np.mean(null_aris >= obs_ari)  
  
    return obs_ari, null_aris, p_value  
  
  
# ====================================================================  
# LEAVE-ONE-PAIR-OUT ANALYSIS  
# ====================================================================  
  
def leave_one_out_pairs(X, true_labels, pair_labels, seed=42):  
    """Drop each pair in turn, re-cluster, measure ARI.  
    Identifies which pairs are essential."""  
    results = []  
    for j, plabel in enumerate(pair_labels):  
        X_reduced = np.delete(X, j, axis=1)  
        X_scaled = StandardScaler().fit_transform(X_reduced)  
        km = KMeans(n_clusters=2, n_init=50, random_state=seed)  
        pred = km.fit_predict(X_scaled)  
        ari = adjusted_rand_score(true_labels, pred)  
        results.append((plabel, ari))  
    return results  
  
  
# ====================================================================  
# SINGLE-PAIR CLUSTERING  
# ====================================================================  
  
def single_pair_clustering(X, true_labels, pair_labels, seed=42):  
    """Cluster using each pair alone. Shows which individual  
    pairs carry the signal."""  
    results = []  
    for j, plabel in enumerate(pair_labels):  
        col = X[:, j].reshape(-1, 1)  
        # Simple threshold: median split  
        median_val = np.median(col)  
        pred_median = (col.ravel() > median_val).astype(int)  
        ari_median = adjusted_rand_score(true_labels, pred_median)  
  
        # K-means on single feature  
        km = KMeans(n_clusters=2, n_init=50, random_state=seed)  
        pred_km = km.fit_predict(col)  
        ari_km = adjusted_rand_score(true_labels, pred_km)  
  
        results.append((plabel, ari_median, ari_km))  
    return results  
  
  
# ====================================================================  
# MAIN  
# ====================================================================  
  
def main():  
    import argparse  
    ap = argparse.ArgumentParser(  
        description="Blind clustering test for Currier A/B")  
    ap.add_argument("ivtff", help="Path to IVTFF file")  
    ap.add_argument("--n-boot", type=int, default=500,  
                    help="Bootstrap iterations (default: 500)")  
    ap.add_argument("--n-perm", type=int, default=1000,  
                    help="Permutation test iterations (default: 1000)")  
    ap.add_argument("--seed", type=int, default=42)  
    args = ap.parse_args()  
  
    W = 76  
    rng = np.random.default_rng(args.seed)  
  
    print(f"\n{'=' * W}")  
    print(f"  BLIND CLUSTERING TEST")  
    print(f"  Can unsupervised methods recover the Currier A/B split?")  
    print(f"{'=' * W}")  
  
    # ---- Parse and build features ----  
    print(f"\n  Parsing {args.ivtff} ...", end="", flush=True)  
    words_by_folio = parse_ivtff(args.ivtff)  
    folio_lang = build_folio_language_map()  
    print(f" done.")  
  
    print(f"  Building feature matrix ...", end="", flush=True)  
    X_raw, folio_ids, true_labels, pair_labels, X_unimputed = build_feature_matrix(words_by_folio, folio_lang)  
    print(f" done.")  
  
    n_folios, n_pairs = X_raw.shape  
    n_A = np.sum(true_labels == 0)  
    n_B = np.sum(true_labels == 1)  
    print(f"  Feature matrix: {n_folios} folios x {n_pairs} pairs")  
    print(f"  True labels: A={n_A}, B={n_B}")  
  
    # Count missing values  
    n_missing = np.sum(np.isnan(X_unimputed))  
    n_total = X_unimputed.size  
    print(f"  Missing values: {n_missing}/{n_total} "  
          f"({100 * n_missing / n_total:.1f}%)")  
  
    # ---- Standardize ----  
    scaler = StandardScaler()  
    X = scaler.fit_transform(X_raw)  
  
    # ================================================================  
    # SECTION 1: FOUR CLUSTERING METHODS AT k=2  
    # ================================================================  
    print(f"\n{'=' * W}")  
    print(f"  SECTION 1: BLIND CLUSTERING (k=2)")  
    print(f"{'=' * W}")  
  
    all_results = []  
  
    # K-means  
    print(f"\n  K-means (k=2) ...", end="", flush=True)  
    pred_km = run_kmeans(X, 2, seed=args.seed)  
    res_km = evaluate_clustering(true_labels, pred_km, "K-means", X)  
    all_results.append(res_km)  
    print(f" done. ARI={res_km['ari']:.3f}")  
  
    # GMM  
    print(f"  GMM (k=2) ...", end="", flush=True)  
    pred_gmm, bic_2, aic_2 = run_gmm(X, 2, seed=args.seed)  
    res_gmm = evaluate_clustering(  
        true_labels, pred_gmm, "GMM", X)  
    all_results.append(res_gmm)  
    print(f" done. ARI={res_gmm['ari']:.3f}")  
  
    # Hierarchical  
    print(f"  Hierarchical (Ward, k=2) ...", end="", flush=True)  
    pred_hc = run_hierarchical(X, 2)  
    res_hc = evaluate_clustering(  
        true_labels, pred_hc, "Hierarchical", X)  
    all_results.append(res_hc)  
    print(f" done. ARI={res_hc['ari']:.3f}")  
  
    # Spectral  
    print(f"  Spectral (k=2) ...", end="", flush=True)  
    pred_sp = run_spectral(X, 2, seed=args.seed)  
    res_sp = evaluate_clustering(  
        true_labels, pred_sp, "Spectral", X)  
    all_results.append(res_sp)  
    print(f" done. ARI={res_sp['ari']:.3f}")  
  
    # Summary table  
    print(f"\n  {'Method':<16} {'ARI':>7} {'NMI':>7} {'Acc':>7} "  
          f"{'Misclass':>9} {'Silhouette':>11}")  
    print(f"  {'-' * 60}")  
    for r in all_results:  
        print(f"  {r['name']:<16} {r['ari']:>7.3f} {r['nmi']:>7.3f} "  
              f"{r['accuracy']:>6.1%} {r['misclassified']:>9d} "  
              f"{r['silhouette']:>11.3f}")  
  
    # ---- Misclassified folios (K-means) ----  
    mismatches = find_misclassified(true_labels, pred_km, folio_ids)  
    if mismatches:  
        print(f"\n  Misclassified folios (K-means):")  
        print(f"    {'Folio':<10} {'Currier':>8} {'Blind':>8}")  
        print(f"    {'-' * 28}")  
        for fid, true_str, pred_str in mismatches:  
            print(f"    {fid:<10} {true_str:>8} {pred_str:>8}")  
  
    # ================================================================  
    # SECTION 2: PERMUTATION TEST  
    # ================================================================  
    print(f"\n{'=' * W}")  
    print(f"  SECTION 2: PERMUTATION TEST FOR ARI")  
    print(f"{'=' * W}")  
  
    print(f"\n  Running {args.n_perm} permutations ...", end="",  
          flush=True)  
    obs_ari, null_aris, perm_p = permutation_test_ari(  
        X, true_labels, args.n_perm, seed=args.seed)  
    print(f" done.")  
  
    print(f"  Observed ARI:     {obs_ari:.3f}")  
    print(f"  Null ARI mean:    {np.mean(null_aris):.3f}")  
    print(f"  Null ARI std:     {np.std(null_aris, ddof=1):.3f}")  
    print(f"  Null ARI 95th:    {np.percentile(null_aris, 95):.3f}")  
    print(f"  Null ARI max:     {np.max(null_aris):.3f}")  
    print(f"  p-value:          {perm_p:.4f}")  
    if perm_p == 0:  
        print(f"  (p < {1 / args.n_perm:.1e})")  
  
    # ================================================================  
    # SECTION 3: BOOTSTRAP STABILITY  
    # ================================================================  
    print(f"\n{'=' * W}")  
    print(f"  SECTION 3: BOOTSTRAP STABILITY")  
    print(f"{'=' * W}")  
  
    print(f"\n  Running {args.n_boot} bootstrap resamples ...",  
          end="", flush=True)  
    boot_aris = bootstrap_ari(X, true_labels, args.n_boot,  
                              seed=args.seed)  
    print(f" done.")  
  
    print(f"  Bootstrap ARI: mean={np.mean(boot_aris):.3f}, "  
          f"std={np.std(boot_aris, ddof=1):.3f}")  
    print(f"  Bootstrap ARI: median={np.median(boot_aris):.3f}")  
    print(f"  Bootstrap ARI: 5th={np.percentile(boot_aris, 5):.3f}, "  
          f"95th={np.percentile(boot_aris, 95):.3f}")  
    print(f"  Fraction with ARI > 0.3: "  
          f"{np.mean(boot_aris > 0.3):.1%}")  
    print(f"  Fraction with ARI > 0.5: "  
          f"{np.mean(boot_aris > 0.5):.1%}")  
  
    # ================================================================  
    # SECTION 4: LEAVE-ONE-PAIR-OUT  
    # ================================================================  
    print(f"\n{'=' * W}")  
    print(f"  SECTION 4: LEAVE-ONE-PAIR-OUT")  
    print(f"{'=' * W}")  
  
    loo_results = leave_one_out_pairs(X, true_labels, pair_labels,  
                                      seed=args.seed)  
  
    # Full ARI for reference  
    km_full = KMeans(n_clusters=2, n_init=50, random_state=args.seed)  
    pred_full = km_full.fit_predict(X)  
    full_ari = adjusted_rand_score(true_labels, pred_full)  
  
    print(f"\n  Full ARI (all pairs): {full_ari:.3f}")  
    print(f"\n  {'Pair dropped':<14} {'ARI':>7} {'Change':>8}")  
    print(f"  {'-' * 32}")  
    for plabel, ari in sorted(loo_results, key=lambda x: x[1]):  
        change = ari - full_ari  
        print(f"  {plabel:<14} {ari:>7.3f} {change:>+8.3f}")  
  
    # ================================================================  
    # SECTION 5: SINGLE-PAIR CLUSTERING  
    # ================================================================  
    print(f"\n{'=' * W}")  
    print(f"  SECTION 5: SINGLE-PAIR CLUSTERING POWER")  
    print(f"{'=' * W}")  
  
    sp_results = single_pair_clustering(  
        X_raw, true_labels, pair_labels, seed=args.seed)  
  
    print(f"\n  {'Pair':<14} {'ARI(median)':>12} {'ARI(kmeans)':>12}")  
    print(f"  {'-' * 40}")  
    for plabel, ari_med, ari_km in sorted(  
            sp_results, key=lambda x: -x[2]):  
        print(f"  {plabel:<14} {ari_med:>12.3f} {ari_km:>12.3f}")  
  
    # ================================================================  
    # SECTION 6: PCA SUMMARY  
    # ================================================================  
    print(f"\n{'=' * W}")  
    print(f"  SECTION 6: PCA SUMMARY")  
    print(f"{'=' * W}")  
  
    pca = PCA()  
    X_pca = pca.fit_transform(X)  
  
    print(f"\n  Explained variance ratio:")  
    cumvar = 0  
    for i, ev in enumerate(pca.explained_variance_ratio_):  
        cumvar += ev  
        print(f"    PC{i + 1}: {ev:.3f} (cumulative: {cumvar:.3f})")  
        if cumvar > 0.95:  
            break  
  
    # PC1 alone  
    pc1 = X_pca[:, 0]  
    pred_pc1 = (pc1 > np.median(pc1)).astype(int)  
    ari_pc1 = adjusted_rand_score(true_labels, pred_pc1)  
    print(f"\n  PC1 median-split ARI: {ari_pc1:.3f}")  
  
    # PC1 loadings  
    print(f"\n  PC1 loadings (pair contributions):")  
    loadings = pca.components_[0]  
    order = np.argsort(-np.abs(loadings))  
    for idx in order:  
        print(f"    {pair_labels[idx]:<14} {loadings[idx]:>+7.3f}")  
  
if __name__ == "__main__":  
    main()  
