import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8080',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
});

export const api = {
    getAppeals: async () => {
        const response = await apiClient.get('/appeals/');
        return response.data;
    },

    createAppeal: async (appeal) => {
        const response = await apiClient.post('/appeals/predict', appeal);
        return response.data;
    },

    deleteAppeal: async (appealId) => {
        const response = await apiClient.delete(`/appeals/${appealId}`);
        return response.data;
    },
};
