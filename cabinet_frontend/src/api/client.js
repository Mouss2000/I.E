import axios from "axios";

const api = axios.create();
const tenantIdPattern = /^[a-z0-9][a-z0-9-]*$/;

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('demo_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  const tenantId = sessionStorage.getItem("tenant_id");
  if (!tenantId || !tenantIdPattern.test(tenantId)) {
    throw new Error("A valid tenant_id is required before making API requests.");
  }

  const apiOrigin = new URL(import.meta.env.VITE_API_ORIGIN || "http://localhost:8000");
  apiOrigin.hostname =
    apiOrigin.hostname === "localhost" || apiOrigin.hostname === "127.0.0.1"
      ? `${tenantId}.localhost`
      : `${tenantId}.${apiOrigin.hostname}`;

  config.baseURL = new URL("/api/", apiOrigin).toString();
  return config;
});

export default api;
