import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Search for similar projects based on input parameters
 * @param {Object} params - Search parameters
 * @param {number} [params.sq_ft] - Square footage
 * @param {number} [params.total_hours] - Total hours (Engineering + Drafting + Manager)
 * @param {number} [params.total_fee] - Total fee (SD + DD + CD)
 * @param {number} [params.total_spent] - Total spent (SD + DD + CD)
 * @param {number} [params.max_results] - Maximum number of results (1-10)
 * @returns {Promise<Object>} Search results
 */
export async function searchProjects(params) {
  const response = await api.post('/search', params);
  return response.data;
}

/**
 * Get statistics about the indexed data
 * @returns {Promise<Object>} Statistics
 */
export async function getStats() {
  const response = await api.get('/stats');
  return response.data;
}

/**
 * Health check
 * @returns {Promise<Object>} Health status
 */
export async function healthCheck() {
  const response = await api.get('/health');
  return response.data;
}

/**
 * Get details for a specific project
 * @param {string} projectId - Project ID
 * @returns {Promise<Object>} Project details
 */
export async function getProject(projectId) {
  const response = await api.get(`/project/${projectId}`);
  return response.data;
}

/**
 * Trigger data ingestion
 * @param {Object} options - Ingestion options
 * @param {boolean} [options.clear_existing] - Clear existing data first
 * @param {number} [options.year] - Only ingest specific year
 * @returns {Promise<Object>} Ingestion stats
 */
export async function triggerIngest(options = {}) {
  const response = await api.post('/ingest', options);
  return response.data;
}

export default api;
