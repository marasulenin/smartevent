import { createContext, useContext, useState } from "react";

import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(
    localStorage.getItem("access_token")
  );

  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("user");

    if (!savedUser) {
      return null;
    }

    try {
      return JSON.parse(savedUser);
    } catch {
      return null;
    }
  });

  const login = async (email, password) => {
    const formData = new URLSearchParams();

    formData.append("username", email.trim());
    formData.append("password", password);

    const response = await api.post(
      "/auth/login",
      formData,
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      }
    );

    const accessToken = response.data.access_token;

    localStorage.setItem(
      "access_token",
      accessToken
    );

    setToken(accessToken);

    const profileResponse = await api.get(
      "/auth/profile",
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );

    localStorage.setItem(
      "user",
      JSON.stringify(profileResponse.data)
    );

    setUser(profileResponse.data);

    return profileResponse.data;
  };

  const register = async (
    username,
    email,
    password
  ) => {
    const response = await api.post(
      "/auth/register",
      {
        username: username.trim(),
        email: email.trim(),
        password,
      }
    );

    return response.data;
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    setToken(null);
    setUser(null);
  };

  const isAuthenticated = Boolean(token);

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        login,
        register,
        logout,
        isAuthenticated,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}