import { useAuth } from '../context/AuthContext.jsx';

const Profile = () => {
  const { user } = useAuth();

  return (
    <div className="profile">
      <h2>Мой профиль</h2>
      <div className="profile-info">
        <p><strong>Email:</strong> {user?.email}</p>
        <p><strong>Роль:</strong> {user?.role}</p>
        <p><strong>Последний вход:</strong> {user?.last_login_at ? new Date(user.last_login_at).toLocaleString() : 'Никогда'}</p>
        <p><strong>Создан :</strong> {user?.created_at ? new Date(user.created_at).toLocaleString() : 'Никогда'}</p>
      </div>
    </div>
  );
};

export default Profile;
