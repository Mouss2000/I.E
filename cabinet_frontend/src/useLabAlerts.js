import { useEffect, useState } from 'react';
import api from './api/client';

export function useLabAlerts(enabled) {
  const [snapshot, setSnapshot] = useState({ scope: null, alerts: [] });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;
    let running = false;
    let queued = false;
    async function refresh() {
      if (running) { queued = true; return; }
      running = true;
      try {
        const { data } = await api.get('alerts/');
        if (!cancelled) { setSnapshot({ scope: enabled, alerts: data }); setError(''); }
      } catch {
        if (!cancelled) setError('Impossible d’actualiser les alertes. Nouvelle tentative automatique dans 30 secondes.');
      } finally {
        running = false;
        if (!cancelled) {
          setLoading(false);
          if (queued) { queued = false; refresh(); }
        }
      }
    }
    refresh();
    const timer = window.setInterval(refresh, 30000);
    window.addEventListener('focus', refresh);
    window.addEventListener('lab-resources-changed', refresh);
    return () => {
      cancelled = true; window.clearInterval(timer);
      window.removeEventListener('focus', refresh);
      window.removeEventListener('lab-resources-changed', refresh);
    };
  }, [enabled]);
  return { alerts: enabled && snapshot.scope === enabled ? snapshot.alerts : [], error, loading };
}

