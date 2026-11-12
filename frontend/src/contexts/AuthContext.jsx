import { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../lib/api';

const AuthContext = createContext(null);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    if (!sessionStorage.getItem('cmk_token')) {
      setLoading(false);
      return;
    }
    api
      .get('/api/auth/me')
      .then(({ data }) => setUser(data))
      .catch(() => sessionStorage.removeItem('cmk_token'))
      .finally(() => setLoading(false));
  }, []);
  const login = async (email, password) => {
    const { data } = await api.post('/api/auth/login', { email, password });
    sessionStorage.setItem('cmk_token', data.access_token);
    setUser(data.user);
    return data.user;
  };
  const logout = () => {
    sessionStorage.removeItem('cmk_token');
    setUser(null);
  };
  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>
  );
}
export function useAuth() {
  return useContext(AuthContext);
}