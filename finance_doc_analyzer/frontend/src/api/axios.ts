// src/api/axios.ts
import axios from "axios"

// Read token from localStorage
const token = "devtoken123"

// Base URL injected via Vite env variable
const API_BASE = import.meta.env.VITE_BACKEND_API_URL || "http://localhost:5050/api"

const instance = axios.create({
  baseURL: API_BASE,
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  timeout: 60000, // 60s for large file uploads
})

// Optional: automatically refresh token / handle 401 globally
instance.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      console.warn("Unauthorized - redirect to login")
      // e.g., window.location.href = "/login"
    }
    return Promise.reject(error)
  }
)

export default instance
