import { NavLink } from "react-router-dom";

export function TabsBar({ tabs }) {
  return (
    <div style={{ display: "flex", gap: 12, borderBottom: "1px solid #ddd", padding: "8px 12px" }}>
      {tabs.map(t => (
        <NavLink
          key={t.to}
          to={t.to}
          end
          style={({ isActive }) => ({
            padding: "6px 10px",
            borderBottom: isActive ? "2px solid #333" : "2px solid transparent",
            textDecoration: "none",
          })}
        >
          {t.label}
        </NavLink>
      ))}
    </div>
  );
}
