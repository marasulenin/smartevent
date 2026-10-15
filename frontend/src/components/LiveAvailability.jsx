import { useEffect, useState } from 'react';
import api from '../services/api';

// Use inside EventDetails: <LiveAvailability eventId={event.id} onUpdate={setEvent} />
export default function LiveAvailability({ eventId, onUpdate }) {
  const [available, setAvailable] = useState(null); const [connected, setConnected] = useState(false);
  useEffect(() => {
    let socket; let stopped=false; let poll;
    const apply = data => { if(data && typeof data.available_tickets==='number'){setAvailable(data.available_tickets);onUpdate?.(old=>old?{...old,...data}:old);} };
    try { const base=api.defaults.baseURL.replace(/^http/,'ws').replace(/\/api\/v1\/?$/,''); socket=new WebSocket(`${base}/api/v1/ws/events/${eventId}/availability`); socket.onopen=()=>setConnected(true); socket.onmessage=e=>{try{apply(JSON.parse(e.data))}catch{}}; socket.onclose=()=>setConnected(false); socket.onerror=()=>setConnected(false); } catch { /* fallback polling below */ }
    poll=setInterval(async()=>{if(stopped)return;try{const r=await api.get(`/events/${eventId}/availability`);apply(r.data)}catch{}},5000);
    return ()=>{stopped=true;clearInterval(poll);socket?.close()};
  },[eventId,onUpdate]);
  if(available===null)return <p>Checking live availability…</p>;
  return <p aria-live="polite">🎟️ {available} tickets available {available<=0?'— Sold out':''} <small>({connected?'live updates':'refreshing every 5 seconds'})</small></p>;
}
