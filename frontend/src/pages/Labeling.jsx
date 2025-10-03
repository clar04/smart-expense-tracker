import { useEffect, useState } from "react";
import { api } from "../api/client";
import { fmtRp } from "../utils/format";

const idOf = (r) => r?.id || r?._id || r?._id?.$oid;

export default function Labeling() {
  const [rows, setRows] = useState([]);
  const [cats, setCats] = useState([]);
  const [error, setError] = useState(null);

    const load = async () => {
    try {
      const [u, c] = await Promise.all([
        api.get("/labeling/unlabeled", { params: { limit: 50 } }),
        api.get("/categories"),
      ]);
      setRows(u.data.items || []);
      setCats(c.data.items || []);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message);
    }
  };
  useEffect(() => { load(); }, []);

  const setLabel = async (rawId, category_id) => {
    const tid = idOf({ id: rawId }) || rawId; // jaga-jaga
    if (!tid) { setError("Invalid transaction id"); return; }
    await api.post(`/labeling/${tid}`, { category_id });
    setRows(prev => prev.filter(x => idOf(x) !== tid));
  };

  return (
    <div className="card p-4">
      {error && <div className="mb-3 p-2 text-sm bg-rose-50 text-rose-700 border border-rose-200 rounded">{String(error)}</div>}
      <div className="mb-3 text-sm text-slate-600">Transactions without category</div>
      <div className="space-y-2">
        {rows.map(r => {
          const rid = idOf(r);
          return (
            <div key={rid || Math.random()} className="border rounded-lg p-3 flex items-center justify-between">
              <div>
                <div className="font-medium">{r.description}</div>
                <div className="text-xs text-slate-500">{r.date} • {r.merchant || "-"} • {fmtRp(r.amount)}</div>
              </div>
              <div className="flex gap-2">
                {cats.map(c => (
                  <button key={c.id || c._id} className="btn btn-ghost" onClick={()=>setLabel(rid, c.id)}>{c.name}</button>
                ))}
                <button className="btn btn-ghost" onClick={()=>setLabel(rid, null)}>Clear</button>
              </div>
            </div>
          );
        })}
        {rows.length === 0 && <div className="text-sm text-slate-500">No unlabeled transactions 🎉</div>}
      </div>
    </div>
  );
}