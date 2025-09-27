import { Routes, Route, Link } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import ProfilePage from "./pages/ProfilePage";
import AdminUsersPage from "./pages/AdminUsersPage";
import { Protected } from "./components/Protected";
import { useAuth } from "./auth";

export default function App() {
  const { user } = useAuth();
  return (
    <div>
      <nav style={{display:"flex", gap:12, padding:12, borderBottom:"1px solid #ddd"}}>
        <Link to="/">Профиль</Link>
        {user?.role === "admin" && <Link to="/admin/users">Пользователи</Link>}
        {!user && <Link to="/login">Вход</Link>}
      </nav>
      <Routes>
        <Route path="/login" element={<LoginPage/>}/>
        <Route path="/" element={
          <Protected><ProfilePage/></Protected>
        }/>
        <Route path="/admin/users" element={
          <Protected role="admin"><AdminUsersPage/></Protected>
        }/>
      </Routes>
    </div>
  );
}
