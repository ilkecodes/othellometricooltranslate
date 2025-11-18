import { create } from "zustand";

interface AuthStore {
  token: string | null;
  user: {
    id: number;
    email: string;
    fullName: string;
    role: string;
  } | null;
  setToken: (token: string) => void;
  setUser: (user: AuthStore["user"]) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  token: null,
  user: null,
  setToken: (token: string) => {
    localStorage.setItem("access_token", token);
    set({ token });
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem("access_token");
    set({ token: null, user: null });
  },
  isAuthenticated: () => {
    return get().token !== null;
  },
}));
