import { useState } from 'react';
import { ArrowRight, CheckCircle, Clock, Search, Save } from 'lucide-react';

const methods = { CFAO: 'CFAO / usinage CNC', IMPRESSION_3D: 'Impression 3D', CONVENTIONNEL: 'Fabrication conventionnelle' };
const phases = {
  reception: ['ANALYSE_DEMANDE', 'ATTENTE_RAMASSAGE', 'EN_ROUTE_LABO', 'A_CONFIRMER', 'CONTROLE_DOSSIER'],
  planning: ['PLANIFICATION'],
  technical: ['SALLE_CAO', 'PREPARATION_CNC', 'USINAGE_CNC', 'TRAITEMENT_THERMIQUE', 'FRITTAGE_9H', 'PREPARATION_3D', 'IMPRESSION_3D', 'LAVAGE_SECHAGE', 'POST_POLYMERISATION', 'MODELE_TRAVAIL', 'MODELAGE', 'FABRICATION_MANUELLE', 'FINITION'],
  shipping: ['CONTROLE_QUALITE', 'CONDITIONNEMENT', 'PRET_EXPEDITION', 'EN_ROUTE_CABINET'],
  delivered: ['LIVRE'],
};
const phaseLabels = { all: 'En cours', reception: 'Analyse et réception', planning: 'Planification', technical: 'Fabrication', shipping: 'Contrôle et expédition', delivered: 'Livrées' };
const instructions = {
  ANALYSE_DEMANDE: 'Vérifier la prescription, la dent, la teinte, le matériau demandé et les informations nécessaires avant d’accepter la demande.',
  ATTENTE_RAMASSAGE: 'Analyse validée. Le coursier doit récupérer l’empreinte physique au cabinet.',
  EN_ROUTE_LABO: 'L’empreinte est en cours d’acheminement. Le coursier confirmera son dépôt au laboratoire.',
  A_CONFIRMER: 'Enregistrer la réception des empreintes ou fichiers et vérifier leur conformité et la désinfection déclarée.',
  CONTROLE_DOSSIER: 'Contrôler la complétude des fichiers, modèles et informations du dossier. Consigner les précisions demandées au cabinet dans les notes.',
  PLANIFICATION: 'Choisir la méthode de fabrication et fixer la livraison prévue. Le parcours technique s’adaptera à ce choix.',
  SALLE_CAO: 'Réaliser la conception numérique et valider le fichier de fabrication.',
  PREPARATION_CNC: 'Préparer la FAO, le placement dans le brut et le parcours d’usinage.',
  USINAGE_CNC: 'Suivre l’usinage selon le dossier technique de la commande.',
  TRAITEMENT_THERMIQUE: 'Effectuer le traitement prévu selon le protocole du matériau et de l’appareil.',
  FRITTAGE_9H: 'Terminer le traitement du dossier déjà engagé dans l’ancien parcours.',
  PREPARATION_3D: 'Préparer l’orientation, les supports et le plateau de fabrication.',
  IMPRESSION_3D: 'Réaliser l’impression avec le matériau et le profil validés pour ce travail.',
  LAVAGE_SECHAGE: 'Réaliser le lavage et le séchage selon le protocole du matériau.',
  POST_POLYMERISATION: 'Réaliser la post-polymérisation selon le protocole du matériau.',
  MODELE_TRAVAIL: 'Préparer et contrôler le modèle de travail.',
  MODELAGE: 'Préparer la maquette et les formes selon la prescription.',
  FABRICATION_MANUELLE: 'Réaliser la fabrication conventionnelle conformément au dossier technique.',
  FINITION: 'Effectuer les finitions et la caractérisation prévues pour la restauration.',
  CONTROLE_QUALITE: 'Contrôler la conformité à la prescription, l’ajustage, les contacts, l’occlusion, la teinte et la traçabilité.',
  CONDITIONNEMENT: 'Préparer le conditionnement, les documents et l’identification de la commande.',
  PRET_EXPEDITION: 'Commande terminée, disponible pour le ramassage du coursier.',
  EN_ROUTE_CABINET: 'Le coursier livre la commande au cabinet.',
  LIVRE: 'Commande livrée au cabinet.',
};
const controlClass = 'w-full rounded-xl border border-white/15 bg-[#171321] px-3 py-2 text-sm text-white outline-none focus:border-sky-400 disabled:opacity-60';

