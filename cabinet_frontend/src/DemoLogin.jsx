import { useState } from 'react';
import { User, ArrowRight } from 'lucide-react';
import platform from './api/platform';
import { useTenant } from './contexts/useTenant';
import logo from './assets/logo.png';

export default function DemoLogin({ setUser, courierLogin }) {
  const [name, setName] = useState('');
  const [courier, setCourier] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const { setTenant, clearTenant } = useTenant();
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError('');
    try {
      const { data } = await platform.post('login/', { name });
      const role = { ADMIN: 'Administrateur', DENTIST: 'Cabinet Dentaire', LAB: 'Laboratoire' }[data.account.role];
      const user = { id: data.account.id, name: data.account.name, role, email: data.account.email };
      if (data.account.laboratory_id) setTenant(data.account.laboratory_id, data.account.laboratory_name);
      else clearTenant();
      sessionStorage.setItem('demo_token', data.token);
      sessionStorage.setItem('demo_user', JSON.stringify(user));
      setUser(user);
    } catch (err) { setError(err.response?.data?.detail || 'Connexion impossible. Vérifiez que le serveur est démarré.'); }
    finally { setBusy(false); }
  }
  if (courier) return <div><button onClick={() => setCourier(false)} className="fixed left-6 top-6 z-10 rounded-xl border border-white/15 bg-[#171321] px-4 py-2 text-sm text-white">← Retour à la connexion</button>{courierLogin}</div>;
  return <div className="min-h-screen bg-[#0d0914] p-6 text-white flex items-center justify-center"><section className="w-full max-w-lg rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl">
    <img src={logo} alt="Cabinet 2.0" className="mx-auto mb-6 h-24 object-contain" /><h1 className="text-center text-2xl font-semibold">Votre espace Cabinet 2.0</h1><p className="mt-3 text-center text-sm text-slate-400">Saisissez votre nom. Votre compte vous dirige automatiquement vers votre espace.</p>
    <form onSubmit={submit} className="mt-7 space-y-4"><label className="block text-sm text-slate-300">Nom du compte<div className="relative mt-2"><User className="absolute left-3 top-3.5 h-4 w-4 text-slate-500" /><input aria-label="Nom du compte" autoComplete="username" required value={name} onChange={event => setName(event.target.value)} placeholder="Dentiste 1 ou Labo 2 - Mohamed" className="w-full rounded-xl border border-white/15 bg-black/30 py-3 pl-10 pr-4 outline-none focus:border-sky-400" /></div></label>{error && <p role="alert" className="rounded-xl bg-red-400/10 p-3 text-sm text-red-300">{error}</p>}<button disabled={busy} className="flex w-full items-center justify-center gap-2 rounded-xl bg-sky-500 px-4 py-3 font-medium disabled:opacity-50">{busy ? 'Connexion…' : 'Accéder à mon espace'}<ArrowRight className="h-4 w-4" /></button></form>
    <div className="mt-6 rounded-xl border border-sky-400/15 bg-sky-400/5 p-4 text-xs leading-relaxed text-slate-400"><p className="font-medium text-sky-300">Mode démonstration — sans mot de passe</p><p className="mt-2">Dentiste 1, Dentiste 2, Dentiste 3</p><p>Labo 1 - Mohamed, Labo 2 - Mohamed, Labo 3 - Mohamed</p><p>Administration du projet : Admin</p></div>
    <button onClick={() => setCourier(true)} className="mt-5 w-full text-center text-xs text-slate-400 hover:text-white">Accès livreur</button>
  </section></div>;
}
