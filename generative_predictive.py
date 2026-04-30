#!/usr/bin/env python3  
"""  
Generative Model + Predictive Validation  
=========================================  
Test 1: Beta-Binomial Mixture Model (latent regime discovery)  
Test 2: Predictive validation (train/test splits)  
"""  
  
import re  
import math  
import sys  
import warnings  
from collections import Counter, defaultdict  
  
import numpy as np  
from scipy import stats as sp_stats  
from scipy.special import gammaln, digamma, betaln  
from sklearn.metrics import (  
    adjusted_rand_score,  
    normalized_mutual_info_score,  
    confusion_matrix,  
    accuracy_score,  
    log_loss,  
)  
from sklearn.model_selection import StratifiedKFold  
  
warnings.filterwarnings("ignore", category=RuntimeWarning)  
  
# ====================================================================  
# EVA TOKENIZER  
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
PAIR_LABELS = [p[2] for p in CONFUSABLE_PAIRS]  
  
  
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
# PARSER + LANGUAGE MAP (same as before)  
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
# PRECOMPUTE FOLIO-LEVEL COUNTS  
# ====================================================================  
  
def folio_sort_key(fid):  
    m = re.search(r'(\d+)', fid)  
    num = int(m.group(1)) if m else 0  
    return (num, fid)  
  
  
def precompute_folio_data(words_by_folio, folio_lang):  
    """  
    Returns:  
      folio_order: list of folio IDs  
      pair_counts: dict[fid][pair_label] -> (count_a, count_b)  
      true_labels: dict[fid] -> 0 (A) or 1 (B)  
    """  
    folio_order = sorted(  
        [f for f in words_by_folio if f in folio_lang],  
        key=folio_sort_key)  
  
    target_tokens = set()  
    for sa, sb, _ in CONFUSABLE_PAIRS:  
        target_tokens.add(sa)  
        target_tokens.add(sb)  
  
    pair_counts = {}  
    for fid in folio_order:  
        token_counts = Counter()  
        for w in words_by_folio[fid]:  
            for t in eva_tokenize(w):  
                if t in target_tokens:  
                    token_counts[t] += 1  
  
        pair_counts[fid] = {}  
        for sa, sb, label in CONFUSABLE_PAIRS:  
            ca = token_counts[sa]  
            cb = token_counts[sb]  
            pair_counts[fid][label] = (ca, cb)  
  
    true_labels = {f: (0 if folio_lang[f] == "A" else 1)  
                   for f in folio_order}  
  
    return folio_order, pair_counts, true_labels  
  
  
# ====================================================================  
# TEST 1: BETA-BINOMIAL MIXTURE MODEL  
# ====================================================================  
  
def beta_binom_logpmf(k, n, alpha, beta_param):  
    """Log probability of k successes in n trials under  
    Beta-Binomial(alpha, beta)."""  
    if n == 0:  
        return 0.0  
    return (gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1)  
            + betaln(k + alpha, n - k + beta_param)  
            - betaln(alpha, beta_param))  
  
  
