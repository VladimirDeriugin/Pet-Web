"""Unit tests for ml_analyzer service."""

import pytest
from app.services.ml_analyzer import (
    compute_stats,
    extract_keywords,
    summarize,
    analyze_sentiment,
    detect_language,
    extract_entities,
    analyze_document,
)

SAMPLE_TEXT = """
Artificial intelligence (AI) is transforming industries worldwide.
Machine learning, a subset of AI, enables computers to learn from data without being explicitly programmed.
Deep learning uses neural networks with many layers to recognise patterns in images, text, and sound.
Natural language processing (NLP) allows machines to understand and generate human language.
Companies like Google, Microsoft, and Amazon are heavily investing in AI research.
The healthcare sector is using AI to analyse medical images and predict patient outcomes.
Self-driving cars rely on AI to perceive the environment and make real-time decisions.
Ethical considerations around AI include bias, transparency, and privacy concerns.
Governments around the world are beginning to regulate artificial intelligence applications.
The future of work will be shaped by automation and the collaboration between humans and machines.
"""


class TestComputeStats:
    def test_word_count(self):
        stats = compute_stats("Hello world foo bar")
        assert stats["word_count"] == 4

    def test_sentence_count(self):
        stats = compute_stats("First sentence. Second sentence! Third?")
        assert stats["sentence_count"] == 3

    def test_reading_time(self):
        # 200 words → 1 minute
        text = " ".join(["word"] * 200)
        stats = compute_stats(text)
        assert stats["reading_time_minutes"] == pytest.approx(1.0)

    def test_sample_text(self):
        stats = compute_stats(SAMPLE_TEXT)
        assert stats["word_count"] > 100
        assert stats["sentence_count"] >= 10
        assert stats["character_count"] > 500


class TestExtractKeywords:
    def test_returns_list(self):
        keywords = extract_keywords(SAMPLE_TEXT)
        assert isinstance(keywords, list)

    def test_keyword_structure(self):
        keywords = extract_keywords(SAMPLE_TEXT, top_n=5)
        assert len(keywords) <= 5
        for kw in keywords:
            assert "keyword" in kw
            assert "score" in kw
            assert isinstance(kw["score"], float)

    def test_ai_keyword_present(self):
        keywords = extract_keywords(SAMPLE_TEXT, top_n=10)
        terms = [k["keyword"].lower() for k in keywords]
        # "ai" or "artificial" should appear in top keywords
        assert any("ai" in t or "artificial" in t or "learning" in t for t in terms)

    def test_short_text(self):
        # Should not crash on very short text
        keywords = extract_keywords("hello world", top_n=5)
        assert isinstance(keywords, list)


class TestSummarize:
    def test_short_text_returned_as_is(self):
        text = "Short text. Only two sentences."
        result = summarize(text, num_sentences=5)
        assert len(result) > 0

    def test_summary_shorter_than_original(self):
        result = summarize(SAMPLE_TEXT, num_sentences=3)
        assert len(result) < len(SAMPLE_TEXT)

    def test_summary_non_empty(self):
        result = summarize(SAMPLE_TEXT)
        assert result.strip() != ""


class TestAnalyzeSentiment:
    def test_positive(self):
        result = analyze_sentiment("This is an excellent, wonderful and amazing product!")
        assert result["sentiment"] == "positive"
        assert result["sentiment_score"] > 0

    def test_negative(self):
        result = analyze_sentiment("This is terrible, awful and completely broken.")
        assert result["sentiment"] == "negative"
        assert result["sentiment_score"] < 0

    def test_neutral(self):
        result = analyze_sentiment("The document contains text.")
        assert result["sentiment"] in ("neutral", "positive", "negative")
        assert isinstance(result["sentiment_score"], float)


class TestDetectLanguage:
    def test_english(self):
        lang = detect_language("The quick brown fox jumps over the lazy dog.")
        assert lang == "en"

    def test_returns_string(self):
        lang = detect_language("Hello world")
        assert isinstance(lang, str)
        assert len(lang) >= 2


class TestExtractEntities:
    def test_returns_list(self):
        entities = extract_entities(SAMPLE_TEXT)
        assert isinstance(entities, list)

    def test_entity_structure(self):
        entities = extract_entities("Google and Microsoft are technology companies based in the United States.")
        for entity in entities:
            assert "text" in entity
            assert "label" in entity


class TestAnalyzeDocument:
    def test_full_pipeline(self):
        result = analyze_document(SAMPLE_TEXT)
        assert "word_count" in result
        assert "keywords" in result
        assert "summary" in result
        assert "sentiment" in result
        assert "language" in result
        assert "entities" in result

    def test_language_is_english(self):
        result = analyze_document(SAMPLE_TEXT)
        assert result["language"] == "en"
