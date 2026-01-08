import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Search for similar projects based on input parameters
 * @param {Object} params - Search parameters
 * @param {number} [params.total_sheets] - Total number of sheets
 * @param {number} [params.engineering_hrs] - Total engineering hours
 * @param {number} [params.drafting_hrs] - Total drafting hours
 * @param {number} [params.manager_hrs] - Total manager/reviewer hours
 * @param {number} [params.cd_fee] - CD fee
 * @param {number} [params.ca_fee] - CA fee
 * @param {number} [params.sq_ft] - Square footage
 * @param {number} [params.total_spent_cd] - Total dollars spent on CD
 * @param {number} [params.total_spent_ca] - Total dollars spent on CA
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
