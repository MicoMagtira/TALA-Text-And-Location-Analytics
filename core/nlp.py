"""NLP analytics for TALA.

Mirrors the reference Text Analytics Explorer feature set and the user's
NLP.ipynb pipeline: frequency + word clouds, n-grams, VADER polarity + NRC
emotions, LDA topic modeling + topic stability, RAKE keywords, noun/POS
extraction, co-occurrence, readability metrics, and TF-IDF K-Means themes.

Heavy/optional dependencies (sklearn, nrclex, rake-nltk, textstat, the NLTK
tagger) are imported lazily inside the functions that use them and degrade
gracefully, so a page only pays for the models it actually runs and a missing
corpus never crashes a page.
"""
from __future__ import annotations

import re
from collections import Counter

import numpy as np
import pandas as pd
import streamlit as st

from . import preprocess

VADER_THRESHOLD = 0.05


# ---------------------------------------------------------------------------
# Frequencies & word clouds
# ---------------------------------------------------------------------------
def word_frequencies(tokens: list[str], top_n: int = 20) -> pd.DataFrame:
    counts = Counter(tokens)
    common = counts.most_common(top_n)
    return pd.DataFrame(common, columns=["word", "count"])


def make_wordcloud(freqs: dict[str, int], colormap_name: str = "NU Navy",
                   width: int = 900, height: int = 450):
    from wordcloud import WordCloud

    from .viz import sequential_cmap

    if not freqs:
        return None
    wc = WordCloud(width=width, height=height, background_color="white",
                   colormap=sequential_cmap(colormap_name), prefer_horizontal=0.9)
    return wc.generate_from_frequencies(freqs)


# ---------------------------------------------------------------------------
# N-grams
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Counting n-grams…")
def top_ngrams(corpus: tuple[str, ...], ngram: tuple[int, int] = (2, 2),
               top_n: int = 20, min_df: int = 2) -> pd.DataFrame:
    from sklearn.feature_extraction.text import CountVectorizer

    docs = [d for d in corpus if d.strip()]
    if not docs:
        return pd.DataFrame(columns=["ngram", "count"])
    vec = CountVectorizer(ngram_range=ngram, min_df=min_df)
    try:
        X = vec.fit_transform(docs)
    except ValueError:
        return pd.DataFrame(columns=["ngram", "count"])
    sums = np.asarray(X.sum(axis=0)).ravel()
    terms = vec.get_feature_names_out()
    order = sums.argsort()[::-1][:top_n]
    return pd.DataFrame({"ngram": terms[order], "count": sums[order].astype(int)})


# ---------------------------------------------------------------------------
# Sentiment (VADER) + Emotions (NRC)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _vader():
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    return SentimentIntensityAnalyzer()


@st.cache_data(show_spinner="Scoring sentiment with VADER…")
def vader_sentiment(texts: tuple[str, ...],
                    threshold: float = VADER_THRESHOLD) -> pd.DataFrame:
    sia = _vader()
    rows = []
    for t in texts:
        c = sia.polarity_scores(str(t))["compound"]
        label = "positive" if c >= threshold else "negative" if c <= -threshold else "neutral"
        rows.append({"text": t, "compound": c, "label": label})
    return pd.DataFrame(rows)


def _nrc():
    """Return a bundled-lexicon NRCLex instance, or None if unavailable.

    We use load_token_list() rather than load_raw_text() so nrclex never touches
    TextBlob/WordNet — it matches our own cleaned tokens straight against the
    bundled NRC lexicon, which keeps the feature offline-safe and fast.
    """
    try:
        from nrclex import NRCLex

        return NRCLex()  # default arg resolves to the packaged nrc_en.json
    except Exception:
        return None


_NRC_ORDER = ["anticipation", "trust", "joy", "surprise", "anger",
              "fear", "sadness", "disgust", "positive", "negative"]