export default function ProductionWorkflow({ orders, patchOrder }) {
  const [phase, setPhase] = useState('all');
  const [query, setQuery] = useState('');
  const visible = orders.filter(order => (phase === 'all' ? order.status !== 'LIVRE' : phases[phase].includes(order.status)) && `${order.patient_ref} ${order.dentist_name} ${order.material}`.toLowerCase().includes(query.toLowerCase()));
  return <div className="space-y-6">
    <div><h2 className="text-2xl font-semibold">Parcours de fabrication</h2><p className="mt-2 text-sm text-slate-400">Analyse → réception → contrôle du dossier → planification → fabrication adaptée → contrôle qualité → expédition.</p></div>
    <div className="rounded-2xl border border-sky-400/20 bg-sky-400/5 p-4 text-sm text-slate-300">Trois méthodes : CFAO / usinage CNC, impression 3D et fabrication conventionnelle. Les paramètres et traitements sont définis par le laboratoire selon le matériau et les équipements.</div>
    <div className="flex flex-wrap gap-2">{Object.entries(phaseLabels).map(([key, label]) => <button key={key} onClick={() => setPhase(key)} aria-pressed={phase === key} className={`rounded-xl border px-3 py-2 text-sm ${phase === key ? 'border-sky-400/30 bg-sky-500/15 text-sky-300' : 'border-white/10 text-slate-400 hover:text-white'}`}>{label} <span className="ml-1 text-xs">{orders.filter(order => key === 'all' ? order.status !== 'LIVRE' : phases[key].includes(order.status)).length}</span></button>)}</div>
    <div className="relative"><Search className="absolute left-3 top-3 h-4 w-4 text-slate-500" /><input className={`${controlClass} pl-10`} aria-label="Rechercher une commande" placeholder="Rechercher une référence patient, un cabinet, un matériau…" value={query} onChange={event => setQuery(event.target.value)} /></div>
    {!visible.length && <p className="rounded-2xl border border-white/10 py-12 text-center text-sm text-slate-400">Aucune commande dans cette vue.</p>}
    <div className="space-y-5">{visible.map(order => <ProductionCard key={`${order.id}:${order.updated_at}`} order={order} patchOrder={patchOrder} />)}</div>
  </div>;
}

