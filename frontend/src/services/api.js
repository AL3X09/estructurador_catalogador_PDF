import axios from 'axios';

// URL base del backend FastAPI en desarrollo
const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

export default {
  /**
   * Sube un archivo PDF al backend para ser procesado.
   * @param {File} file El archivo PDF a procesar.
   * @returns {Promise} Promesa con la respuesta del servidor.
   */
  extractPdf(file) {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/pdfs/extract', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * Obtiene la lista de PDFs procesados junto con su catálogo.
   * @returns {Promise} Promesa con la lista de documentos.
   */
  listPdfs() {
    return api.get('/pdfs');
  },

  /**
   * Verifica si el backend está en línea.
   * @returns {Promise} Promesa con el estado del backend.
   */
  checkHealth() {
    return api.get('/health');
  },
};
