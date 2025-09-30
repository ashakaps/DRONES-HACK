// src/pages/AdminDashboard.js
import React, { useState, useEffect } from 'react';
import { authService } from '../services/authService';
import { useAuth } from '../context/AuthContext';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const { logout } = useAuth();

  const [newUser, setNewUser] = useState({
    email: '',
    password: '',
    role: 'operator'
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await authService.getUsers();
      setUsers(response.data);
    } catch (error) {
      console.error('Error loading users:', error);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await authService.createUser(newUser);
      setNewUser({ email: '', password: '', role: 'operator' });
      setShowCreateForm(false);
      loadUsers();
    } catch (error) {
      console.error('Error creating user:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('Вы уверены, что хотите удалить пользователя?')) {
      try {
        await authService.deleteUser(userId);
        loadUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    }
  };

  return (
    <div className="admin-dashboard">
      <header className="dashboard-header">
        <h1>Панель администратора</h1>
        <button onClick={logout} className="logout-btn">Выйти</button>
      </header>

      <div className="dashboard-content">
        <div className="actions-panel">
          <button 
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="btn-primary"
          >
            Создать пользователя
          </button>
          <button className="btn-secondary">Загрузить данные</button>
          <button className="btn-secondary">Просмотр карты</button>
          <button className="btn-secondary">Мой профиль</button>
        </div>

        {showCreateForm && (
          <div className="create-user-form">
            <h3>Создать нового пользователя</h3>
            <form onSubmit={handleCreateUser}>
              <input
                type="email"
                placeholder="Email"
                value={newUser.email}
                onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                required
              />
              <input
                type="password"
                placeholder="Пароль"
                value={newUser.password}
                onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                required
              />
              <select
                value={newUser.role}
                onChange={(e) => setNewUser({...newUser, role: e.target.value})}
              >
                <option value="operator">Оператор</option>
                <option value="admin">Администратор</option>
              </select>
              <button type="submit" disabled={loading}>
                {loading ? 'Создание...' : 'Создать'}
              </button>
              <button type="button" onClick={() => setShowCreateForm(false)}>
                Отмена
              </button>
            </form>
          </div>
        )}

        <div className="users-table">
          <h3>Пользователи системы</h3>
          <table>
            <thead>
              <tr>
                <th>Email</th>
                <th>Роль</th>
                <th>Последний вход</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id}>
                  <td>{user.email}</td>
                  <td>{user.role}</td>
                  <td>{user.last_login ? new Date(user.last_login).toLocaleString() : 'Никогда'}</td>
                  <td>
                    <button 
                      onClick={() => handleDeleteUser(user.id)}
                      className="btn-danger"
                    >
                      Удалить
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;