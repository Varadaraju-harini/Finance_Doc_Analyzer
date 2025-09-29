// src/App.tsx
import React from "react"
import { Routes, Route, Navigate } from "react-router-dom"
import { RoleSelectPage } from "./pages/RoleSelectPage"
import UploadPage from "./pages/UploadPage"

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <Routes>
        {/* Default → Role selection */}
        <Route path="/" element={<RoleSelectPage />} />

        {/* Upload page after role is selected */}
        <Route path="/upload" element={<UploadPage />} />

        {/* Catch-all redirect to Role Select */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

export default App
