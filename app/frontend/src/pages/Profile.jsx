// src/pages/Profile.js
import React from 'react';
import { useAuth } from '../context/AuthContext';

const Profile = () => {
  const { user } = useAuth();

  return (
    <div className="profile">
      <h2>Мой профиль</h2>
      <div className="profile-info">
        <p><strong>Email:</strong> {user?.email}</p>
        <p><strong>Роль:</strong> {user?.role}</p>
        <p><strong>Последний вход:</strong> {user?.last_login ? new Date(user.last_login).toLocaleString() : 'Никогда'}</p>
      </div>
    </div>
  );
};

export default Profile;