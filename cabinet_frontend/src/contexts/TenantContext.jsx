import { useState } from "react";
import { TenantContext } from "./tenantContext";
const tenantIdPattern = /^[a-z0-9][a-z0-9-]*$/;

function getStoredTenant() {
  const id = sessionStorage.getItem("tenant_id");
  if (!id) return null;

  return {
    id,
    name: sessionStorage.getItem("tenant_name") || id,
  };
}

export function TenantProvider({ children }) {
  const [tenant, setTenantState] = useState(getStoredTenant);

  const setTenant = (id, name = id) => {
    if (!tenantIdPattern.test(id)) {
      throw new Error("Tenant ID must use lowercase letters, numbers, or hyphens.");
    }

    sessionStorage.setItem("tenant_id", id);
    sessionStorage.setItem("tenant_name", name);
    setTenantState({ id, name });
  };

  const clearTenant = () => {
    sessionStorage.removeItem("tenant_id");
    sessionStorage.removeItem("tenant_name");
    setTenantState(null);
  };

  return (
    <TenantContext.Provider value={{ tenant, setTenant, clearTenant }}>
      {children}
    </TenantContext.Provider>
  );
}
