import React, { createContext, useContext, useState } from 'react'


const SnackbarContext = createContext<any>(null)


export const SnackbarProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [msg, setMsg] = useState<string | null>(null)
    return (
        <SnackbarContext.Provider value={{ show: (m: string) => setMsg(m) }}>
            {children}
            {msg && (
                <div className="fixed right-4 bottom-4 bg-black text-white px-4 py-2 rounded" onClick={() => setMsg(null)}>{msg}</div>
            )}
        </SnackbarContext.Provider>
    )
}


export const useSnackbar = () => {
    const ctx = useContext(SnackbarContext)
    if (!ctx) throw new Error('useSnackbar must be used inside SnackbarProvider')
    return ctx
}