import axios from 'axios';

const origin = new URL(import.meta.env.VITE_API_ORIGIN || 'http://localhost:8000');
const platform = axios.create({ baseURL: new URL('/platform/', origin).toString() });
platform.interceptors.request.use(config => {
  const token = sessionStorage.getItem('demo_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
export default platform;