class BetaBinomialMixture:  
    """  
    Mixture of K regimes, each with independent Beta-Binomial  
    distributions for each pair.  
  
    Parameters per regime per pair: (alpha, beta)  
    Global parameters: mixing weights pi_k  
    """  
  
    def __init__(self, K, n_pairs, seed=42):  
        self.K = K  
        self.n_pairs = n_pairs  
        self.rng = np.random.default_rng(seed)  
  
        # Initialize parameters  
        self.log_pi = np.log(np.ones(K) / K)  
        self.alpha = self.rng.uniform(0.5, 5.0, (K, n_pairs))  
        self.beta = self.rng.uniform(0.5, 5.0, (K, n_pairs))  
  
    def _e_step(self, data):  
        """  
        data: list of dicts, each dict maps pair_index ->  
              (count_a, count_b) or None if missing  
        Returns: responsibilities (N x K)  
        """  
        N = len(data)  
        log_resp = np.zeros((N, self.K))  
  
        for i, folio_data in enumerate(data):  
            for k in range(self.K):  
                log_p = self.log_pi[k]  
                for j in range(self.n_pairs):  
                    if j in folio_data:  
                        ca, cb = folio_data[j]  
                        n = ca + cb  
                        if n > 0:  
                            log_p += beta_binom_logpmf(  
                                ca, n, self.alpha[k, j],  
                                self.beta[k, j])  
                log_resp[i, k] = log_p  
  
        # Normalize  
        log_max = log_resp.max(axis=1, keepdims=True)  
        log_resp -= log_max  
        resp = np.exp(log_resp)  
        resp_sum = resp.sum(axis=1, keepdims=True)  
        resp_sum = np.maximum(resp_sum, 1e-300)  
        resp /= resp_sum  
  
        # Log-likelihood  
        ll = np.sum(np.log(np.maximum(  
            np.exp(log_resp).sum(axis=1), 1e-300)) +  
            log_max.ravel())  
  
        return resp, ll  
  
    def _m_step(self, data, resp):  
        """Update parameters given responsibilities."""  
        N = len(data)  
  
        # Update mixing weights  
        Nk = resp.sum(axis=0) + 1e-10  
        self.log_pi = np.log(Nk / Nk.sum())  
  
        # Update alpha, beta for each regime and pair  
        # Using method of moments with weighted counts  
        for k in range(self.K):  
            for j in range(self.n_pairs):  
                # Weighted statistics  
                weighted_ratios = []  
                weighted_ns = []  
                total_weight = 0  
  
                for i, folio_data in enumerate(data):  
                    if j not in folio_data:  
                        continue  
                    ca, cb = folio_data[j]  
                    n = ca + cb  
                    if n == 0:  
                        continue  
                    w = resp[i, k]  
                    r = ca / n  
                    weighted_ratios.append((w, r, n))  
                    total_weight += w  
  
                if total_weight < 1e-10 or len(weighted_ratios) < 2:  
                    continue  
  
                # Weighted mean and variance  
                w_sum = sum(w for w, r, n in weighted_ratios)  
                mean_r = sum(w * r for w, r, n in weighted_ratios) / w_sum  
                var_r = sum(w * (r - mean_r) ** 2  
                            for w, r, n in weighted_ratios) / w_sum  
  
                # Mean n  
                mean_n = sum(w * n for w, r, n in weighted_ratios) / w_sum  
  
                # Method of moments for Beta-Binomial  
                # Var(X/n) = p(1-p)(1 + (n-1)*rho) / n  
                # where rho = 1/(alpha+beta+1)  
                mean_r = np.clip(mean_r, 0.01, 0.99)  
                var_r = max(var_r, 1e-6)  
  
                # Estimate concentration  
                binom_var = mean_r * (1 - mean_r) / max(mean_n, 1)  
                if var_r > binom_var and mean_n > 1:  
                    rho = (var_r / (mean_r * (1 - mean_r)) -   
                           1 / mean_n) / (1 - 1 / mean_n)  
                    rho = np.clip(rho, 0.001, 0.999)  
                    concentration = (1 - rho) / rho  
                else:  
                    concentration = 100.0  
  
                concentration = np.clip(concentration, 0.1, 1000.0)  
  
                self.alpha[k, j] = mean_r * concentration  
                self.beta[k, j] = (1 - mean_r) * concentration  
  
    def fit(self, data, max_iter=200, tol=1e-6, n_restarts=5):  
        """Fit with multiple restarts."""  
        best_ll = -np.inf  
        best_params = None  
  
        for restart in range(n_restarts):  
            # Re-initialize  
            self.log_pi = np.log(np.ones(self.K) / self.K)  
            self.alpha = self.rng.uniform(  
                0.5, 5.0, (self.K, self.n_pairs))  
            self.beta = self.rng.uniform(  
                0.5, 5.0, (self.K, self.n_pairs))  
  
            prev_ll = -np.inf  
            for it in range(max_iter):  
                resp, ll = self._e_step(data)  
                self._m_step(data, resp)  
  
                if abs(ll - prev_ll) < tol:  
                    break  
                prev_ll = ll  
  
            if ll > best_ll:  
                best_ll = ll  
                best_params = (  
                    self.log_pi.copy(),  
                    self.alpha.copy(),  
                    self.beta.copy(),  
                    resp.copy(),  
                    ll  
                )  
  
        self.log_pi, self.alpha, self.beta, resp, ll = best_params  
        return resp, ll  
  
    def predict(self, data):  
        """Return MAP assignments."""  
        resp, ll = self._e_step(data)  
        return np.argmax(resp, axis=1), resp, ll  
  
    def bic(self, data, ll):  
        N = len(data)  
        n_params = (self.K - 1) + 2 * self.K * self.n_pairs  
        return n_params * np.log(N) - 2 * ll  
  
    def aic(self, data, ll):  
        n_params = (self.K - 1) + 2 * self.K * self.n_pairs  
        return 2 * n_params - 2 * ll  
  
    def regime_summary(self):  
        """Return mean ratio for each regime and pair."""  
        means = self.alpha / (self.alpha + self.beta)  
        return means  
  
  
