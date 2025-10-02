// src/services/authService.js
import api from './api.js';

export const authService = {
  login: (email, password) => 
    api.post('/auth/login', { email, password }).then(r => r.data),
  
  getProfile: () => 
    api.get('/auth/me').then(r => r.data),
  
  getUsers: () => 
    api.get('/users').then(r => r.data),
  
  createUser: (userData) => 
    api.post('/users', userData).then(r => r.data),
  
  deleteUser: (userId) => 
    api.delete(`/users/${userId}`).then(r => r.data)
};
