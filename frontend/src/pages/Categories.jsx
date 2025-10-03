import { useEffect, useState } from "react";
import { api } from "../api/client";

const TrashIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
      <path fillRule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.58.22-2.365.468a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75a1.25 1.25 0 00-1.25-1.25h-2.5A1.25 1.25 0 007.5 3.75v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clipRule="evenodd" />
    </svg>
  );

export default function Categories() {
const [rows, setRows] = useState([]);
const [name, setName] = useState("");
const [loading, setLoading] = useState(false);

const load = async () => {
  setLoading(true);
  const r = await api.get("/categories");
  setRows(r.data.items || []);
  setLoading(false);
};
useEffect(() => { load(); }, []);

const createCat = async (e) => {
    e.preventDefault();
    if (!name.trim() || loading) return;
    setLoading(true);
    try {
      await api.post("/categories", { name });
      setName("");
      load();
    } finally {
      setLoading(false);
    }
  };
  const del = async (id) => {
    if (!confirm("Delete category? Transactions will be detached.")) return;
    setLoading(true);
    try {
      await api.delete(`/categories/${id}`, { params: { force: true } });
      load();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-1">
        <form onSubmit={createCat} className="card p-5 space-y-4">
          <h3 className="font-semibold text-slate-700">New Category</h3>
          <div>
            <label className="label">Category Name</label>
            <input className="input" value={name} onChange={e => setName(e.target.value)} placeholder="e.g., Groceries" />
          </div>
          <button className="btn btn-primary w-full" disabled={loading}>
            {loading ? "Adding..." : "Add Category"}
          </button>
        </form>
      </div>

      <div className="md:col-span-2 card p-5">
        <h3 className="font-semibold text-slate-700 mb-4">Existing Categories</h3>
        {rows.length > 0 ? (
          <ul className="divide-y divide-slate-200">
            {rows.map(c => (
              <li key={c.id} className="py-2.5 flex items-center justify-between hover:bg-slate-50 -mx-3 px-3 rounded-lg">
                <span className="text-slate-800">{c.name}</span>
                <button className="btn btn-icon text-slate-500 hover:text-red-600" onClick={() => del(c.id)}>
                    <TrashIcon/>
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-sm text-center py-6 text-slate-500">No categories created yet.</div>
        )}
      </div>
    </div>
  );
}