import { useEffect, useState } from "react";
import { api } from "../api/client";
import { fmtRp } from "../utils/format";

const TrashIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
    <path fillRule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.58.22-2.365.468a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75a1.25 1.25 0 00-1.25-1.25h-2.5A1.25 1.25 0 007.5 3.75v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clipRule="evenodd" />
  </svg>
);

function AddForm({ onSaved, onError }) {
  const [form, setForm] = useState({
    date: new Date().toISOString().slice(0, 10),
    description: "",
    amount: "",
    merchant: "",
    category_id: "",
  });
  const [cats, setCats] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/categories")
      .then(r => setCats(r.data.items || []))
      .catch(err => onError?.(err));
  }, []);

  const onChange = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        date: form.date,
        description: form.description,
        amount: Number(form.amount),
        merchant: form.merchant || null,
        category_id: form.category_id || null,
        source: "manual",
      };
      await api.post("/transactions", payload);
      setForm(f => ({ ...f, description: "", amount: "", merchant: "" }));
      onSaved?.();
    } catch (e) {
      onError?.(e);
    } finally { setLoading(false); }
  };

  return (
    <div className="card p-5">
      <h3 className="text-lg font-semibold mb-4 text-slate-700">Add New Transaction</h3>
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="label">Date</label>
            <input className="input" type="date" name="date" value={form.date} onChange={onChange} required />
          </div>
          <div>
            <label className="label">Amount</label>
            <input className="input" type="number" step="100" name="amount" value={form.amount} onChange={onChange} required placeholder="e.g., 50000" />
          </div>
          <div>
            <label className="label">Category</label>
            <select className="input" name="category_id" value={form.category_id} onChange={onChange}>
              <option value="">— Select Category —</option>
              {cats.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label">Description</label>
            <input className="input" name="description" value={form.description} onChange={onChange} required placeholder="e.g., Coffee with friend" />
          </div>
          <div>
            <label className="label">Merchant (optional)</label>
            <input className="input" name="merchant" value={form.merchant} onChange={onChange} placeholder="e.g., Starbucks" />
          </div>
        </div>
        <div>
          <button className="btn btn-primary" disabled={loading}>{loading ? "Saving..." : "Save Transaction"}</button>
        </div>
      </form>
    </div>
  );
}

export default function Transactions() {
  const [rows, setRows] = useState([]);
  const [q, setQ] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [error, setError] = useState(null);
  const [loadingList, setLoadingList] = useState(false);

  const load = async () => {
    setLoadingList(true);
    setError(null);
    try {
      const params = { limit: 20 };
      if (q) params.q = q; if (start) params.start = start; if (end) params.end = end;
      const r = await api.get("/transactions", { params });
      setRows(r.data.items || []);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Failed to load");
      setRows([]);  // clear to avoid stale
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => { load(); }, []);

  const del = async (id) => {
    try {
      await api.delete(`/transactions/${id}`);
      load();
    } catch (e) {
      setError(e?.response?.data?.detail || e.message);
    }
  };

  return (
    <div className="space-y-6">
      <AddForm onSaved={load} onError={(e) => setError(e?.response?.data?.detail || e.message)} />

      {error && (
        <div className="card p-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg">
          Error: {String(error)}
        </div>
      )}

      <div className="card p-5">
        <div className="flex flex-wrap gap-3 items-center mb-4 pb-4 border-b">
          <h3 className="text-lg font-semibold text-slate-700 flex-1">History</h3>
          <input className="input w-48" placeholder="Search description..." value={q} onChange={e => setQ(e.target.value)} />
          <input className="input" type="date" value={start} onChange={e => setStart(e.target.value)} />
          <input className="input" type="date" value={end} onChange={e => setEnd(e.target.value)} />
          <button className="btn btn-secondary" onClick={load} disabled={loadingList}>{loadingList ? "Loading..." : "Filter"}</button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-slate-600">
              <tr>
                <th className="p-2 font-semibold">Date</th>
                <th className="p-2 font-semibold">Description</th>
                <th className="p-2 font-semibold">Merchant</th>
                <th className="p-2 font-semibold text-right">Amount</th>
                <th className="p-2 font-semibold text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(r => (
                <tr key={r.id} className="border-t border-slate-200 hover:bg-slate-50">
                  <td className="p-3 whitespace-nowrap">{r.date}</td>
                  <td className="p-3">{r.description}</td>
                  <td className="p-3 text-slate-500">{r.merchant || "—"}</td>
                  <td className="p-3 text-right font-mono">{fmtRp(r.amount)}</td>
                  <td className="p-3 text-center">
                    <button className="btn btn-icon text-slate-500 hover:text-red-600" onClick={() => del(r.id)}>
                      <TrashIcon />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 && !loadingList && (
            <div className="text-center p-6 text-slate-500">No transactions found.</div>
          )}
          {loadingList && (
            <div className="text-center p-6 text-slate-500">Loading data...</div>
          )}
        </div>
      </div>
    </div>
  );
}
