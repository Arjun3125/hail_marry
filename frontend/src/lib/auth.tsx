"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api";

interface User {
    id: string;
    tenant_id: string;
    email: string;
    full_name: string | null;
    avatar_url: string | null;
    role: string;
    is_active: boolean;
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (googleToken: string) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    loading: true,
    login: async () => { },
    logout: async () => { },
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is already logged in
        api.auth
            .me()
            .then((u) => setUser(u))
            .catch(() => setUser(null))
            .finally(() => setLoading(false));
    }, []);

    const login = async (googleToken: string) => {
        await api.auth.loginGoogle(googleToken);
        const u = await api.auth.me();
        setUser(u);
    };

    const logout = async () => {
        await api.auth.logout();
        setUser(null);
        window.location.href = "/";
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}

export function getRoleDashboard(role: string): string {
    switch (role) {
        case "admin":
            return "/admin/dashboard";
        case "teacher":
            return "/teacher/dashboard";
        case "parent":
            return "/parent/dashboard";
        case "student":
        default:
            return "/student/overview";
    }
}
