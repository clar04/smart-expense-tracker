import axios from "axios";


export const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE || "http://localhost:8000",
});


api.interceptors.response.use(
    (r) => r,
    (err) => {
        const detail = err?.response?.data?.detail;
        if (detail) console.error("API Error:", detail);
        return Promise.reject(err);
    }
);