def prepare_mixture_data(folio_order, pair_counts):  
    """Convert to list of dicts for mixture model."""  
    data = []  
    for fid in folio_order:  
        folio_data = {}  
        for j, (sa, sb, label) in enumerate(CONFUSABLE_PAIRS):  
            ca, cb = pair_counts[fid][label]  
            if ca + cb >= MIN_TOKENS:  
                folio_data[j] = (ca, cb)  
        data.append(folio_data)  
    return data  
  
  
def run_mixture_analysis(folio_order, pair_counts, true_labels,  
                         max_k=6, seed=42):  
    """Run Beta-Binomial mixture for k=1..max_k."""  
    data = prepare_mixture_data(folio_order, pair_counts)  
    n_pairs = len(CONFUSABLE_PAIRS)  
    true_arr = np.array([true_labels[f] for f in folio_order])  
  
    results = []  
  
    for k in range(1, max_k + 1):  
        print(f"    k={k} ...", end="", flush=True)  
        model = BetaBinomialMixture(k, n_pairs, seed=seed)  
        resp, ll = model.fit(data, n_restarts=10)  
        assignments = np.argmax(resp, axis=1)  
  
        bic = model.bic(data, ll)  
        aic = model.aic(data, ll)  
  
        if k >= 2:  
            ari = adjusted_rand_score(true_arr, assignments)  
            nmi = normalized_mutual_info_score(  
                true_arr, assignments)  
  
            # Best accuracy  
            cm = confusion_matrix(true_arr, assignments)  
            # Try all label permutations for small k  
            from itertools import permutations  
            best_acc = 0  
            for perm in permutations(range(k)):  
                remapped = np.array([perm[a] for a in assignments])  
                # For k>2, map to binary  
                if k == 2:  
                    acc = max(  
                        accuracy_score(true_arr, remapped),  
                        accuracy_score(true_arr, 1 - remapped))  
                else:  
                    # Map each cluster to majority true label  
                    mapped = np.zeros_like(assignments)  
                    for c in range(k):  
                        mask = assignments == c  
                        if mask.sum() > 0:  
                            mapped[mask] = np.round(  
                                np.mean(true_arr[mask]))  
                    acc = accuracy_score(true_arr, mapped)  
                best_acc = max(best_acc, acc)  
                if k > 4:  
                    break  # Too many permutations  
        else:  
            ari = float('nan')  
            nmi = float('nan')  
            best_acc = float('nan')  
  
        means = model.regime_summary()  
  
        results.append({  
            'k': k,  
            'll': ll,  
            'bic': bic,  
            'aic': aic,  
            'ari': ari,  
            'nmi': nmi,  
            'accuracy': best_acc,  
            'assignments': assignments,  
            'responsibilities': resp,  
            'means': means,  
            'model': model,  
        })  
        print(f" LL={ll:.1f}, BIC={bic:.1f}"  
              f"{f', ARI={ari:.3f}' if k >= 2 else ''}")  
  
    return results  
  
  
# ====================================================================  
# TEST 2: PREDICTIVE VALIDATION  
# ====================================================================  
  
