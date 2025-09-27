import React, { useEffect, useState } from "react";
import { api } from "../api";

type Role = "admin" | "operator";
type UserRead = {
  id: number; email: string; role: Role; created_at: string; last_login_at?: string | null;
};

export default function AdminUsersPage() {
  const [users, setUsers] = useState<UserRead[]>([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("operator");
  const [err, setErr] = useState<string | null>(null);

  const load = async () => {
    try {
      const { data } = await api.get<UserRead[]>("/users");
      setUsers(data);
    } catch (e:any) { setErr(e?.response?.data?.detail ?? "load error"); }
  };

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/users", { email, password, role });
      setEmail(""); setPassword(""); setRole("operator");
      await load();
    } catch (e:any) { setErr(e?.response?.data?.detail ?? "create error"); }
  };

  const delUser = async (id: number) => {
    await api.delete(`/users/${id}`);
    await load();
  };

  useEffect(()=>{ load(); }, []);

  return (
    <div style={{maxWidth: 900, margin: "32px auto"}}>
      <h2>Пользователи (Админ)</h2>
      {err && <p style={{color:"crimson"}}>{err}</p>}
      <form onSubmit={add} style={{display:"grid", gridTemplateColumns:"1fr 1fr 1fr auto", gap:8, alignItems:"end"}}>
        <label>Email<input value={email} onChange={e=>setEmail(e.target.value)} type="email" required/></label>
        <label>Пароль<input value={password} onChange={e=>setPassword(e.target.value)} type="password" required/></label>
        <label>Роль
          <select value={role} onChange={e=>setRole(e.target.value as Role)}>
            <option value="operator">operator</option>
            <option value="admin">admin</option>
          </select>
        </label>
        <button type="submit">Добавить</button>
      </form>

      <table style={{width:"100%", marginTop:20}} border={1} cellPadding={6}>
        <thead>
          <tr><th>ID</th><th>Email</th><th>Роль</th><th>Создан</th><th>Последний вход</th><th/></tr>
        </thead>
        <tbody>
          {users.map(u=>(
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.email}</td>
              <td>{u.role}</td>
              <td>{new Date(u.created_at).toLocaleString()}</td>
              <td>{u.last_login_at ? new Date(u.last_login_at).toLocaleString() : "—"}</td>
              <td><button onClick={()=>delUser(u.id)}>Удалить</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