@st.cache_data(show_spinner="Matching the NRC emotion lexicon…")
def nrc_emotions(texts: tuple[str, ...]) -> pd.DataFrame:
    """Aggregate NRC emotion + pos/neg counts across the corpus."""
    nrc = _nrc()
    if nrc is None:
        return pd.DataFrame()
    tokens: list[str] = []
    for t in texts:
        tokens.extend(preprocess.clean_text(t).split())
    if not tokens:
        return pd.DataFrame()
    nrc.load_token_list(tokens)
    scores = nrc.raw_emotion_scores
    data = [(e, int(scores.get(e, 0))) for e in _NRC_ORDER]
    df = pd.DataFrame(data, columns=["emotion", "count"])
    return df[df["count"] > 0].reset_index(drop=True)


@st.cache_data(show_spinner="Sorting polarity word clouds…")
def polarity_word_frequencies(tokens: tuple[str, ...], top_n: int = 100):
    """Split unique tokens into NRC positive / negative buckets (for word clouds)."""
    nrc = _nrc()
    if nrc is None:
        return {}, {}
    counts = Counter(tokens)
    nrc.load_token_list(list(counts))
    pos: dict[str, int] = {}
    neg: dict[str, int] = {}
    for word, emotions in nrc.affect_dict.items():
        if "positive" in emotions:
            pos[word] = counts[word]
        if "negative" in emotions:
            neg[word] = counts[word]
    trim = lambda d: dict(sorted(d.items(), key=lambda kv: kv[1], reverse=True)[:top_n])
    return trim(pos), trim(neg)


# ---------------------------------------------------------------------------
# Topic modeling (LDA) + stability
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Fitting the LDA topic model…")
def _lda_fit(corpus: tuple[str, ...], n_topics: int, seed: int, min_df: int):
    """Fit LDA and cache the model itself, keyed only on what changes the fit.

    ``n_top_words`` is deliberately *not* a parameter here. It only decides how
    many words get displayed, but when it was part of the cache key, nudging the
    "Words per topic" slider threw away the model and refit from scratch — tens of
    seconds for a purely cosmetic change. It also meant the stability check (which
    asks for 15 words) could never reuse the model the charts had already fit at
    10 words.

    Solver settings: max_iter 20->10 and max_doc_update_iter 100->25 roughly halve
    the fit on this corpus (~43s -> ~22s locally) while topic word-sets still agree
    with the slower settings at 0.79 best-match Jaccard and perplexity moves only
    228.7 -> 232.0. n_jobs is left at 1 on purpose: the parallel E-step is ~4x
    faster, but each joblib worker re-imports numpy/scipy/sklearn, and ~150 MB per
    worker is not affordable in a 1 GB container.
    """
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import CountVectorizer

    docs = [d for d in corpus if d.strip()]
    if len(docs) < n_topics:
        return None
    vec = CountVectorizer(min_df=min_df, max_df=0.9)
    X = vec.fit_transform(docs)
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=seed,
                                    learning_method="batch", max_iter=10,
                                    max_doc_update_iter=25, n_jobs=1)
    doc_topic = lda.fit_transform(X)
    return {"components": lda.components_, "terms": vec.get_feature_names_out(),
            "doc_topic": doc_topic, "docs": docs}


def lda_topics(corpus: tuple[str, ...], n_topics: int = 5, n_top_words: int = 10,
               seed: int = 42, min_df: int = 3):
    """Top-N words per topic. Slicing only — the fit behind it is cached."""
    fit = _lda_fit(corpus, n_topics, seed, min_df)
    if fit is None:
        return None
    terms = fit["terms"]
    topics = []
    for k, comp in enumerate(fit["components"]):
        idx = comp.argsort()[::-1][:n_top_words]
        topics.append({"topic": k, "words": list(terms[idx]),
                       "weights": list(comp[idx] / comp.sum())})
    return {"topics": topics, "doc_topic": fit["doc_topic"], "docs": fit["docs"]}


