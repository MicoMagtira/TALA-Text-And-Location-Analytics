"""NLP analytics for TALA.

Mirrors the reference Text Analytics Explorer feature set and the user's
NLP.ipynb pipeline: frequency + word clouds, n-grams, VADER polarity + NRC
emotions, LDA topic modeling + topic stability, RAKE keywords, spaCy noun/POS
extraction, co-occurrence, readability metrics, and TF-IDF K-Means themes.

Heavy/optional dependencies (nrclex, spacy model, rake-nltk, textstat) are
imported lazily and degrade gracefully so a missing model never crashes a page.
"""
from __future__ import annotations

from collections import Counter

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
@st.cache_data(show_spinner=False)
def top_ngrams(corpus: tuple[str, ...], ngram: tuple[int, int] = (2, 2),
               top_n: int = 20, min_df: int = 2) -> pd.DataFrame:
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


@st.cache_data(show_spinner=False)
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


@st.cache_data(show_spinner=False)
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


@st.cache_data(show_spinner=False)
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
@st.cache_data(show_spinner=False)
def lda_topics(corpus: tuple[str, ...], n_topics: int = 5, n_top_words: int = 10,
               seed: int = 42, min_df: int = 3):
    docs = [d for d in corpus if d.strip()]
    if len(docs) < n_topics:
        return None
    vec = CountVectorizer(min_df=min_df, max_df=0.9)
    X = vec.fit_transform(docs)
    terms = vec.get_feature_names_out()
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=seed,
                                    learning_method="batch", max_iter=20)
    doc_topic = lda.fit_transform(X)
    topics = []
    for k, comp in enumerate(lda.components_):
        idx = comp.argsort()[::-1][:n_top_words]
        topics.append({"topic": k, "words": list(terms[idx]),
                       "weights": list(comp[idx] / comp.sum())})
    return {"topics": topics, "doc_topic": doc_topic, "docs": docs}


def _topic_word_sets(corpus, n_topics, seed, n_top_words=15, min_df=3):
    res = lda_topics(corpus, n_topics, n_top_words, seed, min_df)
    if res is None:
        return []
    return [set(t["words"]) for t in res["topics"]]


@st.cache_data(show_spinner=False)
def topic_stability(corpus: tuple[str, ...], n_topics: int = 5,
                    seeds: tuple[int, ...] = (0, 1, 2)) -> pd.DataFrame:
    """Re-run LDA under different seeds; score topic-set agreement between the
    first run and each other via best-match Jaccard and cosine (bag overlap)."""
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
# Keywords (RAKE) + Noun/POS extraction (spaCy)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
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


def _ensure_nltk():
    import nltk

    for pkg, path in [("stopwords", "corpora/stopwords"),
                      ("punkt", "tokenizers/punkt"),
                      ("punkt_tab", "tokenizers/punkt_tab")]:
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(pkg, quiet=True)
            except Exception:
                pass


@st.cache_resource(show_spinner="Loading spaCy model…")
def _spacy():
    import spacy

    try:
        return spacy.load("en_core_web_sm", disable=["parser", "ner"])
    except Exception:
        return None


def spacy_available() -> bool:
    return _spacy() is not None


@st.cache_data(show_spinner=False)
def extract_nouns(texts: tuple[str, ...], top_n: int = 25):
    nlp = _spacy()
    if nlp is None:
        return pd.DataFrame(), pd.DataFrame()
    common, proper = Counter(), Counter()
    sample = list(texts)[:4000]  # cap for responsiveness on 12k rows
    for doc in nlp.pipe((str(t) for t in sample), batch_size=200):
        for tok in doc:
            if tok.is_stop or not tok.is_alpha or len(tok) < 3:
                continue
            if tok.pos_ == "NOUN":
                common[tok.lemma_.lower()] += 1
            elif tok.pos_ == "PROPN":
                proper[tok.text] += 1
    to_df = lambda c, col: pd.DataFrame(c.most_common(top_n), columns=[col, "count"])
    return to_df(common, "noun"), to_df(proper, "proper_noun")


@st.cache_data(show_spinner=False)
def pos_proportions(texts: tuple[str, ...]) -> pd.DataFrame:
    nlp = _spacy()
    if nlp is None:
        return pd.DataFrame()
    counts = Counter()
    sample = list(texts)[:4000]
    for doc in nlp.pipe((str(t) for t in sample), batch_size=200):
        for tok in doc:
            if tok.is_alpha:
                counts[tok.pos_] += 1
    total = sum(counts.values()) or 1
    df = pd.DataFrame([(p, n, 100 * n / total) for p, n in counts.most_common()],
                      columns=["pos", "count", "percent"])
    return df


# ---------------------------------------------------------------------------
# Co-occurrence
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def cooccurrence(corpus: tuple[str, ...], top_terms: int = 15,
                 min_df: int = 3) -> pd.DataFrame:
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
@st.cache_data(show_spinner=False)
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
@st.cache_data(show_spinner=False)
def tfidf_kmeans(corpus: tuple[str, ...], k: int = 4, seed: int = 42,
                 top_terms: int = 10):
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
    coords = PCA(n_components=2, random_state=seed).fit_transform(X.toarray())
    sizes = pd.Series(labels).value_counts().sort_index()
    return {"labels": labels, "top_terms": top, "coords": coords,
            "sizes": sizes, "docs": docs}
