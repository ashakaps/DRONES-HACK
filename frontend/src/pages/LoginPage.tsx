import React, { useState } from "react";
import { useAuth } from "../auth";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [err, setErr] = useState<string | null>(null);
  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      nav("/");
    } catch (e:any) {
      setErr(e?.response?.data?.detail ?? "Login failed");
    }
  };
  return (
    <div style={{maxWidth: 360, margin: "64px auto"}}>
      <h2>Вход</h2>
      <form onSubmit={onSubmit}>
        <label> Email
          <input value={email} onChange={e=>setEmail(e.target.value)} type="email" required />
        </label>
        <label> Пароль
          <input value={password} onChange={e=>setPassword(e.target.value)} type="password" required />
        </label>
        <button type="submit">Войти</button>
      </form>
      {err && <p style={{color:"crimson"}}>{err}</p>}
      <p style={{opacity:.7, marginTop:12}}>Демо: admin@example.com / admin123</p>
    </div>
  );
}
