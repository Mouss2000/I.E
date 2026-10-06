import React, { useState, useEffect } from "react";
import { 
  User, Activity, FileText, CheckCircle, Package, Truck, 
  ShieldCheck, Clock, Zap, LogOut, ChevronRight, Check
} from "lucide-react";
import shadeGuideImg from "./assets/shade-guide.png";
import logoImg from "./assets/logo.png";

const API_URL = "http://127.0.0.1:8000/api/prescriptions/";

export default function App() {
  const [user, setUser] = useState(null);
  const [orders, setOrders] = useState([]);
  
  const fetchOrders = async () => {
    try {
      const res = await fetch(API_URL);
      if (res.ok) {
        const data = await res.json();
        setOrders(data);
      }
    } catch (e) {
      console.error("API Error", e);
    }
  };

  useEffect(() => {
    if (user) fetchOrders();
  }, [user]);

  if (!user) return <LoginScreen setUser={setUser} />;

  return (
    <div className="flex h-screen bg-[#0d0914] text-white font-sans overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 bg-white/5 border-r border-white/10 p-6 flex flex-col">
        <div className="flex items-center gap-3 mb-10">
          <img src={logoImg} alt="Cabinet 2.0 Logo" className="h-10 w-10 drop-shadow-[0_0_15px_rgba(14,165,233,0.6)] object-contain" />
          <h1 className="text-xl font-bold text-white tracking-wide">Cabinet 2.0</h1>
        </div>
        
        <div className="bg-black/40 rounded-xl p-4 border border-white/10 mb-8">
          <div className="text-sm text-gray-400 mb-1">Connecté en tant que</div>
          <div className="font-semibold text-lg">{user.name}</div>
          <div className="text-xs text-violet-400 mt-1 uppercase tracking-wider font-semibold">
            {user.role}
          </div>
        </div>
        
        <div className="flex-1"></div>
        
        <button 
          onClick={() => setUser(null)}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors p-2"
        >
          <LogOut className="w-5 h-5" />
          Déconnexion
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <header className="h-16 border-b border-white/10 bg-white/5 flex items-center px-8 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Système synchronisé
          </div>
        </header>
        
        <main className="p-8 max-w-7xl mx-auto">
          {user.role === "Cabinet Dentaire" && <DentistPortal user={user} orders={orders} refresh={fetchOrders} />}
          {user.role === "Laboratoire" && <LabPortal orders={orders} refresh={fetchOrders} />}
          {user.role === "Coursier" && <CourierPortal orders={orders} refresh={fetchOrders} />}
        </main>
      </div>
    </div>
  );
}

// ---------------- VIEWS ----------------