def _topic_word_sets(corpus, n_topics, seed, n_top_words=15, min_df=3):
    res = lda_topics(corpus, n_topics, n_top_words, seed, min_df)
    if res is None:
        return []
    return [set(t["words"]) for t in res["topics"]]


@st.cache_data(show_spinner="Re-running LDA across seeds…")
def topic_stability(corpus: tuple[str, ...], n_topics: int = 5,
                    seeds: tuple[int, ...] = (0, 1, 2)) -> pd.DataFrame:
    """Re-run LDA under different seeds; score topic-set agreement between the
    first run and each other via best-match Jaccard and cosine (bag overlap)."""
    from sklearn.metrics.pairwise import cosine_similarity

    runs = [_topic_word_sets(corpus, n_topics, s) for s in seeds]
    runs = [r for r in runs if r]
    if len(runs) < 2:
        return pd.DataFrame()
    base = runs[0]
    rows = []
    for si, other in zip(seeds[1:], runs[1:]):
        jac, cos = [], []
        for bt in base:
            best_j = max((len(bt & ot) / len(bt | ot)) for ot in other)
            jac.append(best_j)
            # cosine over shared vocabulary bag
            vocab = list(bt | set().union(*other))
            bvec = np.array([1 if w in bt else 0 for w in vocab])
            best_c = max(
                float(cosine_similarity([bvec], [np.array([1 if w in ot else 0 for w in vocab])])[0][0])
                for ot in other)
            cos.append(best_c)
        rows.append({"seed_pair": f"{seeds[0]} vs {si}",
                     "mean_jaccard": np.mean(jac), "mean_cosine": np.mean(cos)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Keywords (RAKE) + Noun/POS extraction (NLTK)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Extracting RAKE keywords…")
def rake_keywords(texts: tuple[str, ...], top_n: int = 25) -> pd.DataFrame:
    try:
        from rake_nltk import Rake
    except Exception:
        return pd.DataFrame()
    _ensure_nltk()
    r = Rake()
    r.extract_keywords_from_text(" . ".join(str(t) for t in texts))
    ranked = r.get_ranked_phrases_with_scores()[:top_n]
    return pd.DataFrame(ranked, columns=["score", "keyword"])[["keyword", "score"]]


def _ensure_nltk(extra: tuple[tuple[str, str], ...] = ()) -> None:
    """Make sure the NLTK data packages we need are present.

    NLTK renamed the English tagger in 3.8.2, so both names are attempted and a
    miss on either is tolerated."""
    import nltk

    wanted = [("stopwords", "corpora/stopwords"),
              ("punkt", "tokenizers/punkt"),
              ("punkt_tab", "tokenizers/punkt_tab")] + list(extra)
    for pkg, path in wanted:
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(pkg, quiet=True)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# POS tagging (NLTK averaged perceptron)
# ---------------------------------------------------------------------------
# Penn Treebank -> coarse universal tags, so the UI keeps speaking NOUN/PROPN/
# VERB/ADJ regardless of the tagger underneath.
_PTB_TO_UNIVERSAL = {
    "NN": "NOUN", "NNS": "NOUN",
    "NNP": "PROPN", "NNPS": "PROPN",
    "VB": "VERB", "VBD": "VERB", "VBG": "VERB", "VBN": "VERB",
    "VBP": "VERB", "VBZ": "VERB", "MD": "VERB",
    "JJ": "ADJ", "JJR": "ADJ", "JJS": "ADJ",
    "RB": "ADV", "RBR": "ADV", "RBS": "ADV", "WRB": "ADV",
    "PRP": "PRON", "PRP$": "PRON", "WP": "PRON", "WP$": "PRON",
    "DT": "DET", "PDT": "DET", "WDT": "DET",
    "IN": "ADP", "TO": "PART", "RP": "PART", "POS": "PART",
    "CC": "CCONJ", "CD": "NUM", "UH": "INTJ", "EX": "PRON", "FW": "X",
}

# Lightweight sentence segmentation — avoids pulling the punkt model just to
# find sentence boundaries in short, social-media-style comments.
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

_TAGGER_PKGS = (("averaged_perceptron_tagger", "taggers/averaged_perceptron_tagger"),
                ("averaged_perceptron_tagger_eng",
                 "taggers/averaged_perceptron_tagger_eng"))


@st.cache_resource(show_spinner="Loading the POS tagger…")
def _pos_backend():
    """Return (tokenizer, tagger, lemmatizer) or None if NLTK data is unavailable.

    Uses TreebankWordTokenizer directly rather than ``word_tokenize`` so no punkt
    sentence model is needed for this path. The WordNet lemmatizer is optional —
    without it, nouns are counted in surface form."""
    try:
        import nltk
        from nltk.tokenize.treebank import TreebankWordTokenizer
    except Exception:
        return None

    _ensure_nltk(_TAGGER_PKGS)
    tokenizer = TreebankWordTokenizer()
    try:  # fail fast if the tagger data really did not land
        nltk.pos_tag(["test"])
    except Exception:
        return None

    lemmatizer = None
    try:
        from nltk.stem import WordNetLemmatizer

        _ensure_nltk((("wordnet", "corpora/wordnet"),))
        lemmatizer = WordNetLemmatizer()
        lemmatizer.lemmatize("tests")  # touch it once; raises if data is missing
    except Exception:
        lemmatizer = None
    return tokenizer, nltk.pos_tag, lemmatizer


def pos_available() -> bool:
    return _pos_backend() is not None


@st.cache_data(show_spinner="Tagging parts of speech…")
def _pos_analysis(texts: tuple[str, ...], top_n: int = 25, sample: int = 4000) -> dict:
    """Tag the corpus once and derive every POS-based view from that single pass.

    Both the noun ranking and the POS distribution read this, so viewing both
    costs one tagging pass instead of two. Only the small aggregates are cached,
    never the token stream."""
    backend = _pos_backend()
    if backend is None:
        return {}
    tokenize, pos_tag, lemmatizer = backend
    stops = preprocess.english_stopwords()

    common, pos_counts = Counter(), Counter()
    # Proper nouns are tallied in two buckets. A capitalized word that only ever
    # appears at the start of a sentence ("Tried…", "Felt…") is almost always a
    # tagger artifact, not a name; one that also appears capitalized mid-sentence
    # is a real proper noun. Only the latter survives, and it keeps its full count.
    proper_initial, proper_mid = Counter(), Counter()

    for text in list(texts)[:sample]:  # cap for responsiveness on 12k rows
        # TreebankWordTokenizer assumes sentence-level input — it only splits a
        # trailing period at the very end of the string. Segmenting first is what
        # makes both the tags and the sentence-initial test correct.
        for sentence in _SENT_SPLIT.split(str(text)):
            tokens = tokenize.tokenize(sentence)
            if not tokens:
                continue
            for idx, (word, tag) in enumerate(pos_tag(tokens)):
                universal = _PTB_TO_UNIVERSAL.get(tag, "X")
                if not word.isalpha():
                    continue
                pos_counts[universal] += 1
                if len(word) < 3 or word.lower() in stops:
                    continue
                if universal == "NOUN":
                    lemma = word.lower()
                    if lemmatizer is not None:
                        lemma = lemmatizer.lemmatize(lemma)
                    common[lemma] += 1
                elif universal == "PROPN":
                    (proper_initial if idx == 0 else proper_mid)[word] += 1

    proper = Counter({w: c + proper_initial[w] for w, c in proper_mid.items()})

    total = sum(pos_counts.values()) or 1
    to_df = lambda c, col: pd.DataFrame(c.most_common(top_n), columns=[col, "count"])
    return {
        "nouns": to_df(common, "noun"),
        "proper": to_df(proper, "proper_noun"),
        "pos": pd.DataFrame(
            [(p, n, 100 * n / total) for p, n in pos_counts.most_common()],
            columns=["pos", "count", "percent"]),
    }


def extract_nouns(texts: tuple[str, ...], top_n: int = 25):
    res = _pos_analysis(texts, top_n)
    if not res:
        return pd.DataFrame(), pd.DataFrame()
    return res["nouns"], res["proper"]


def pos_proportions(texts: tuple[str, ...]) -> pd.DataFrame:
    res = _pos_analysis(texts)
    return res.get("pos", pd.DataFrame())


# ---------------------------------------------------------------------------
# Co-occurrence
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Building the co-occurrence matrix…")
def cooccurrence(corpus: tuple[str, ...], top_terms: int = 15,
                 min_df: int = 3) -> pd.DataFrame:
    from sklearn.feature_extraction.text import CountVectorizer

    docs = [d for d in corpus if d.strip()]
    if not docs:
        return pd.DataFrame()
    vec = CountVectorizer(min_df=min_df, binary=True)
    try:
        X = vec.fit_transform(docs)
    except ValueError:
        return pd.DataFrame()
    terms = vec.get_feature_names_out()
    freq = np.asarray(X.sum(axis=0)).ravel()
    keep = freq.argsort()[::-1][:top_terms]
    Xk = X[:, keep]
    co = (Xk.T @ Xk).toarray()
    np.fill_diagonal(co, 0)
    labels = terms[keep]
    return pd.DataFrame(co, index=labels, columns=labels)


# ---------------------------------------------------------------------------
# Readability / linguistic metrics
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Computing readability metrics…")
def readability(texts: tuple[str, ...]) -> dict:
    joined = " ".join(str(t) for t in texts)
    words = joined.split()
    n_words = len(words)
    n_types = len({w.lower() for w in words})
    ttr = n_types / n_words if n_words else 0
    herdan = (np.log(n_types) / np.log(n_words)) if n_words > 1 else 0
    metrics = {"Total words": n_words, "Unique words (types)": n_types,
               "Type-Token Ratio": round(ttr, 4), "Herdan's C": round(float(herdan), 4)}
    try:
        import textstat

        metrics.update({
            "Flesch Reading Ease": round(textstat.flesch_reading_ease(joined), 2),
            "Flesch-Kincaid Grade": round(textstat.flesch_kincaid_grade(joined), 2),
            "Gunning Fog": round(textstat.gunning_fog(joined), 2),
            "SMOG Index": round(textstat.smog_index(joined), 2),
            "Avg. sentence length": round(textstat.avg_sentence_length(joined), 2),
        })
    except Exception:
        pass
    return metrics


# ---------------------------------------------------------------------------
# TF-IDF K-Means themes (from NLP.ipynb)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Clustering themes (TF-IDF + K-Means)…")
def tfidf_kmeans(corpus: tuple[str, ...], k: int = 4, seed: int = 42,
                 top_terms: int = 10):
    from sklearn.cluster import KMeans
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer

    docs = [d for d in corpus if d.strip()]
    if len(docs) < k:
        return None
    vec = TfidfVectorizer(ngram_range=(1, 2), max_df=0.9, min_df=3, max_features=1200)
    X = vec.fit_transform(docs)
    km = KMeans(n_clusters=k, n_init=10, random_state=seed)
    labels = km.fit_predict(X)
    terms = vec.get_feature_names_out()
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    top = {c: [terms[i] for i in order_centroids[c, :top_terms]] for c in range(k)}
    # TruncatedSVD, not PCA: it consumes the sparse TF-IDF matrix directly.
    # PCA required X.toarray(), which densified 12k x 1200 float64 into a ~115 MB
    # allocation — the single largest transient in the app, on a 1 GB box.
    coords = TruncatedSVD(n_components=2, random_state=seed).fit_transform(X)
    sizes = pd.Series(labels).value_counts().sort_index()
    return {"labels": labels, "top_terms": top, "coords": coords,
            "sizes": sizes, "docs": docs}
