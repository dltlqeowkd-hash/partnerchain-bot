'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import axios from 'axios'

export interface User {
    id: number;
    username: string;
    email: string;
    contact_name?: string;
    phone_number?: string;
    company_name?: string;
    business_number?: string;
    is_active: boolean;
    is_superuser: boolean;
    created_at: string;
    // Free Trial
    trial_days: number;
    trial_start_date: string | null;
    trial_end_date: string | null;
    subscription_status: string; // trial, active, expired
}

interface AuthContextType {
    user: User | null
    token: string | null
    login: (token: string, user: User) => void
    logout: () => void
    loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [token, setToken] = useState<string | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const storedToken = localStorage.getItem('token')
        const storedUser = localStorage.getItem('user')

        if (storedToken && storedUser) {
            setToken(storedToken)
            setUser(JSON.parse(storedUser))
            axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
        }
        setLoading(false)
    }, [])

    const login = (newToken: string, newUser: User) => {
        setToken(newToken)
        setUser(newUser)
        localStorage.setItem('token', newToken)
        localStorage.setItem('user', JSON.stringify(newUser))
        axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    }

    const logout = () => {
        setToken(null)
        setUser(null)
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        delete axios.defaults.headers.common['Authorization']
        window.location.href = '/'
    }

    return (
        <AuthContext.Provider value={{ user, token, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