function LoginScreen({ setUser }) {
  const [name, setName] = useState("");
  const [role, setRole] = useState("Cabinet Dentaire");

  const handleLogin = (e) => {
    e.preventDefault();
    if (name.trim()) setUser({ name, role });
  };

  return (
    <div className="min-h-screen bg-[#0d0914] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-xl shadow-2xl">
        <img src={logoImg} alt="Cabinet 2.0 Logo" className="h-24 w-auto mx-auto mb-6 drop-shadow-[0_0_25px_rgba(14,165,233,0.5)] object-contain" />
        <h2 className="text-2xl font-bold text-center text-white mb-8">Connexion à votre espace</h2>
        
        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Votre Nom</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input 
                type="text" 
                required
                value={name}
                onChange={e => setName(e.target.value)}
                className="w-full bg-black/40 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:border-violet-500 focus:ring-1 focus:ring-violet-500 outline-none transition-all"
                placeholder="Dr. Dupont / Labo / Livreur"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Rôle</label>
            <select 
              value={role}
              onChange={e => setRole(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white focus:border-violet-500 outline-none appearance-none"
            >
              <option>Cabinet Dentaire</option>
              <option>Laboratoire</option>
              <option>Coursier</option>
            </select>
          </div>

          <button 
            type="submit"
            className="w-full bg-violet-600 hover:bg-violet-700 text-white font-semibold py-3 rounded-xl transition-colors shadow-[0_0_20px_rgba(124,58,237,0.3)] mt-4"
          >
            Accéder au portail
          </button>
        </form>
      </div>
    </div>
  );
}

function DentistPortal({ user, orders, refresh }) {
  const [tab, setTab] = useState("new");
  
  const myOrders = orders.filter(o => o.dentist_name === user.name);

  return (
    <div className="space-y-6">
      <div className="flex gap-4 border-b border-white/10 pb-4">
        <button 
          onClick={() => setTab("new")}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${tab === "new" ? "bg-white/10 text-white" : "text-gray-400 hover:text-white"}`}
        >
          Nouvelle Fiche
        </button>
        <button 
          onClick={() => setTab("list")}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${tab === "list" ? "bg-white/10 text-white" : "text-gray-400 hover:text-white"}`}
        >
          Mes Commandes ({myOrders.length})
        </button>
      </div>

      {tab === "new" ? <DentistForm user={user} onSuccess={() => { refresh(); setTab("list"); }} /> : <DentistList orders={myOrders} />}
    </div>
  );
}

const getToothWidth = (num) => {
  const d = num % 10;
  if (d >= 6) return "w-8";
  if (d >= 3) return "w-6";
  return "w-5";
};

const getTopMargin = (num) => {
  const d = num % 10;
  if (d <= 2) return "mt-4";
  if (d <= 5) return "mt-2";
  return "mt-0";
};

const getBottomMargin = (num) => {
  const d = num % 10;
  if (d <= 2) return "mb-4";
  if (d <= 5) return "mb-2";
  return "mb-0";
};

const ToothSvg = ({ isTop, isActive, className }) => (
  <svg 
    viewBox="0 0 24 24" 
    className={`${className} transition-all duration-300 ${isActive ? 'fill-sky-500 stroke-sky-300 drop-shadow-[0_0_10px_rgba(14,165,233,0.8)]' : 'fill-white/5 stroke-white/30 group-hover:stroke-sky-400 group-hover:fill-sky-900/40'}`}
    style={{ transform: isTop ? 'rotate(180deg)' : '' }}
  >
    <path 
      d="M4 6c0-2.5 2-4 4.5-4C10 2 11 3 12 4c1-1 2-2 3.5-2C18 2 20 3.5 20 6c0 3-1.5 5.5-3 7.5L16 20c-.5 1-2 1-2.5 0L12 16l-1.5 4c-.5 1-2 1-2.5 0L6 13.5C4.5 11.5 4 9 4 6z" 
      strokeWidth="1.5"
    />
  </svg>
);

function DentistForm({ user, onSuccess }) {
  const [formData, setFormData] = useState({
    patient_ref: "", tooth_number: "", shade: "A1", material: "Zircone",
    is_fast_track: false, disinfected: false
  });
  const [loading, setLoading] = useState(false);

  const prices = { 
    "Zircone": 1200, 
    "E-Max": 1500, 
    "Céramo-Métal": 800, 
    "100% Métal": 500, 
    "Provisoire Résine": 200 
  };
  const basePrice = prices[formData.material] || 0;
  const totalPrice = basePrice + (formData.is_fast_track ? 200 : 0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const payload = {
      ...formData,
      dentist_name: user.name,
      total_price: totalPrice
    };

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) onSuccess();
      else alert("Erreur lors de la soumission");
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div className="grid grid-cols-3 gap-8">
      <div className="col-span-2 bg-white/5 border border-white/10 rounded-2xl p-6">
        <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
          <FileText className="text-violet-400" /> Prescrire
        </h2>
        <form id="dentistForm" onSubmit={handleSubmit} className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Réf. Patient (Anonyme)</label>
            <input type="text" required className="w-full bg-black/40 border border-white/10 rounded-lg p-3" 
              value={formData.patient_ref} onChange={e => setFormData({...formData, patient_ref: e.target.value})} placeholder="PAT-XXXX" />
          </div>
          <div className="col-span-2 bg-black/20 border border-white/5 p-6 rounded-xl mb-2 mt-2">
            <label className="block text-sm font-medium text-slate-300 mb-8 text-center uppercase tracking-widest">
              Odontogramme
            </label>
            <div className="flex flex-col gap-8 items-center overflow-x-auto pb-4">
              {/* Upper Arch */}
              <div className="flex gap-4 items-start">
                {/* Q1 */}
                <div className="flex gap-1 items-start">
                  {[18, 17, 16, 15, 14, 13, 12, 11].map((tooth) => {
                    const isActive = formData.tooth_number === tooth.toString();
                    return (
                      <button key={tooth} type="button" onClick={() => setFormData({ ...formData, tooth_number: tooth.toString() })} className={`group flex flex-col items-center gap-2 ${getTopMargin(tooth)} transition-all`}>
                        <div className="text-xs font-mono transition-colors text-slate-400 group-hover:text-sky-300">
                          {isActive ? <span className="text-white font-bold">{tooth}</span> : tooth}
                        </div>
                        <ToothSvg isTop={true} isActive={isActive} className={getToothWidth(tooth)} />
                      </button>
                    );
                  })}
                </div>
                {/* Midline */}
                <div className="w-px h-16 bg-white/10 mx-2"></div>
                {/* Q2 */}
                <div className="flex gap-1 items-start">
                  {[21, 22, 23, 24, 25, 26, 27, 28].map((tooth) => {
                    const isActive = formData.tooth_number === tooth.toString();
                    return (
                      <button key={tooth} type="button" onClick={() => setFormData({ ...formData, tooth_number: tooth.toString() })} className={`group flex flex-col items-center gap-2 ${getTopMargin(tooth)} transition-all`}>
                        <div className="text-xs font-mono transition-colors text-slate-400 group-hover:text-sky-300">
                          {isActive ? <span className="text-white font-bold">{tooth}</span> : tooth}
                        </div>
                        <ToothSvg isTop={true} isActive={isActive} className={getToothWidth(tooth)} />
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Lower Arch */}
              <div className="flex gap-4 items-end">
                {/* Q4 */}
                <div className="flex gap-1 items-end">
                  {[48, 47, 46, 45, 44, 43, 42, 41].map((tooth) => {
                    const isActive = formData.tooth_number === tooth.toString();
                    return (
                      <button key={tooth} type="button" onClick={() => setFormData({ ...formData, tooth_number: tooth.toString() })} className={`group flex flex-col items-center gap-2 ${getBottomMargin(tooth)} transition-all`}>
                        <ToothSvg isTop={false} isActive={isActive} className={getToothWidth(tooth)} />
                        <div className="text-xs font-mono transition-colors text-slate-400 group-hover:text-sky-300">
                          {isActive ? <span className="text-white font-bold">{tooth}</span> : tooth}
                        </div>
                      </button>
                    );
                  })}
                </div>
                {/* Midline */}
                <div className="w-px h-16 bg-white/10 mx-2"></div>
                {/* Q3 */}
                <div className="flex gap-1 items-end">
                  {[31, 32, 33, 34, 35, 36, 37, 38].map((tooth) => {
                    const isActive = formData.tooth_number === tooth.toString();
                    return (
                      <button key={tooth} type="button" onClick={() => setFormData({ ...formData, tooth_number: tooth.toString() })} className={`group flex flex-col items-center gap-2 ${getBottomMargin(tooth)} transition-all`}>
                        <ToothSvg isTop={false} isActive={isActive} className={getToothWidth(tooth)} />
                        <div className="text-xs font-mono transition-colors text-slate-400 group-hover:text-sky-300">
                          {isActive ? <span className="text-white font-bold">{tooth}</span> : tooth}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
            <div className="mt-6 text-center">
              <span className="text-slate-400 text-sm mr-2">Dent sélectionnée :</span>
              <span className="text-sky-400 font-bold font-mono tracking-wider">{formData.tooth_number || 'Aucune'}</span>
            </div>
          </div>
          {/* Clinical Lightbox */}
          <div className="col-span-2 bg-white/5 border border-white/10 rounded-xl p-4 mb-4">
            <img src={shadeGuideImg} alt="Guide de Teintes VITA" className="w-full object-contain rounded-lg bg-white p-2" />
            <p className="text-xs text-slate-400 mt-2 text-center">Guide VITA Classical - Référence Visuelle</p>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Sélectionner la Teinte</label>
            <select className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-white"
              value={formData.shade} onChange={e => setFormData({...formData, shade: e.target.value})}>
              <optgroup label="Rouges-Bruns (A)">
                <option value="A1">A1</option>
                <option value="A2">A2</option>
                <option value="A3">A3</option>
                <option value="A3.5">A3.5</option>
                <option value="A4">A4</option>
              </optgroup>
              <optgroup label="Jaunes-Rouges (B)">
                <option value="B1">B1</option>
                <option value="B2">B2</option>
                <option value="B3">B3</option>
                <option value="B4">B4</option>
              </optgroup>
              <optgroup label="Gris (C)">
                <option value="C1">C1</option>
                <option value="C2">C2</option>
                <option value="C3">C3</option>
                <option value="C4">C4</option>
              </optgroup>
              <optgroup label="Gris-Rouges (D)">
                <option value="D2">D2</option>
                <option value="D3">D3</option>
                <option value="D4">D4</option>
              </optgroup>
            </select>
          </div>
          <div className="col-span-2">
            <label className="block text-sm text-gray-400 mb-2">Choix du Matériau</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {[
                { name: "Zircone", price: 1200 },
                { name: "E-Max", price: 1500 },
                { name: "Céramo-Métal", price: 800 },
                { name: "100% Métal", price: 500 },
                { name: "Provisoire Résine", price: 200 }
              ].map(mat => (
                <div 
                  key={mat.name}
                  onClick={() => setFormData({...formData, material: mat.name})}
                  className={`flex flex-col items-center justify-center p-4 rounded-xl cursor-pointer transition-all text-center border ${
                    formData.material === mat.name 
                      ? "ring-2 ring-sky-500 bg-sky-900/30 border-sky-500" 
                      : "bg-black/40 border-white/10 hover:border-white/30"
                  }`}
                >
                  <span className="text-white font-semibold mb-1">{mat.name}</span>
                  <span className="text-sm text-sky-400">{mat.price} MAD</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="col-span-2 border border-white/10 rounded-xl p-4 flex items-center justify-between bg-black/20">
            <div>
              <div className="font-medium flex items-center gap-2"><Zap className="w-4 h-4 text-amber-400" /> Fast-Track</div>
              <div className="text-sm text-gray-400">Priorité labo (+200 MAD)</div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" checked={formData.is_fast_track} onChange={e => setFormData({...formData, is_fast_track: e.target.checked})} />
              <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-violet-500"></div>
            </label>
          </div>

          <div className="col-span-2 border border-emerald-500/30 bg-emerald-500/5 rounded-xl p-4 flex items-start gap-3">
            <input type="checkbox" required id="lock" className="mt-1 w-4 h-4 accent-emerald-500" 
              checked={formData.disinfected} onChange={e => setFormData({...formData, disinfected: e.target.checked})} />
            <label htmlFor="lock" className="cursor-pointer">
              <div className="font-medium text-emerald-400">Verrou Sanitaire Obligatoire</div>
              <div className="text-sm text-gray-400">Je confirme que les empreintes ont été désinfectées selon le protocole.</div>
            </label>
          </div>
        </form>
      </div>

      <div className="col-span-1">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 sticky top-24">
          <h3 className="text-lg font-semibold mb-4 text-gray-200">Devis Estimatif</h3>
          <div className="space-y-3 mb-6">
            <div className="flex justify-between text-gray-400"><span>Base ({formData.material})</span><span>{basePrice} MAD</span></div>
            {formData.is_fast_track && <div className="flex justify-between text-amber-400"><span>Option Fast-Track</span><span>+200 MAD</span></div>}
            <div className="border-t border-white/10 pt-3 flex justify-between font-bold text-lg text-white">
              <span>Total</span><span>{totalPrice} MAD</span>
            </div>
          </div>
          <button form="dentistForm" type="submit" disabled={loading} className="w-full bg-violet-600 hover:bg-violet-700 text-white font-semibold py-3 rounded-xl transition-colors shadow-lg disabled:opacity-50">
            {loading ? "Envoi..." : "Envoyer au Labo"}
          </button>
        </div>
      </div>
    </div>
  );
}

function DentistList({ orders }) {
  const statusColors = {
    EN_ATTENTE: "bg-gray-500/20 text-gray-300 border-gray-500/30",
    EN_PRODUCTION: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    PRET_EXPEDITION: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    EN_ROUTE: "bg-purple-500/20 text-purple-300 border-purple-500/30",
    LIVRE: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
  };

  if (orders.length === 0) return <div className="text-gray-400">Aucune commande.</div>;

  return (
    <div className="grid gap-4">
      {orders.map(o => (
        <div key={o.id} className="bg-white/5 border border-white/10 rounded-xl p-5 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <span className="font-bold text-lg">{o.patient_ref}</span>
              <span className="bg-black/50 px-2 py-1 rounded text-xs text-gray-400">Dent {o.tooth_number}</span>
              {o.is_fast_track && <span className="bg-amber-500/20 text-amber-400 px-2 py-1 rounded flex items-center gap-1 text-xs font-medium"><Zap className="w-3 h-3"/> Fast</span>}
            </div>
            <div className="text-sm text-gray-400">{o.material} - Teinte {o.shade}</div>
          </div>
          <div className="text-right">
            <div className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold border ${statusColors[o.status]}`}>
              {o.status.replace("_", " ")}
            </div>
            {o.delivery_date && <div className="text-xs text-gray-400 mt-2 flex items-center justify-end gap-1"><Clock className="w-3 h-3"/> Prévu: {o.delivery_date}</div>}
          </div>
        </div>
      ))}
    </div>
  );
}

function LabPortal({ orders, refresh }) {
  const [activeTab, setActiveTab] = useState('dashboard');

  const patchOrder = async (id, payload) => {
    await fetch(`${API_URL}${id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    refresh();
  };

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex gap-4 border-b border-white/10 pb-0">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 ${activeTab === 'dashboard' ? 'text-sky-400 border-sky-500' : 'text-slate-400 border-transparent hover:text-white hover:border-white/20'}`}
        >
          Dashboard
        </button>
        <button
          onClick={() => setActiveTab('commandes')}
          className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 ${activeTab === 'commandes' ? 'text-sky-400 border-sky-500' : 'text-slate-400 border-transparent hover:text-white hover:border-white/20'}`}
        >
          Commandes
        </button>
        <button
          onClick={() => setActiveTab('facturation')}
          className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 ${activeTab === 'facturation' ? 'text-sky-400 border-sky-500' : 'text-slate-400 border-transparent hover:text-white hover:border-white/20'}`}
        >
          Facturation
        </button>
      </div>

      {/* Tab Content */}
      <div className="pt-2">
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            <div className="grid grid-cols-3 gap-6">
              <div className="bg-white/5 border border-white/10 p-5 rounded-2xl">
                <div className="text-gray-400 text-sm mb-1">Fiches incomplètes bloquées</div>
                <div className="text-2xl font-bold text-emerald-400">74.5%</div>
              </div>
              <div className="bg-white/5 border border-white/10 p-5 rounded-2xl">
                <div className="text-gray-400 text-sm mb-1">Infections bloquées (Verrou)</div>
                <div className="text-2xl font-bold text-emerald-400">83.0%</div>
              </div>
              <div className="bg-white/5 border border-white/10 p-5 rounded-2xl">
                <div className="text-gray-400 text-sm mb-1">Appels inutiles éliminés</div>
                <div className="text-2xl font-bold text-violet-400">93.6%</div>
              </div>
            </div>
            
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Activité Récente</h3>
              <div className="space-y-3">
                <div className="bg-black/30 border border-white/5 p-4 rounded-xl flex items-center justify-between">
                  <span className="text-sm text-slate-300">Connexion sécurisée établie (Dr. Dupont)</span>
                  <span className="text-xs text-slate-500">Il y a 2 min</span>
                </div>
                <div className="bg-black/30 border border-white/5 p-4 rounded-xl flex items-center justify-between">
                  <span className="text-sm text-slate-300">Mise à jour du catalogue des matériaux</span>
                  <span className="text-xs text-slate-500">Il y a 1 heure</span>
                </div>
                <div className="bg-black/30 border border-white/5 p-4 rounded-xl flex items-center justify-between">
                  <span className="text-sm text-slate-300">Synchronisation logistique réussie</span>
                  <span className="text-xs text-slate-500">Il y a 3 heures</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'commandes' && (
          <div className="grid grid-cols-3 gap-6 items-start">
            <div className="bg-black/20 border border-white/5 rounded-2xl p-4">
              <h3 className="font-semibold text-gray-300 mb-4 flex items-center justify-between">
                À Confirmer <span className="bg-white/10 px-2 py-0.5 rounded-full text-xs">{orders.filter(o => o.status === 'EN_ATTENTE').length}</span>
              </h3>
              <div className="space-y-4">
                {orders.filter(o => o.status === 'EN_ATTENTE').map(o => <LabCardNew key={o.id} order={o} onAccept={(date) => patchOrder(o.id, { status: "EN_PRODUCTION", delivery_date: date })} />)}
              </div>
            </div>
            <div className="bg-black/20 border border-white/5 rounded-2xl p-4">
              <h3 className="font-semibold text-gray-300 mb-4 flex items-center justify-between">
                En Production <span className="bg-white/10 px-2 py-0.5 rounded-full text-xs">{orders.filter(o => o.status === 'EN_PRODUCTION').length}</span>
              </h3>
              <div className="space-y-4">
                {orders.filter(o => o.status === 'EN_PRODUCTION').map(o => <LabCardProd key={o.id} order={o} onReady={() => patchOrder(o.id, { status: "PRET_EXPEDITION" })} />)}
              </div>
            </div>
            <div className="bg-black/20 border border-white/5 rounded-2xl p-4">
              <h3 className="font-semibold text-gray-300 mb-4 flex items-center justify-between">
                Prêt (Attente Coursier) <span className="bg-white/10 px-2 py-0.5 rounded-full text-xs">{orders.filter(o => o.status === 'PRET_EXPEDITION').length}</span>
              </h3>
              <div className="space-y-4">
                {orders.filter(o => o.status === 'PRET_EXPEDITION').map(o => (
                  <div key={o.id} className="bg-white/5 border border-white/10 p-4 rounded-xl opacity-75">
                    <div className="font-bold">{o.patient_ref}</div>
                    <div className="text-xs text-gray-400 mt-1">{o.dentist_name}</div>
                    <div className="mt-3 text-xs text-amber-400 border border-amber-400/20 bg-amber-400/10 p-2 rounded flex justify-center">En attente de ramassage</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'facturation' && (
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 overflow-x-auto">
            <h3 className="text-lg font-semibold text-white mb-6">Factures et Règlements</h3>
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs text-slate-500 uppercase bg-black/20 border-b border-white/10">
                <tr>
                  <th className="px-4 py-3 rounded-tl-xl">Réf. Patient</th>
                  <th className="px-4 py-3">Cabinet</th>
                  <th className="px-4 py-3">Montant (MAD)</th>
                  <th className="px-4 py-3">Statut Paiement</th>
                  <th className="px-4 py-3 rounded-tr-xl">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="px-4 py-4 font-medium text-white">PAT-1042</td>
                  <td className="px-4 py-4">Dr. Dupont</td>
                  <td className="px-4 py-4 font-mono">1 200</td>
                  <td className="px-4 py-4">
                    <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs font-semibold">Payé</span>
                  </td>
                  <td className="px-4 py-4">
                    <button className="bg-white/10 hover:bg-white/20 text-white px-3 py-1.5 rounded-lg text-xs transition-colors flex items-center gap-1">
                      PDF
                    </button>
                  </td>
                </tr>
                <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="px-4 py-4 font-medium text-white">PAT-0985</td>
                  <td className="px-4 py-4">Dr. Berrada</td>
                  <td className="px-4 py-4 font-mono">2 400</td>
                  <td className="px-4 py-4">
                    <span className="bg-orange-500/20 text-orange-400 px-2 py-1 rounded text-xs font-semibold">En attente</span>
                  </td>
                  <td className="px-4 py-4">
                    <button className="bg-white/10 hover:bg-white/20 text-white px-3 py-1.5 rounded-lg text-xs transition-colors flex items-center gap-1">
                      PDF
                    </button>
                  </td>
                </tr>
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-4 font-medium text-white">PAT-1102</td>
                  <td className="px-4 py-4">Centre Dentaire Al Noor</td>
                  <td className="px-4 py-4 font-mono">800</td>
                  <td className="px-4 py-4">
                    <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs font-semibold">Payé</span>
                  </td>
                  <td className="px-4 py-4">
                    <button className="bg-white/10 hover:bg-white/20 text-white px-3 py-1.5 rounded-lg text-xs transition-colors flex items-center gap-1">
                      PDF
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function LabCardNew({ order, onAccept }) {
  const [date, setDate] = useState("");
  return (
    <div className="bg-white/10 border border-white/10 p-4 rounded-xl shadow-lg relative overflow-hidden">
      {order.is_fast_track && <div className="absolute top-0 right-0 w-16 h-16"><div className="absolute transform rotate-45 bg-amber-500 text-black text-[10px] font-bold py-1 right-[-35px] top-[10px] w-[100px] text-center">FAST</div></div>}
      <div className="font-bold text-lg">{order.patient_ref}</div>
      <div className="text-sm text-gray-400 mb-2">{order.dentist_name}</div>
      <div className="text-xs text-gray-300 grid grid-cols-2 gap-2 mb-3 bg-black/30 p-2 rounded">
        <div>Dent: {order.tooth_number}</div>
        <div>Teinte: {order.shade}</div>
        <div className="col-span-2">Mat: {order.material}</div>
      </div>
      <div className="flex gap-2">
        <input type="date" className="bg-black/50 border border-white/10 rounded text-xs p-2 flex-1" value={date} onChange={e => setDate(e.target.value)} />
        <button onClick={() => date && onAccept(date)} disabled={!date} className="bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white p-2 rounded flex items-center justify-center">
          <Check className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

function LabCardProd({ order, onReady }) {
  return (
    <div className="bg-white/10 border border-blue-500/30 p-4 rounded-xl shadow-lg">
      <div className="flex justify-between items-start mb-2">
        <div>
          <div className="font-bold text-lg">{order.patient_ref}</div>
          <div className="text-sm text-gray-400">{order.dentist_name}</div>
        </div>
        <div className="text-xs text-blue-300 border border-blue-500/30 bg-blue-500/10 px-2 py-1 rounded">Prévu: {order.delivery_date}</div>
      </div>
      <button onClick={onReady} className="w-full mt-3 bg-white/10 hover:bg-white/20 border border-white/20 py-2 rounded text-sm transition-colors flex items-center justify-center gap-2">
        <Package className="w-4 h-4" /> Générer QR Expédition
      </button>
    </div>
  );
}

function CourierPortal({ orders, refresh }) {
  const [verifyingId, setVerifyingId] = useState(null);
  const [pin, setPin] = useState("");

  const patchOrder = async (id, payload) => {
    await fetch(`${API_URL}${id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    refresh();
  };

  const handleConfirmDelivery = (id) => {
    if (pin.length > 0) {
      patchOrder(id, { status: "LIVRE" });
      setVerifyingId(null);
      setPin("");
    }
  };

  const toPickup = orders.filter(o => o.status === 'PRET_EXPEDITION');
  const inTransit = orders.filter(o => o.status === 'EN_ROUTE');

  return (
    <div className="max-w-md mx-auto bg-black/40 border border-white/5 p-4 rounded-3xl min-h-[800px] shadow-2xl relative overflow-hidden">
      {/* Header */}
      <div className="mb-6 border-b border-white/10 pb-4">
        <h2 className="text-lg font-bold text-white mb-2">Interface Logistique Partenaire</h2>
        <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 px-3 py-1.5 rounded-full w-max">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-xs font-semibold text-green-400">API MedLogistics En Ligne</span>
        </div>
      </div>

      <div className="space-y-6">
        {/* A Collecter */}
        <div>
          <h3 className="text-sm font-semibold text-slate-400 mb-3 uppercase tracking-wider flex items-center gap-2">
            <Package className="w-4 h-4"/> À Collecter ({toPickup.length})
          </h3>
          <div className="space-y-4">
            {toPickup.map(o => (
              <div key={o.id} className="bg-white/5 border border-white/10 rounded-2xl p-4">
                <div className="flex justify-between items-center mb-4">
                  <span className="font-mono text-sm font-bold text-white text-opacity-80">REF: {o.patient_ref}</span>
                  <span className="bg-indigo-500/20 text-indigo-300 text-[10px] px-2 py-0.5 rounded font-bold uppercase">Prioritaire</span>
                </div>
                
                {/* Route */}
                <div className="relative pl-6 mb-5 space-y-4">
                  <div className="absolute left-[11px] top-2 bottom-2 w-0.5 border-l-2 border-dashed border-white/20"></div>
                  <div className="relative">
                    <div className="absolute -left-6 top-0.5 text-base">📍</div>
                    <div className="text-sm font-medium text-white">Point A: Laboratoire</div>
                    <div className="text-xs text-slate-400">Départ - Prêt pour enlèvement</div>
                  </div>
                  <div className="relative">
                    <div className="absolute -left-6 top-0.5 text-base">🏥</div>
                    <div className="text-sm font-medium text-white">Point B: {o.dentist_name}</div>
                    <div className="text-xs text-slate-400">Destination - Cabinet Dentaire</div>
                  </div>
                </div>

                <button 
                  onClick={() => patchOrder(o.id, { status: "EN_ROUTE" })} 
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl py-3 flex justify-center items-center gap-2 font-semibold transition-colors shadow-lg"
                >
                  📷 Scanner QR d'Enlèvement
                </button>
              </div>
            ))}
            {toPickup.length === 0 && <div className="text-sm text-center text-slate-500 py-4">Aucun colis à collecter.</div>}
          </div>
        </div>

        {/* En Cours de Livraison */}
        <div>
          <h3 className="text-sm font-semibold text-slate-400 mb-3 uppercase tracking-wider flex items-center gap-2">
            <Truck className="w-4 h-4"/> En Cours de Livraison ({inTransit.length})
          </h3>
          <div className="space-y-4">
            {inTransit.map(o => (
              <div key={o.id} className="bg-white/5 border border-emerald-500/20 rounded-2xl p-4">
                <div className="flex justify-between items-center mb-4">
                  <span className="font-mono text-sm font-bold text-white text-opacity-80">REF: {o.patient_ref}</span>
                  <span className="bg-amber-500/20 text-amber-300 text-[10px] px-2 py-0.5 rounded font-bold uppercase animate-pulse">En Transit</span>
                </div>
                
                {/* Route */}
                <div className="relative pl-6 mb-5 space-y-4">
                  <div className="absolute left-[11px] top-2 bottom-2 w-0.5 border-l-2 border-dashed border-emerald-500/30"></div>
                  <div className="relative opacity-50">
                    <div className="absolute -left-6 top-0.5 text-base">📍</div>
                    <div className="text-sm font-medium text-white line-through">Point A: Laboratoire</div>
                  </div>
                  <div className="relative">
                    <div className="absolute -left-6 top-0.5 text-base">🏥</div>
                    <div className="text-sm font-medium text-emerald-400">Point B: {o.dentist_name}</div>
                    <div className="text-xs text-slate-400">Approche imminente</div>
                  </div>
                </div>

                {verifyingId === o.id ? (
                  <div className="bg-black/50 border border-white/10 p-3 rounded-xl flex gap-2 animate-in fade-in slide-in-from-bottom-2">
                    <input 
                      type="text" 
                      placeholder="Code PIN (Ex: 1234)" 
                      value={pin}
                      onChange={e => setPin(e.target.value)}
                      className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
                      autoFocus
                    />
                    <button 
                      onClick={() => handleConfirmDelivery(o.id)}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors"
                    >
                      Confirmer
                    </button>
                    <button 
                      onClick={() => { setVerifyingId(null); setPin(""); }}
                      className="bg-white/10 hover:bg-white/20 text-slate-300 font-semibold px-3 py-2 rounded-lg text-sm transition-colors"
                    >
                      X
                    </button>
                  </div>
                ) : (
                  <button 
                    onClick={() => setVerifyingId(o.id)} 
                    className="w-full bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl py-3 flex justify-center items-center gap-2 font-semibold transition-colors shadow-[0_0_15px_rgba(5,150,105,0.3)]"
                  >
                    ✅ Valider la Livraison
                  </button>
                )}
              </div>
            ))}
            {inTransit.length === 0 && <div className="text-sm text-center text-slate-500 py-4">Aucune livraison en cours.</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
