import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth";

export const Protected: React.FC<{ children: React.ReactNode; role?: "admin" | "operator" }>=({ children, role })=>{
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to="/" replace />;
  return children;
};
