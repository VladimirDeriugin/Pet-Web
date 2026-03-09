"""AI/ML analysis service for extracted document text.

Features
--------
* Document statistics (word/sentence/paragraph counts, reading time)
* Keyword extraction via TF-IDF
* Extractive summarisation (top-N sentences by TF-IDF score)
* Sentiment analysis via TextBlob
* Basic named-entity recognition (NLTK chunker)
* Language detection via langdetect
"""

import re
import logging
import math
from typing import List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy NLTK bootstrap
# ---------------------------------------------------------------------------

_NLTK_READY = False


def _ensure_nltk() -> None:
    global _NLTK_READY
    if _NLTK_READY:
        return
    import nltk  # noqa: PLC0415

    for resource in (
        "punkt",
        "punkt_tab",
        "stopwords",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
        "maxent_ne_chunker",
        "maxent_ne_chunker_tab",
        "words",
    ):
        try:
            nltk.download(resource, quiet=True)
        except Exception:  # noqa: BLE001
            pass
    _NLTK_READY = True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compute_stats(text: str) -> dict:
    """Return basic statistics about *text*."""
    _ensure_nltk()
    import nltk  # noqa: PLC0415

    sentences = nltk.sent_tokenize(text)
    words = re.findall(r"\b\w+\b", text)
    paragraphs = [p for p in re.split(r"\n{2,}", text) if p.strip()]

    word_count = len(words)
    reading_time = round(word_count / 200, 2)  # ~200 wpm average reader

    return {
        "word_count": word_count,
        "sentence_count": len(sentences),
        "paragraph_count": max(len(paragraphs), 1),
        "character_count": len(text),
        "reading_time_minutes": reading_time,
    }


def extract_keywords(text: str, top_n: int = 10) -> List[dict]:
    """Return the *top_n* keywords extracted via TF-IDF from *text*."""
    _ensure_nltk()
    from nltk.corpus import stopwords  # noqa: PLC0415
    from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: PLC0415

    stop_words = set(stopwords.words("english"))

    # Split text into "documents" (sentences) so TF-IDF has variance to work with
    import nltk  # noqa: PLC0415

    sentences = nltk.sent_tokenize(text)
    if len(sentences) < 2:
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if not sentences:
        return []

    try:
        vectorizer = TfidfVectorizer(
            stop_words=list(stop_words),
            ngram_range=(1, 2),
            max_features=200,
            min_df=1,
        )
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()

        # Average TF-IDF score across all sentences
        avg_scores = tfidf_matrix.mean(axis=0).A1
        scored = sorted(
            zip(feature_names, avg_scores), key=lambda x: x[1], reverse=True
        )

        return [
            {"keyword": kw, "score": round(float(score), 4)}
            for kw, score in scored[:top_n]
            if score > 0
        ]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Keyword extraction failed: %s", exc)
        return []


def summarize(text: str, num_sentences: int = 5) -> str:
    """Return an extractive summary of *text* using sentence TF-IDF scores."""
    _ensure_nltk()
    import nltk  # noqa: PLC0415
    from nltk.corpus import stopwords  # noqa: PLC0415

    sentences = nltk.sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text.strip()

    stop_words = set(stopwords.words("english"))

    def _score_sentence(sentence: str) -> float:
        words = re.findall(r"\b\w+\b", sentence.lower())
        return sum(1 for w in words if w not in stop_words and len(w) > 2)

    scored = [(s, _score_sentence(s)) for s in sentences]
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:num_sentences]
    # Re-order by original position
    top_set = {s for s, _ in top}
    ordered = [s for s in sentences if s in top_set]
    return " ".join(ordered)


def analyze_sentiment(text: str) -> dict:
    """Return sentiment label and polarity score using TextBlob."""
    try:
        from textblob import TextBlob  # noqa: PLC0415

        polarity = TextBlob(text).sentiment.polarity
        if polarity > 0.1:
            label = "positive"
        elif polarity < -0.1:
            label = "negative"
        else:
            label = "neutral"
        return {"sentiment": label, "sentiment_score": round(polarity, 4)}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Sentiment analysis failed: %s", exc)
        return {"sentiment": "neutral", "sentiment_score": 0.0}


def detect_language(text: str) -> str:
    """Detect the primary language of *text*."""
    try:
        from langdetect import detect  # noqa: PLC0415

        return detect(text[:2000])
    except Exception:  # noqa: BLE001
        return "unknown"


def extract_entities(text: str) -> List[dict]:
    """Extract named entities using NLTK chunker."""
    _ensure_nltk()
    try:
        import nltk  # noqa: PLC0415

        tokens = nltk.word_tokenize(text[:5000])
        pos_tags = nltk.pos_tag(tokens)
        tree = nltk.ne_chunk(pos_tags, binary=False)

        entities: List[dict] = []
        seen: set = set()
        for subtree in tree:
            if hasattr(subtree, "label"):
                entity_text = " ".join(word for word, tag in subtree.leaves())
                label = subtree.label()
                key = f"{entity_text}|{label}"
                if key not in seen:
                    seen.add(key)
                    entities.append({"text": entity_text, "label": label})
        return entities[:30]
    except Exception as exc:  # noqa: BLE001
        logger.warning("NER failed: %s", exc)
        return []


def analyze_document(text: str) -> dict:
    """Run the full analysis pipeline on *text* and return a result dict."""
    stats = compute_stats(text)
    keywords = extract_keywords(text)
    summary = summarize(text)
    sentiment_result = analyze_sentiment(text)
    language = detect_language(text)
    entities = extract_entities(text)

    return {
        **stats,
        "keywords": keywords,
        "summary": summary,
        **sentiment_result,
        "language": language,
        "entities": entities,
    }