class BetaBinomialClassifier:  
    """  
    Supervised classifier: learn Beta-Binomial parameters for  
    each class (A/B) and each pair from training data, then  
    predict held-out folios.  
    """  
  
    def __init__(self, n_classes=2, n_pairs=11):  
        self.n_classes = n_classes  
        self.n_pairs = n_pairs  
        self.alpha = np.ones((n_classes, n_pairs))  
        self.beta_param = np.ones((n_classes, n_pairs))  
        self.log_prior = np.log(  
            np.ones(n_classes) / n_classes)  
  
    def fit(self, data, labels):  
        """  
        data: list of dicts (pair_index -> (ca, cb))  
        labels: array of class labels (0 or 1)  
        """  
        for c in range(self.n_classes):  
            mask = labels == c  
            self.log_prior[c] = np.log(  
                max(mask.sum(), 1) / len(labels))  
  
            for j in range(self.n_pairs):  
                # Collect counts for this class and pair  
                cas, cbs = [], []  
                for i in np.where(mask)[0]:  
                    if j in data[i]:  
                        ca, cb = data[i][j]  
                        if ca + cb > 0:  
                            cas.append(ca)  
                            cbs.append(cb)  
  
                if len(cas) < 3:  
                    self.alpha[c, j] = 1.0  
                    self.beta_param[c, j] = 1.0  
                    continue  
  
                cas = np.array(cas, dtype=float)  
                cbs = np.array(cbs, dtype=float)  
                ns = cas + cbs  
                rs = cas / ns  
  
                mean_r = np.clip(np.mean(rs), 0.01, 0.99)  
                var_r = max(np.var(rs, ddof=1), 1e-6)  
                mean_n = np.mean(ns)  
  
                binom_var = mean_r * (1 - mean_r) / max(mean_n, 1)  
                if var_r > binom_var and mean_n > 1:  
                    rho = (var_r / (mean_r * (1 - mean_r)) -  
                           1 / mean_n) / (1 - 1 / mean_n)  
                    rho = np.clip(rho, 0.001, 0.999)  
                    conc = (1 - rho) / rho  
                else:  
                    conc = 100.0  
  
                conc = np.clip(conc, 0.1, 1000.0)  
                self.alpha[c, j] = mean_r * conc  
                self.beta_param[c, j] = (1 - mean_r) * conc  
  
    def predict_proba(self, data):  
        """Return (N x n_classes) probability matrix."""  
        N = len(data)  
        log_probs = np.zeros((N, self.n_classes))  
  
        for i, folio_data in enumerate(data):  
            for c in range(self.n_classes):  
                log_p = self.log_prior[c]  
                for j in range(self.n_pairs):  
                    if j in folio_data:  
                        ca, cb = folio_data[j]  
                        n = ca + cb  
                        if n > 0:  
                            log_p += beta_binom_logpmf(  
                                ca, n, self.alpha[c, j],  
                                self.beta_param[c, j])  
                log_probs[i, c] = log_p  
  
        # Normalize  
        log_max = log_probs.max(axis=1, keepdims=True)  
        log_probs -= log_max  
        probs = np.exp(log_probs)  
        probs /= probs.sum(axis=1, keepdims=True)  
        return probs  
  
    def predict(self, data):  
        probs = self.predict_proba(data)  
        return np.argmax(probs, axis=1)  
  
    def score(self, data, labels):  
        pred = self.predict(data)  
        return accuracy_score(labels, pred)  
  
  
def run_cross_validation(folio_order, pair_counts, true_labels,  
                         n_folds=5, n_repeats=20, seed=42):  
    """Repeated stratified k-fold cross-validation."""  
    data = prepare_mixture_data(folio_order, pair_counts)  
    true_arr = np.array([true_labels[f] for f in folio_order])  
    n_pairs = len(CONFUSABLE_PAIRS)  
  
    all_accs = []  
    all_aris = []  
    all_log_losses = []  
  
    rng = np.random.default_rng(seed)  
  
    for rep in range(n_repeats):  
        skf = StratifiedKFold(  
            n_splits=n_folds, shuffle=True,  
            random_state=int(rng.integers(1e9)))  
  
        for train_idx, test_idx in skf.split(  
                np.zeros(len(data)), true_arr):  
            train_data = [data[i] for i in train_idx]  
            train_labels = true_arr[train_idx]  
            test_data = [data[i] for i in test_idx]  
            test_labels = true_arr[test_idx]  
  
            clf = BetaBinomialClassifier(2, n_pairs)  
            clf.fit(train_data, train_labels)  
  
            pred = clf.predict(test_data)  
            proba = clf.predict_proba(test_data)  
  
            acc = accuracy_score(test_labels, pred)  
            ari = adjusted_rand_score(test_labels, pred)  
  
            # Clip probabilities for log_loss  
            proba = np.clip(proba, 1e-10, 1 - 1e-10)  
            ll = log_loss(test_labels, proba)  
  
            all_accs.append(acc)  
            all_aris.append(ari)  
            all_log_losses.append(ll)  
  
    return {  
        'accs': np.array(all_accs),  
        'aris': np.array(all_aris),  
        'log_losses': np.array(all_log_losses),  
    }  
  
  
