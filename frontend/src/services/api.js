import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL
});

// Add token to all requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// Handle token expiration
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export const authApi = {
    login: (credentials) => api.post('/auth/login/', credentials),
    register: (userData) => api.post('/auth/register/', userData),
    verify: () => api.get('/profile/'),  // Use profile endpoint to verify token
    checkUsername: (username) => api.get(`/auth/check-username/${username}/`),
};

export const profileApi = {
    get: () => api.get('/profile/'),
    update: (data) => api.patch('/profile/', data),
    uploadResume: (formData) => api.post('/upload_resume/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    }),
    getCurrentResume: () => api.get('/resume/current/'),
    deleteResume: () => api.delete('/resume/current/'),
};

export const skillsApi = {
    list: () => api.get('/skills/'),
    create: (skill) => api.post('/skills/', skill),
    update: (id, skill) => api.patch(`/skills/${id}/`, skill),
    delete: (id) => api.delete(`/skills/${id}/`),
    findMatches: (skills) => api.post('/match_skills/', { skills }),
};

export const usersApi = {
    search: (params) => api.get('/users/search/', { params }),
    getProfile: (username) => api.get(`/users/profile/${username}/`),
};

export const connectionsApi = {
    request: (userId) => api.post(`/connections/request/${userId}/`),
    accept: (connectionId) => api.post(`/connections/${connectionId}/accept/`),
    reject: (connectionId) => api.post(`/connections/${connectionId}/reject/`),
};

export const messagesApi = {
    fetchConversation: (withUserId) => api.get('/messages/', { params: { with: withUserId } }),
    sendMessage: (receiverId, content) => api.post('/messages/', { receiver: receiverId, content }),
    sendMessageWithFile: (formData) => api.post('/messages/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    }),
    getConversations: () => api.get('/conversations/'),
};

export default api;