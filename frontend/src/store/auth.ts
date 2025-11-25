import { create } from 'zustand';
import api from '../lib/api';

interface User {
    id: number;
    email: string;
    full_name?: string;
}

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    login: (token: string) => void;
    logout: () => void;
    fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
    isAuthenticated: typeof window !== 'undefined' ? !!localStorage.getItem('token') : false,

    login: (token: string) => {
        localStorage.setItem('token', token);
        set({ token, isAuthenticated: true });
    },

    logout: () => {
        localStorage.removeItem('token');
        set({ token: null, user: null, isAuthenticated: false });
    },

    fetchUser: async () => {
        try {
            const response = await api.get('/auth/me');
            set({ user: response.data });
        } catch (error) {
            console.error('Failed to fetch user', error);
            // If fetch fails (e.g. 401), logout
            localStorage.removeItem('token');
            set({ token: null, user: null, isAuthenticated: false });
        }
    },
}));
