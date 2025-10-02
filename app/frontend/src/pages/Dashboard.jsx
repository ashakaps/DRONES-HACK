import React, { useEffect, useState, useCallback } from "react";
import { Routes, Route, Navigate, useLocation, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { TabsBar } from "../components/TabsBar.jsx";
import UsersAdmin from "../components/UsersAdmin.jsx";
import Profile from "../components/Profile.jsx";
import { authService } from '../services/authService.js';
import DroneRadar from "../components/DroneRadar.tsx";

import "./Dashboard.css";

// заглушки вкладок — подмени своими компонентами
function ImportData() { return <div>Загрузка данных</div>; }
function DroneRadarStub() { return <div>Будет карта. потом.</div>; }

function MapWithLegacyLink() {
  return (
    <>
        <Link to="/static/" reloadDocument>Переход на карту</Link>
    </>
  );
}


function Logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "/login";
  return null;
}

export default function Dashboard() {
  const { user, logout, isAdmin } = useAuth();
  const [users, setUsers] = useState([]);
  const [uLoading, setULoading] = useState(false);
  const [uError, setUError] = useState(null);
  const { pathname } = useLocation();


  const loadUsers = useCallback(async () => {
    try {
      setULoading(true); setUError(null);
      const data = await authService.getUsers(); // должен возвращать .data
      setUsers(data);
    } catch (e) {
      setUError(e?.response?.data?.detail || "Не удалось загрузить пользователей");
    } finally {
      setULoading(false);
    }
  }, []);


  useEffect(() => {
    if (isAdmin && pathname === "/users") loadUsers();
  }, [isAdmin, pathname, loadUsers]);

  const handleDeleteUser = async (id) => {
    if (!confirm("Удалить пользователя?")) return;
    await authService.deleteUser(id);
    await loadUsers();
  };

const handleCreateUser = async (payload) => {
  await authService.createUser(payload);
  // список обновит onRefresh внутри компонента
};    

    const tabs = (() => {
        if (isAdmin) {
            return  [
                { to: "/users",   label: "Пользователи" },
                { to: "/import",  label: "Загрузка данных" },
//                { to: "/map",     label: "Карта" },
                { to: "/static",  label: "Карта России" },
                { to: "/profile", label: "Профиль" },
            ];
        } else {
            return [
//                { to: "/map",     label: "Карта" },
                { to: "/static",     label: "Карта России" },
                { to: "/profile", label: "Профиль" },
            ];

        }

    })();

  const defaultRoute = isAdmin ? "/users" : "/map";

  return (
    <div className="admin-dashboard">
      <header className={`dashboard-${isAdmin ? 'admin' : 'operator'}-header`}>
        <h1>{isAdmin ? "Администратор" : "Оператор"} {user.email} </h1>
        <button onClick={logout} className="logout-btn">Выйти</button>
      </header>

      <TabsBar tabs={tabs} />
      <div style={{ padding: 12 }}>
        <Routes>
          {isAdmin && <Route path="/users" element={<UsersAdmin users={users} loading={uLoading} error={uError} onRefresh={loadUsers} onDelete={handleDeleteUser} onCreate={handleCreateUser}/>} />}
          {isAdmin && <Route path="/import" element={<ImportData />} />}
//          <Route path="/map" element={<DroneRadarStub />} />
          <Route path="/static" element={<MapWithLegacyLink />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="*" element={<Navigate to={defaultRoute} replace />} />
        </Routes>
      </div>
    </div>
  );
}
