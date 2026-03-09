import './AnalysisResults.css';

const SENTIMENT_EMOJI = {
  positive: '😊',
  negative: '😟',
  neutral: '😐',
};

const ENTITY_COLORS = {
  PERSON: '#4fc3f7',
  ORGANIZATION: '#aed581',
  GPE: '#ffb74d',
  LOCATION: '#ce93d8',
  FACILITY: '#80deea',
  GSP: '#f48fb1',
};

function SentimentBadge({ sentiment, score }) {
  return (
    <span className={`sentiment-badge sentiment-${sentiment}`}>
      {SENTIMENT_EMOJI[sentiment] || '🔍'} {sentiment}
      <span className="sentiment-score">({score > 0 ? '+' : ''}{score.toFixed(3)})</span>
    </span>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="stat-card">
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

function KeywordTag({ keyword, score }) {
  const opacity = 0.5 + Math.min(score * 5, 0.5);
  return (
    <span className="keyword-tag" style={{ opacity }}>
      {keyword}
    </span>
  );
}

function EntityBadge({ text, label }) {
  const color = ENTITY_COLORS[label] || '#90caf9';
  return (
    <span className="entity-badge" style={{ borderColor: color, color }}>
      {text}
      <span className="entity-label">{label}</span>
    </span>
  );
}

export default function AnalysisResults({ result }) {
  if (!result) return null;

  const { filename, file_type, language, stats, keywords, summary, sentiment,
          sentiment_score, entities, full_text } = result;

  return (
    <div className="results-container">
      <div className="results-header">
        <h2 className="results-title">📊 Analysis Results</h2>
        <div className="doc-meta">
          <span className="meta-badge">{file_type}</span>
          <span className="meta-badge lang">{language.toUpperCase()}</span>
          <SentimentBadge sentiment={sentiment} score={sentiment_score} />
        </div>
        <p className="filename">{filename}</p>
      </div>

      {/* Statistics */}
      <section className="results-section">
        <h3>📈 Statistics</h3>
        <div className="stats-grid">
          <StatCard label="Words" value={stats.word_count.toLocaleString()} />
          <StatCard label="Sentences" value={stats.sentence_count.toLocaleString()} />
          <StatCard label="Paragraphs" value={stats.paragraph_count.toLocaleString()} />
          <StatCard label="Characters" value={stats.character_count.toLocaleString()} />
          <StatCard label="Reading time" value={`${stats.reading_time_minutes} min`} />
        </div>
      </section>

      {/* Summary */}
      {summary && (
        <section className="results-section">
          <h3>📝 Summary</h3>
          <p className="summary-text">{summary}</p>
        </section>
      )}

      {/* Keywords */}
      {keywords.length > 0 && (
        <section className="results-section">
          <h3>🔑 Keywords</h3>
          <div className="keywords-list">
            {keywords.map((kw) => (
              <KeywordTag key={kw.keyword} keyword={kw.keyword} score={kw.score} />
            ))}
          </div>
        </section>
      )}

      {/* Named Entities */}
      {entities.length > 0 && (
        <section className="results-section">
          <h3>🏷️ Named Entities</h3>
          <div className="entities-list">
            {entities.map((e, i) => (
              <EntityBadge key={`${e.text}-${i}`} text={e.text} label={e.label} />
            ))}
          </div>
        </section>
      )}

      {/* Document Preview */}
      {full_text && (
        <section className="results-section">
          <h3>📄 Document Preview</h3>
          <pre className="text-preview">{full_text}</pre>
        </section>
      )}
    </div>
  );
}