def run_spatial_split(folio_order, pair_counts, true_labels):  
    """Train on first half of manuscript, predict second half."""  
    data = prepare_mixture_data(folio_order, pair_counts)  
    true_arr = np.array([true_labels[f] for f in folio_order])  
    n = len(folio_order)  
    n_pairs = len(CONFUSABLE_PAIRS)  
  
    mid = n // 2  
  
    results = {}  
  
    # Forward: train on first half, test on second  
    train_data = data[:mid]  
    train_labels = true_arr[:mid]  
    test_data = data[mid:]  
    test_labels = true_arr[mid:]  
  
    clf = BetaBinomialClassifier(2, n_pairs)  
    clf.fit(train_data, train_labels)  
    pred = clf.predict(test_data)  
    proba = clf.predict_proba(test_data)  
  
    results['forward'] = {  
        'acc': accuracy_score(test_labels, pred),  
        'ari': adjusted_rand_score(test_labels, pred),  
        'n_train': mid,  
        'n_test': n - mid,  
        'train_folios': folio_order[:mid],  
        'test_folios': folio_order[mid:],  
        'pred': pred,  
        'true': test_labels,  
        'proba': proba,  
    }  
  
    # Backward: train on second half, test on first  
    train_data = data[mid:]  
    train_labels = true_arr[mid:]  
    test_data = data[:mid]  
    test_labels = true_arr[:mid]  
  
    clf = BetaBinomialClassifier(2, n_pairs)  
    clf.fit(train_data, train_labels)  
    pred = clf.predict(test_data)  
    proba = clf.predict_proba(test_data)  
  
    results['backward'] = {  
        'acc': accuracy_score(test_labels, pred),  
        'ari': adjusted_rand_score(test_labels, pred),  
        'n_train': n - mid,  
        'n_test': mid,  
        'train_folios': folio_order[mid:],  
        'test_folios': folio_order[:mid],  
        'pred': pred,  
        'true': test_labels,  
        'proba': proba,  
    }  
  
    # Even/odd folios  
    even_idx = list(range(0, n, 2))  
    odd_idx = list(range(1, n, 2))  
  
    train_data = [data[i] for i in even_idx]  
    train_labels = true_arr[even_idx]  
    test_data = [data[i] for i in odd_idx]  
    test_labels = true_arr[odd_idx]  
  
    clf = BetaBinomialClassifier(2, n_pairs)  
    clf.fit(train_data, train_labels)  
    pred = clf.predict(test_data)  
  
    results['even_odd'] = {  
        'acc': accuracy_score(test_labels, pred),  
        'ari': adjusted_rand_score(test_labels, pred),  
        'n_train': len(even_idx),  
        'n_test': len(odd_idx),  
    }  
  
    return results  
  
  
def run_ratio_prediction(folio_order, pair_counts, true_labels,  
                         n_folds=5, n_repeats=10, seed=42):  
    """  
    Predict pair RATIOS on held-out folios given their A/B label.  
    Measures whether the A/B label carries predictive information  
    about character statistics on unseen folios.  
    """  
    true_arr = np.array([true_labels[f] for f in folio_order])  
    n_pairs = len(CONFUSABLE_PAIRS)  
    rng = np.random.default_rng(seed)  
  
    # Build ratio matrix  
    ratios = np.full((len(folio_order), n_pairs), np.nan)  
    for i, fid in enumerate(folio_order):  
        for j, (sa, sb, label) in enumerate(CONFUSABLE_PAIRS):  
            ca, cb = pair_counts[fid][label]  
            total = ca + cb  
            if total >= MIN_TOKENS:  
                ratios[i, j] = ca / total  
  
    all_mse_model = []  
    all_mse_null = []  
  
    for rep in range(n_repeats):  
        skf = StratifiedKFold(  
            n_splits=n_folds, shuffle=True,  
            random_state=int(rng.integers(1e9)))  
  
        for train_idx, test_idx in skf.split(  
                np.zeros(len(folio_order)), true_arr):  
            for j in range(n_pairs):  
                # Train: compute mean ratio per class  
                train_mask_A = (true_arr[train_idx] == 0)  
                train_mask_B = (true_arr[train_idx] == 1)  
  
                train_A_vals = ratios[train_idx[train_mask_A], j]  
                train_B_vals = ratios[train_idx[train_mask_B], j]  
  
                train_A_vals = train_A_vals[~np.isnan(train_A_vals)]  
                train_B_vals = train_B_vals[~np.isnan(train_B_vals)]  
  
                if len(train_A_vals) < 3 or len(train_B_vals) < 3:  
                    continue  
  
                mean_A = np.mean(train_A_vals)  
                mean_B = np.mean(train_B_vals)  
                mean_all = np.mean(np.concatenate(  
                    [train_A_vals, train_B_vals]))  
  
                # Test: predict using class mean vs global mean  
                for i in test_idx:  
                    if np.isnan(ratios[i, j]):  
                        continue  
                    true_ratio = ratios[i, j]  
                    pred_model = mean_A if true_arr[i] == 0  else mean_B  
                    pred_null = mean_all  
  
                    all_mse_model.append(  
                        (true_ratio - pred_model) ** 2)  
                    all_mse_null.append(  
                        (true_ratio - pred_null) ** 2)  
  
    mse_model = np.mean(all_mse_model)  
    mse_null = np.mean(all_mse_null)  
    r_squared = 1 - mse_model / mse_null  
  
    return {  
        'mse_model': mse_model,  
        'mse_null': mse_null,  
        'r_squared': r_squared,  
        'n_predictions': len(all_mse_model),  
    }  
  
  
