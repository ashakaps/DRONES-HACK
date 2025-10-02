import React, { useState } from "react";

function fmt(dt) {
  if (!dt) return "Никогда";
  try { return new Date(dt).toLocaleString(); } catch { return String(dt); }
}

export default function UsersAdmin({ users, loading, error, onRefresh, onDelete, onCreate }) {

  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ email: "", password: "", role: "operator" });
  const [cErr, setCErr] = useState(null);
  const canSubmit = form.email && form.password && form.role;

  const submitCreate = async (e) => {
    e.preventDefault();
    if (!onCreate) return;
    setCErr(null);
    try {
      setCreating(true);
      await onCreate(form);                 // ожидается { email, password, role }
      setForm({ email: "", password: "", role: "operator" });
      onRefresh?.();                        // обновим список после создания
    } catch (e2) {
      setCErr(e2?.response?.data?.detail || "Не удалось создать пользователя");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="users-table">
      <h3>Пользователи системы</h3>

      {/* Форма создания */}
      <form onSubmit={submitCreate} className="create-user-form" style={{ display:"grid", gap:8, gridTemplateColumns:"2fr 2fr 1fr auto" }}>
        <input
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          required
        />
        <input
          type="password"
          placeholder="Пароль"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          required
        />
        <select
          value={form.role}
          onChange={(e) => setForm({ ...form, role: e.target.value })}
        >
          <option value="operator">Оператор</option>
          <option value="admin">Администратор</option>
        </select>
        <button type="submit" className="btn-primary" disabled={!canSubmit || creating}>
          {creating ? "Создаю…" : "Создать"}
        </button>
        {cErr && <div style={{ gridColumn:"1/-1", color:"crimson" }}>{cErr}</div>}
      </form>


      {loading && <div>Загрузка…</div>}
      {error && <div style={{color:"crimson"}}>{error}</div>}
      {(!users || users.length === 0) ? (
        <div style={{opacity:.7, padding:"8px 0"}}>Пока нет пользователей</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Email</th>
              <th>Роль</th>
              <th>Последний вход</th>
              <th>Создан</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id}>
                <td>{u.email}</td>
                <td>{u.role}</td>
                <td>{fmt(u.last_login_at)}</td>
                <td>{fmt(u.created_at)}</td>
                <td>
                  <button
                    onClick={() => onDelete?.(u.id)}
                    className="btn-danger"
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ marginTop: 10 }}>
        <button onClick={onRefresh} className="btn-secondary">Обновить</button>
      </div>

    </div>
  );
}
