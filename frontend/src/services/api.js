import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const dealdeskAPI = {
  ask: async (question, options = {}) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/ask`, {
        question,
        top_k: options.topK || 5,
        retriever: options.retriever || 'hybrid',
        mode: options.mode || 'qa',
        vendor: options.vendor || null,
        use_gemini: options.useGemini !== false
      });
      return response.data;
    } catch (error) {
      console.error("API Error in ask():", error);
      throw new Error(error.response?.data?.detail || "Failed to fetch response from DealDesk AI");
    }
  },

  upload: async (file, vendor) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('vendor', vendor || 'Custom');

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } catch (error) {
      console.error("API Error in upload():", error);
      throw new Error(error.response?.data?.detail || "Failed to upload document");
    }
  },

  sendFeedback: async (logId, feedbackValue) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/feedback`, {
        log_id: logId,
        feedback: feedbackValue
      });
      return response.data;
    } catch (error) {
      console.error("API Error in sendFeedback():", error);
      throw new Error(error.response?.data?.detail || "Failed to submit feedback");
    }
  }
};
