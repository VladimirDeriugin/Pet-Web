import { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import AnalysisResults from './components/AnalysisResults';
import { analyzeDocument } from './services/api';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async (file) => {
    setIsLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await analyzeDocument(file);
      setResult(data);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError('');
  };

  return (
    <div className="app-wrapper">
      <header className="app-header">
        <h1 className="app-title">🧠 DocAnalyser</h1>
        <p className="app-subtitle">
          AI/ML-powered document analysis — keywords, summaries, sentiment &amp; more
        </p>
      </header>

      <main className="app-main">
        {!result ? (
          <section className="upload-section">
            <DocumentUpload onAnalyze={handleAnalyze} isLoading={isLoading} />
            {error && (
              <div className="global-error" role="alert">
                ⚠️ {error}
              </div>
            )}
          </section>
        ) : (
          <section className="results-section-outer">
            <button className="back-btn" onClick={handleReset}>
              ← Analyse another document
            </button>
            <AnalysisResults result={result} />
          </section>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by FastAPI · React · scikit-learn · NLTK · TextBlob</p>
      </footer>
    </div>
  );
}

export default App;