# ====================================================================  
# PERMUTATION BASELINE FOR PREDICTIVE VALIDATION  
# ====================================================================  
  
def permutation_cv(folio_order, pair_counts, true_labels,  
                   n_perm=500, n_folds=5, seed=42):  
    """Permute labels and run CV to get null distribution."""  
    data = prepare_mixture_data(folio_order, pair_counts)  
    true_arr = np.array([true_labels[f] for f in folio_order])  
    n_pairs = len(CONFUSABLE_PAIRS)  
    rng = np.random.default_rng(seed)  
  
    # Observed  
    skf = StratifiedKFold(  
        n_splits=n_folds, shuffle=True, random_state=42)  
    obs_accs = []  
    for train_idx, test_idx in skf.split(  
            np.zeros(len(data)), true_arr):  
        clf = BetaBinomialClassifier(2, n_pairs)  
        clf.fit([data[i] for i in train_idx],  
                true_arr[train_idx])  
        pred = clf.predict([data[i] for i in test_idx])  
        obs_accs.append(accuracy_score(true_arr[test_idx], pred))  
    obs_acc = np.mean(obs_accs)  
  
    # Null distribution  
    null_accs = []  
    for p in range(n_perm):  
        perm_labels = true_arr.copy()  
        rng.shuffle(perm_labels)  
  
        skf = StratifiedKFold(  
            n_splits=n_folds, shuffle=True,  
            random_state=int(rng.integers(1e9)))  
        fold_accs = []  
        for train_idx, test_idx in skf.split(  
                np.zeros(len(data)), perm_labels):  
            clf = BetaBinomialClassifier(2, n_pairs)  
            clf.fit([data[i] for i in train_idx],  
                    perm_labels[train_idx])  
            pred = clf.predict([data[i] for i in test_idx])  
            fold_accs.append(  
                accuracy_score(perm_labels[test_idx], pred))  
        null_accs.append(np.mean(fold_accs))  
  
        if (p + 1) % 100 == 0:  
            print(f"\r    Permutation CV: {p + 1}/{n_perm}",  
                  end="", flush=True)  
    print(f"\r    Permutation CV: {n_perm}/{n_perm}    ")  
  
    null_accs = np.array(null_accs)  
    p_value = np.mean(null_accs >= obs_acc)  
  
    return obs_acc, null_accs, p_value  
  
  
# ====================================================================  
# MAIN  
# ====================================================================  
  
