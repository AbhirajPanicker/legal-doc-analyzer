/**
 * AuthContext — global auth state, persisted in localStorage.
 * Provides: user, token, login(), register(), logout()
 */
import { createContext, useContext, useState, useCallback } from 'react';
import { loginUser, registerUser } from '../services/api';

const AuthContext = createContext(null);

const TOKEN_KEY = 'lex_token';
const USER_KEY  = 'lex_user';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || null);
  const [user,  setUser]  = useState(() => {
    try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; }
  });

  const _persist = useCallback((tok, usr) => {
    setToken(tok);
    setUser(usr);
    if (tok) {
      localStorage.setItem(TOKEN_KEY, tok);
      localStorage.setItem(USER_KEY, JSON.stringify(usr));
    } else {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
  }, []);

  const login = useCallback(async (email, password) => {
    const { data } = await loginUser(email, password);
    _persist(data.access_token, data.user);
    return data.user;
  }, [_persist]);

  const register = useCallback(async (email, password, fullName) => {
    const { data } = await registerUser(email, password, fullName);
    _persist(data.access_token, data.user);
    return data.user;
  }, [_persist]);

  const logout = useCallback(() => _persist(null, null), [_persist]);

  return (
    <AuthContext.Provider value={{ token, user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
