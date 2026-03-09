import { useState, useCallback } from 'react';
import './DocumentUpload.css';

const ACCEPTED_TYPES = '.pdf,.docx,.doc,.txt,.md';
const MAX_SIZE_MB = 10;

export default function DocumentUpload({ onAnalyze, isLoading }) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileError, setFileError] = useState('');

  const validateFile = (file) => {
    if (!file) return 'No file selected.';
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'doc', 'txt', 'md'].includes(ext)) {
      return `Unsupported file type ".${ext}". Please upload PDF, DOCX, or TXT files.`;
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File is too large. Maximum size is ${MAX_SIZE_MB} MB.`;
    }
    return '';
  };

  const handleFile = useCallback((file) => {
    const error = validateFile(file);
    setFileError(error);
    if (!error) {
      setSelectedFile(file);
    } else {
      setSelectedFile(null);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleInputChange = (e) => {
    const file = e.target.files[0];
    if (file) handleFile(file);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedFile && !isLoading) {
      onAnalyze(selectedFile);
    }
  };

  return (
    <div className="upload-container">
      <form onSubmit={handleSubmit}>
        <div
          className={`drop-zone ${dragOver ? 'drag-over' : ''} ${selectedFile ? 'has-file' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input').click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && document.getElementById('file-input').click()}
          aria-label="Drop zone for document upload"
        >
          <input
            id="file-input"
            type="file"
            accept={ACCEPTED_TYPES}
            onChange={handleInputChange}
            className="hidden-input"
            aria-label="File input"
          />
          <div className="drop-zone-content">
            {selectedFile ? (
              <>
                <span className="file-icon">📄</span>
                <p className="selected-file-name">{selectedFile.name}</p>
                <p className="file-size">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </p>
              </>
            ) : (
              <>
                <span className="upload-icon">☁️</span>
                <p className="drop-text">
                  Drag & drop your document here
                </p>
                <p className="drop-subtext">or click to browse</p>
                <p className="supported-formats">
                  Supported formats: PDF, DOCX, TXT, MD (max {MAX_SIZE_MB} MB)
                </p>
              </>
            )}
          </div>
        </div>

        {fileError && (
          <p className="error-message" role="alert">{fileError}</p>
        )}

        <button
          type="submit"
          className="analyze-btn"
          disabled={!selectedFile || isLoading || !!fileError}
        >
          {isLoading ? (
            <span className="btn-loading">
              <span className="spinner" aria-hidden="true" />
              Analyzing…
            </span>
          ) : (
            '🔍 Analyse Document'
          )}
        </button>
      </form>
    </div>
  );
}