def main():  
    import argparse  
    ap = argparse.ArgumentParser()  
    ap.add_argument("ivtff", help="Path to IVTFF file")  
    ap.add_argument("--n-perm", type=int, default=500)  
    ap.add_argument("--n-cv-repeats", type=int, default=20)  
    ap.add_argument("--seed", type=int, default=42)  
    args = ap.parse_args()  
  
    W = 76  
  
    print(f"\n{'=' * W}")  
    print(f"  GENERATIVE MODEL + PREDICTIVE VALIDATION")  
    print(f"{'=' * W}")  
  
    # ---- Parse ----  
    print(f"\n  Parsing {args.ivtff} ...", end="", flush=True)  
    words_by_folio = parse_ivtff(args.ivtff)  
    folio_lang = build_folio_language_map()  
    print(f" done.")  
  
    folio_order, pair_counts, true_labels = precompute_folio_data(  
        words_by_folio, folio_lang)  
  
    n_folios = len(folio_order)  
    n_A = sum(1 for f in folio_order if true_labels[f] == 0)  
    n_B = n_folios - n_A  
    print(f"  Folios: {n_folios} (A={n_A}, B={n_B})")  
  
    # ================================================================  
    # TEST 1: BETA-BINOMIAL MIXTURE  
    # ================================================================  
    print(f"\n{'=' * W}")  
    print(f"  TEST 1: BETA-BINOMIAL MIXTURE MODEL")  
    print(f"{'=' * W}")  
  
    print(f"\n  Fitting mixtures k=1..6:")  
    mix_results = run_mixture_analysis(  
        folio_order, pair_counts, true_labels,  
        max_k=6, seed=args.seed)  
  
    # Summary table  
    print(f"\n  {'k':>3} {'LL':>10} {'BIC':>10} {'AIC':>10} "  
          f"{'ARI':>7} {'Acc':>7}")  
    print(f"  {'-' * 52}")  
    for r in mix_results:  
        ari_str = f"{r['ari']:.3f}" if not math.isnan(r['ari'])  else "  --"  
        acc_str = f"{r['accuracy']:.1%}" if not math.isnan(  
            r['accuracy']) else "  --"  
        print(f"  {r['k']:>3} {r['ll']:>10.1f} {r['bic']:>10.1f} "  
              f"{r['aic']:>10.1f} {ari_str:>7} {acc_str:>7}")  
  
    best_bic = min(mix_results, key=lambda x: x['bic'])  
    print(f"\n  Best k by BIC: {best_bic['k']}")  
  
    # Show k=2 regime profiles  
    k2 = [r for r in mix_results if r['k'] == 2][0]  
    means = k2['means']  
  
    # Determine which regime is A-like  
    assignments = k2['assignments']  
    true_arr = np.array([true_labels[f] for f in folio_order])  
    regime0_A_frac = np.mean(true_arr[assignments == 0] == 0)  
    if regime0_A_frac < 0.5:  
        means = means[::-1]  
        assignments = 1 - assignments  
  
    print(f"\n  k=2 Regime profiles (mean ratio per pair):")  
    print(f"    {'Pair':<12} {'Regime A':>10} {'Regime B':>10} "  
          f"{'Diff':>10}")  
    print(f"    {'-' * 44}")  
    for j, (sa, sb, label) in enumerate(CONFUSABLE_PAIRS):  
        diff = abs(means[0, j] - means[1, j])  
        print(f"    {label:<12} {means[0, j]:>10.3f} "  
              f"{means[1, j]:>10.3f} {diff:>10.3f}")  
  
    # Posterior uncertainty  
    resp = k2['responsibilities']  
    confident = np.max(resp, axis=1) > 0.9  
    print(f"\n  Posterior confidence:")  
    print(f"    Folios with P(regime) > 0.9: "  
          f"{confident.sum()}/{n_folios} ({confident.mean():.1%})")  
    print(f"    Mean max posterior: {np.max(resp, axis=1).mean():.3f}")  
  
    # Misclassified at k=2  
    mismatches = []  
    for i, fid in enumerate(folio_order):  
        if assignments[i] != true_labels[fid]:  
            true_str = "A" if true_labels[fid] == 0 else "B"  
            pred_str = "A" if assignments[i] == 0 else "B"  
            max_p = np.max(resp[i])  
            mismatches.append((fid, true_str, pred_str, max_p))  
  
    if mismatches:  
        print(f"\n  Misclassified folios (k=2 mixture):")  
        print(f"    {'Folio':<10} {'Currier':>8} {'Mixture':>8} "  
              f"{'Confidence':>11}")  
        print(f"    {'-' * 40}")  
        for fid, ts, ps, mp in sorted(  
                mismatches, key=lambda x: x[3]):  
            print(f"    {fid:<10} {ts:>8} {ps:>8} {mp:>11.3f}")  
  
    # Show k=3 if it has better BIC  
    if best_bic['k'] >= 3:  
        k3 = [r for r in mix_results if r['k'] == 3]  
        if k3:  
            k3 = k3[0]  
            print(f"\n  k=3 regime assignments vs Currier:")  
            for c in range(3):  
                mask = k3['assignments'] == c  
                n_c = mask.sum()  
                if n_c > 0:  
                    frac_A = np.mean(true_arr[mask] == 0)  
                    print(f"    Regime {c}: {n_c} folios "  
                          f"({frac_A:.0%} A, {1 - frac_A:.0%} B)")  
  
    # ================================================================  
    # TEST 2: PREDICTIVE VALIDATION  
    # ================================================================  
    print(f"\n{'=' * W}")  
    print(f"  TEST 2: PREDICTIVE VALIDATION")  
    print(f"{'=' * W}")  
  
    # ---- 2a: Cross-validated label prediction ----  
    print(f"\n  2a. Cross-validated label prediction "  
          f"({args.n_cv_repeats}x 5-fold):")  
    cv_results = run_cross_validation(  
        folio_order, pair_counts, true_labels,  
        n_folds=5, n_repeats=args.n_cv_repeats, seed=args.seed)  
  
    print(f"    Accuracy: {cv_results['accs'].mean():.1%} "  
          f"± {cv_results['accs'].std():.1%}")  
    print(f"    ARI:      {cv_results['aris'].mean():.3f} "  
          f"± {cv_results['aris'].std():.3f}")  
    print(f"    Log-loss: {cv_results['log_losses'].mean():.3f} "  
          f"± {cv_results['log_losses'].std():.3f}")  
  
    # ---- 2b: Spatial splits ----  
    print(f"\n  2b. Spatial split prediction:")  
    spatial = run_spatial_split(  
        folio_order, pair_counts, true_labels)  
  
    for split_name, split_data in spatial.items():  
        print(f"    {split_name:>12}: acc={split_data['acc']:.1%}, "  
              f"ARI={split_data['ari']:.3f} "  
              f"(train={split_data['n_train']}, "  
              f"test={split_data['n_test']})")  
  
    # Show misclassified for forward split  
    if 'pred' in spatial['forward']:  
        fwd = spatial['forward']  
        mismatches = []  
        for i, fid in enumerate(fwd['test_folios']):  
            if fwd['pred'][i] != fwd['true'][i]:  
                true_str = "A" if fwd['true'][i] == 0 else "B"  
                pred_str = "A" if fwd['pred'][i] == 0 else "B"  
                conf = max(fwd['proba'][i])  
                mismatches.append((fid, true_str, pred_str, conf))  
  
        if mismatches:  
            print(f"\n    Forward split misclassified:")  
            print(f"      {'Folio':<10} {'True':>6} {'Pred':>6} "  
                  f"{'Conf':>8}")  
            print(f"      {'-' * 34}")  
            for fid, ts, ps, c in mismatches:  
                print(f"      {fid:<10} {ts:>6} {ps:>6} {c:>8.3f}")  
  
    # ---- 2c: Ratio prediction ----  
    print(f"\n  2c. Ratio prediction (does A/B label predict "  
          f"character ratios?):")  
    ratio_pred = run_ratio_prediction(  
        folio_order, pair_counts, true_labels,  
        n_folds=5, n_repeats=10, seed=args.seed)  
  
    print(f"    MSE (A/B model): {ratio_pred['mse_model']:.5f}")  
    print(f"    MSE (null/mean): {ratio_pred['mse_null']:.5f}")  
    print(f"    R²:              {ratio_pred['r_squared']:.3f}")  
    print(f"    N predictions:   {ratio_pred['n_predictions']}")  
  
    # ---- 2d: Permutation baseline ----  
    print(f"\n  2d. Permutation baseline for CV accuracy:")  
    obs_acc, null_accs, perm_p = permutation_cv(  
        folio_order, pair_counts, true_labels,  
        n_perm=args.n_perm, seed=args.seed)  
  
    print(f"    Observed CV acc: {obs_acc:.1%}")  
    print(f"    Null mean:       {null_accs.mean():.1%}")  
    print(f"    Null std:        {null_accs.std():.1%}")  
    print(f"    Null 95th:       {np.percentile(null_accs, 95):.1%}")  
    print(f"    Null max:        {null_accs.max():.1%}")  
    print(f"    p-value:         {perm_p:.4f}")  
    if perm_p == 0:  
        print(f"    (p < {1 / args.n_perm:.1e})")  
  
    # ================================================================  
    # SYNTHESIS  
    # ================================================================  
    print(f"\n\n{'=' * W}")  
    print(f"  SYNTHESIS")  
    print(f"{'=' * W}")  
  
    k2_ari = k2['ari'] if k2 else float('nan')  
    cv_acc = cv_results['accs'].mean()  
    cv_ari = cv_results['aris'].mean()  
    r2 = ratio_pred['r_squared']  
  
    print(f"""  
  GENERATIVE MODEL (Beta-Binomial Mixture):  
    k=2 ARI with Currier:  {k2_ari:.3f}  
    Best k by BIC:         {best_bic['k']}  
    Confident assignments: {confident.sum()}/{n_folios}  
  
  PREDICTIVE VALIDATION:  
    CV accuracy:           {cv_acc:.1%} (p={perm_p:.4f})  
    CV ARI:                {cv_ari:.3f}  
    Spatial forward acc:   {spatial['forward']['acc']:.1%}  
    Spatial backward acc:  {spatial['backward']['acc']:.1%}  
    Ratio R²:              {r2:.3f}  
""")  
  
  
if __name__ == "__main__":  
    main()  
