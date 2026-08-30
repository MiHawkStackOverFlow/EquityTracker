import axios from 'axios';

// Create a configured Axios instance
export const apiClient = axios.create({
    // Points to the EC2 backend or local dev server
    baseURL: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000',
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Basic GET example calling the root/ping endpoint
export const pingServer = async () => {
    try {
        const response = await apiClient.get('/');
        return response.data;
    } catch (error) {
        console.error("API Ping Failed:", error);
        throw error;
    }
};