// src/pages/AdminDashboard.jsx  ← исправил расширение
import React, { useState, useEffect } from 'react';
import { authService } from '../services/authService';
import { useAuth } from '../context/AuthContext';
import DroneRadarEmbeddable from '../components/DroneRadarEmbeddable';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('map'); // 'map' или 'users'
  const { logout, user } = useAuth();

  const [newUser, setNewUser] = useState({
    email: '',
    password: '',
    role: 'operator'
  });

  // Данные для карты
  const cities = [
    { id: 'moscow', name: 'Москва' },
    { id: 'spb', name: 'Санкт-Петербург' },
    { id: 'kazan', name: 'Казань' },
    { id: 'novosibirsk', name: 'Новосибирск' }
  ];

  const regions = [
    { id: 'central', name: 'Центральный ФО' },
    { id: 'northwest', name: 'Северо-Западный ФО' },
    { id: 'south', name: 'Южный ФО' },
    { id: 'volga', name: 'Приволжский ФО' },
    { id: 'ural', name: 'Уральский ФО' },
    { id: 'siberian', name: 'Сибирский ФО' },
    { id: 'far_east', name: 'Дальневосточный ФО' }
  ];

  useEffect(() => {
    if (activeTab === 'users') {
      loadUsers();
    }
  }, [activeTab]);

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

  const handleMapReady = (map) => {
    console.log('Карта готова для администратора:', map);
  };

  const handleCitySelect = (cityId) => {
    console.log('Админ выбрал город:', cityId);
  };

  const handleRegionSelect = (regionId) => {
    console.log('Админ выбрал регион:', regionId);
  };

  return (
    <div className="admin-dashboard">
      <header className="dashboard-header">
        <h1>Панель администратора</h1>
        <div className="user-info">
          <span>{user?.email}</span>
          <button onClick={logout} className="logout-btn">Выйти</button>
        </div>
      </header>

      <div className="dashboard-content">
        {/* Панель вкладок */}
        <div className="tabs-panel">
          <button 
            className={`tab-btn ${activeTab === 'map' ? 'active' : ''}`}
            onClick={() => setActiveTab('map')}
          >
            Просмотр карты
          </button>
          <button 
            className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            Управление пользователями
          </button>
          <button className="tab-btn" onClick={() => console.log('Загрузка данных')}>
            Загрузить данные
          </button>
          <button className="tab-btn" onClick={() => window.location.href = '/profile'}>
            Мой профиль
          </button>
        </div>

        {/* Контент вкладок */}
        {activeTab === 'map' && (
          <div className="map-container">
            <DroneRadarEmbeddable
              containerId="admin-map"
              className="admin-map"
              initialCities={cities}
              initialRegions={regions}
              onMapReady={handleMapReady}
              onCitySelect={handleCitySelect}
              onRegionSelect={handleRegionSelect}
              onFilter={() => console.log('Фильтр применен')}
              onModeToggle={() => console.log('Режим переключен')}
            />
          </div>
        )}

        {activeTab === 'users' && (
          <div className="users-panel">
            <div className="panel-header">
              <h3>Управление пользователями</h3>
              <button 
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="btn-primary"
              >
                {showCreateForm ? 'Отмена' : 'Создать пользователя'}
              </button>
            </div>

            {showCreateForm && (
              <div className="create-user-form card">
                <h4>Создать нового пользователя</h4>
                <form onSubmit={handleCreateUser}>
                  <div className="form-group">
                    <input
                      type="email"
                      placeholder="Email"
                      value={newUser.email}
                      onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <input
                      type="password"
                      placeholder="Пароль"
                      value={newUser.password}
                      onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <select
                      value={newUser.role}
                      onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                    >
                      <option value="operator">Оператор</option>
                      <option value="admin">Администратор</option>
                    </select>
                  </div>
                  <div className="form-actions">
                    <button type="submit" disabled={loading} className="btn-primary">
                      {loading ? 'Создание...' : 'Создать'}
                    </button>
                  </div>
                </form>
              </div>
            )}

            <div className="users-table card">
              <h4>Пользователи системы</h4>
              <table className="table">
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
                      <td>
                        <span className={`role-badge role-${user.role}`}>
                          {user.role}
                        </span>
                      </td>
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
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;