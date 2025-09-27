import { useAuth } from "../auth";

export default function ProfilePage() {
  const { user, logout } = useAuth();
  if (!user) return null;
  return (
    <div style={{maxWidth: 720, margin: "32px auto"}}>
      <h2>Профиль</h2>
      <table>
        <tbody>
          <tr><td>Role</td><td>{user.role}</td></tr>
          <tr><td>Email</td><td>{user.email}</td></tr>
          <tr><td>Зарегистрирован</td><td>{new Date(user.created_at).toLocaleString()}</td></tr>
          <tr><td>Последний вход</td><td>{user.last_login_at ? new Date(user.last_login_at).toLocaleString() : "—"}</td></tr>
        </tbody>
      </table>
      <button onClick={logout} style={{marginTop:12}}>Выйти</button>
    </div>
  );
}
