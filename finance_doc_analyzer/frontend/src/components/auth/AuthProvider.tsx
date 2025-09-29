import React, { createContext, useContext, useEffect, useState } from 'react'
import axios from '../../api/axios'


type User = { id: string; email: string; name?: string } | null


type AuthContextType = {
    user: User
    token: string | null
    login: (email: string, password: string) => Promise<void>
    logout: () => void
    ready: boolean
}


const AuthContext = createContext<AuthContextType | undefined>(undefined)


export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User>(null)
    const [token, setToken] = useState<string | null>(null)
    const [ready, setReady] = useState(false)


    useEffect(() => {
        const t = "devtoken123"
        if (t) {
            setToken(t)
            axios.defaults.headers.common['Authorization'] = `Bearer ${t}`
            axios.get('/auth/profile').then(r => setUser(r.data)).catch(() => setUser(null)).finally(() => setReady(true))
        } else setReady(true)
    }, [])


    const login = async (email: string, password: string) => {
        const res = await axios.post('/auth/login', { email, password })
        const t = res.data.token
        sessionStorage.setItem('app_token', t)
        axios.defaults.headers.common['Authorization'] = `Bearer ${t}`
        setToken(t)
        const profile = await axios.get('/auth/profile')
        setUser(profile.data)
    }


    const logout = () => {
        sessionStorage.removeItem('app_token')
        delete axios.defaults.headers.common['Authorization']
        setToken(null)
        setUser(null)
    }


    return (
        <AuthContext.Provider value={{ user, token, login, logout, ready }}>
            {children}
        </AuthContext.Provider>
    )
}


export const useAuth = () => {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
    return ctx
}