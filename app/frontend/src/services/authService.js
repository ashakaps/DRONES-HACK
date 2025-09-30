// src/services/authService.js
import api from './api';

export const authService = {
  login: (email, password) => 
    api.post('/auth/login', { email, password }),
  
  getProfile: () => 
    api.get('/auth/me'),
  
  getUsers: () => 
    api.get('/users'),
  
  createUser: (userData) => 
    api.post('/users', userData),
  
  deleteUser: (userId) => 
    api.delete(`/users/${userId}`)
};