export function ProductionCard({ order, patchOrder, diagram = false }) {
  const [method, setMethod] = useState(order.production_method || '');
  const [treatment, setTreatment] = useState(order.thermal_treatment || 'AUCUN');
  const [date, setDate] = useState(order.delivery_date || '');
  const [notes, setNotes] = useState(order.technical_notes || '');
  const [analysis, setAnalysis] = useState(order.analysis_validated);
  const [reception, setReception] = useState(order.reception_validated);
  const [quality, setQuality] = useState(order.quality_validated);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [paused, setPaused] = useState(order.is_paused || false);
  const [pauseReason, setPauseReason] = useState(order.pause_reason || '');
  const [issues, setIssues] = useState(order.current_issues || '');
  const [dragging, setDragging] = useState(false);
  const steps = order.workflow_steps || [];
  const current = steps.findIndex(step => step.key === order.status);
  const planning = order.status === 'PLANIFICATION';
  const courier = ['ATTENTE_RAMASSAGE', 'EN_ROUTE_LABO', 'PRET_EXPEDITION', 'EN_ROUTE_CABINET', 'LIVRE'].includes(order.status);
  const next = planning ? method === 'CONVENTIONNEL' ? 'MODELE_TRAVAIL' : method ? 'SALLE_CAO' : null : order.next_status;
  const nextLabel = steps.find(step => step.key === next)?.label || (next === 'SALLE_CAO' ? 'Conception numérique / CAO' : next === 'MODELE_TRAVAIL' ? 'Préparation du modèle de travail' : next);
  const canAdvance = order.accepted && !paused && next && !courier && (order.status !== 'ANALYSE_DEMANDE' || analysis) && (order.status !== 'A_CONFIRMER' || reception) && (order.status !== 'CONTROLE_QUALITE' || quality) && (!planning || (method && date));

  async function save(advance) {
    if (advance && !canAdvance) return;
    setBusy(true); setError(''); setNotice('');
    const payload = { technical_notes: notes, delivery_date: date || null, analysis_validated: analysis, reception_validated: reception, quality_validated: quality, is_paused: paused, pause_reason: pauseReason, current_issues: issues };
    if (planning) { payload.production_method = method; payload.thermal_treatment = method === 'CFAO' ? treatment : 'AUCUN'; }
    if (advance) payload.status = next;
    try { await patchOrder(order.id, payload); setNotice('Enregistrement effectué.'); }
    catch (err) { setError(err.response?.data ? Object.values(err.response.data).flat().join(' ') : 'Enregistrement impossible. Vérifiez la connexion.'); }
    finally { setBusy(false); }
  }
  return <article aria-label={`Commande ${order.patient_ref}`} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 space-y-5">
    <div className="flex flex-wrap items-start justify-between gap-4"><div><div className="flex items-center gap-3"><h3 className="text-lg font-semibold">{order.patient_ref}</h3>{order.is_fast_track && <span className="rounded-full bg-amber-400/10 px-2 py-1 text-xs text-amber-300">Urgent</span>}</div><p className="mt-1 text-sm text-slate-400">{order.dentist_name} · Dent {order.tooth_number} · {order.material} · Teinte {order.shade}</p><p className="mt-1 text-xs text-slate-500">{order.impression_type === 'PHYSIQUE' ? 'Empreinte physique' : `Empreinte numérique${order.stl_file_name ? ` · ${order.stl_file_name}` : ''}`} · {methods[order.production_method] || 'Méthode à planifier'}</p></div><span className="rounded-xl border border-sky-400/20 bg-sky-400/10 px-3 py-2 text-sm text-sky-300">{order.status_label || order.status}</span></div>
    {!diagram && <details><summary className="cursor-pointer text-sm text-sky-300">Voir les étapes du parcours ({Math.max(current + 1, 1)} / {steps.length})</summary><ol className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">{steps.map((step, index) => <li key={step.key} aria-current={step.key === order.status ? 'step' : undefined} className={`rounded-lg border p-2 text-xs ${index === current ? 'border-sky-400/40 bg-sky-400/10 text-sky-200' : index < current ? 'border-emerald-400/10 text-emerald-300' : 'border-white/5 text-slate-500'}`}>{index + 1}. {step.label}</li>)}</ol>{!order.production_method && <p className="mt-3 text-xs text-slate-500">Les étapes techniques s’afficheront après le choix de la méthode.</p>}</details>}
    {diagram && <section aria-label="Diagramme des étapes" className="rounded-2xl border border-white/10 bg-black/20 p-4 space-y-4">
      <div><h4 className="font-medium">Diagramme de la commande</h4><p className="mt-1 text-xs text-slate-400">Glissez la fiche de la commande sur l’étape suivante. Les validations ci-dessous s’appliquent aussi au glisser-déposer. Les étapes du coursier se mettent à jour dans son portail.</p></div>
      {planning && method !== order.production_method && <p className="text-xs text-sky-300">Enregistrez les informations après le choix de la méthode pour afficher les étapes techniques correspondantes dans le diagramme.</p>}
      <div draggable={!busy && !paused && !courier} onDragStart={event => { event.dataTransfer.setData('text/plain', order.id); event.dataTransfer.effectAllowed = 'move'; setDragging(true); }} onDragEnd={() => setDragging(false)} aria-label={`Déplacer ${order.patient_ref}`} className={`w-fit rounded-xl border border-sky-400/30 bg-sky-400/10 px-4 py-3 text-sm text-sky-200 ${paused || courier ? 'opacity-50' : 'cursor-grab active:cursor-grabbing'}`}>⠿ {order.patient_ref} · {order.status_label}{paused ? ' · En pause' : ''}</div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">{steps.map((step, index) => {
        const validTarget = step.key === next && canAdvance;
        return <div key={step.key} data-stage={step.key} onDragOver={event => { if (validTarget && !busy) { event.preventDefault(); event.dataTransfer.dropEffect = 'move'; } }} onDrop={event => { event.preventDefault(); setDragging(false); if (event.dataTransfer.getData('text/plain') === String(order.id) && validTarget && !busy) save(true); }} className={`relative rounded-xl border p-4 ${step.key === order.status ? 'border-sky-400/50 bg-sky-400/10' : validTarget ? `border-dashed border-emerald-400/50 ${dragging ? 'bg-emerald-400/20 ring-2 ring-emerald-400/40' : 'bg-emerald-400/5'}` : index < current ? 'border-emerald-400/15 bg-emerald-400/5' : 'border-white/10 bg-white/[0.02]'}`}>
          <span className="text-[10px] uppercase tracking-widest text-slate-500">Étape {index + 1} {index < steps.length - 1 ? '→' : ''}</span><p className={`mt-2 text-sm ${step.key === order.status ? 'text-sky-200' : index < current ? 'text-emerald-300' : 'text-slate-300'}`}>{step.label}</p><p className="mt-2 text-[10px] text-slate-500">{step.key === order.status ? 'Tâche actuelle' : index < current ? 'Étape passée' : validTarget ? 'Déposez la commande ici' : 'À venir'}</p>
        </div>;
      })}</div>
    </section>}
    <div className="rounded-xl border border-white/10 bg-black/20 p-4"><p className="flex items-center gap-2 text-sm font-medium"><Clock className="h-4 w-4 text-sky-400" />Étape actuelle : {order.status_label}</p><p className="mt-2 text-sm leading-relaxed text-slate-400">{instructions[order.status]}</p></div>
    <fieldset disabled={busy} className="space-y-4">
      <div className="rounded-xl border border-amber-400/20 bg-amber-400/5 p-4 space-y-3"><label className="flex items-center gap-3 text-sm text-amber-200"><input type="checkbox" checked={paused} onChange={event => setPaused(event.target.checked)} />Mettre la commande en pause</label>{paused && <label className="block space-y-2 text-sm text-slate-300"><span>Motif de la pause *</span><textarea aria-label="Motif de la pause" className={controlClass} value={pauseReason} onChange={event => setPauseReason(event.target.value)} /></label>}<label className="block space-y-2 text-sm text-slate-300"><span>Problèmes actuels</span><textarea aria-label="Problèmes actuels" rows={2} className={controlClass} value={issues} onChange={event => setIssues(event.target.value)} placeholder="Éléments manquants, attente de réponse du cabinet…" /></label></div>
      {planning && <div className="grid gap-4 md:grid-cols-2"><label className="space-y-2 text-sm text-slate-300"><span>Méthode de fabrication *</span><select aria-label="Méthode de fabrication" className={controlClass} value={method} onChange={event => setMethod(event.target.value)}><option value="">Choisir une méthode</option>{Object.entries(methods).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>{method === 'CFAO' && <label className="space-y-2 text-sm text-slate-300"><span>Traitement après usinage</span><select aria-label="Traitement après usinage" className={controlClass} value={treatment} onChange={event => setTreatment(event.target.value)}><option value="AUCUN">Sans traitement thermique</option><option value="FRITTAGE">Frittage</option><option value="CRISTALLISATION">Cristallisation</option><option value="CUISSON">Cuisson</option></select></label>}</div>}
      <div className="grid gap-4 md:grid-cols-[220px_1fr]"><label className="space-y-2 text-sm text-slate-300"><span>Livraison prévue{planning ? ' *' : ''}</span><input aria-label="Livraison prévue" type="date" className={controlClass} value={date} onChange={event => setDate(event.target.value)} /></label><label className="space-y-2 text-sm text-slate-300"><span>Notes du dossier / consignes techniques</span><textarea aria-label="Notes du dossier" rows={2} className={controlClass} value={notes} onChange={event => setNotes(event.target.value)} /></label></div>
      {order.status === 'ANALYSE_DEMANDE' && <label className="flex items-center gap-3 text-sm text-slate-300"><input type="checkbox" checked={analysis} onChange={event => setAnalysis(event.target.checked)} className="accent-sky-400" />Analyse de la demande validée</label>}
      {order.status === 'A_CONFIRMER' && <label className="flex items-center gap-3 text-sm text-slate-300"><input type="checkbox" checked={reception} onChange={event => setReception(event.target.checked)} className="accent-sky-400" />Réception et conformité des éléments confirmées</label>}
      {order.status === 'CONTROLE_QUALITE' && <label className="flex items-center gap-3 text-sm text-slate-300"><input type="checkbox" checked={quality} onChange={event => setQuality(event.target.checked)} className="accent-sky-400" />Contrôle qualité final validé</label>}
    </fieldset>
    {error && <p role="alert" className="rounded-xl bg-red-500/10 p-3 text-sm text-red-300">{error}</p>}{notice && <p role="status" className="text-sm text-emerald-300">{notice}</p>}
    <div className="flex flex-wrap justify-end gap-3"><button disabled={busy} onClick={() => save(false)} className="inline-flex items-center gap-2 rounded-xl border border-white/15 px-4 py-2 text-sm text-slate-300 disabled:opacity-50"><Save className="h-4 w-4" />Enregistrer les informations</button>{!courier && <button disabled={busy || !canAdvance} onClick={() => save(true)} className="inline-flex items-center gap-2 rounded-xl bg-sky-500 px-4 py-2 text-sm font-medium disabled:opacity-40"><ArrowRight className="h-4 w-4" />{busy ? 'Enregistrement…' : `Valider → ${nextLabel || 'Choisir la méthode'}`}</button>}{order.status === 'LIVRE' && <span className="flex items-center gap-2 text-sm text-emerald-300"><CheckCircle className="h-4 w-4" />Livraison terminée</span>}</div>
    <details><summary className="cursor-pointer text-xs text-slate-500">Historique des étapes ({order.workflow_history?.length || 0})</summary><ol className="mt-3 space-y-2 text-xs text-slate-400">{order.workflow_history?.map((event, index) => <li key={`${event.at}-${index}`}>{new Date(event.at).toLocaleString('fr-FR')} · {steps.find(step => step.key === event.status)?.label || event.status}</li>)}</ol></details>
  </article>;
}
