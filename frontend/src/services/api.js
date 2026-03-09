const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Upload a document file and return the AI/ML analysis result.
 * @param {File} file
 * @returns {Promise<Object>}
 */
export async function analyzeDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/api/documents/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let message = `Server error: ${response.status}`;
    try {
      const errorData = await response.json();
      message = errorData.detail || message;
    } catch {
      // ignore JSON parse error
    }
    throw new Error(message);
  }

  return response.json();
}

/**
 * Check API health.
 * @returns {Promise<{status: string}>}
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE}/api/documents/health`);
  return response.json();
}
