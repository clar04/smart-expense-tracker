import { useEffect, useState } from "react";
import { api } from "../api/client";
import { fmtRp } from "../utils/format";

export default function Reports() {
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [rows, setRows] = useState([]);
  const [totals, setTotals] = useState({ grand_total: 0, tx_count: 0 });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (start) params.start = start; if (end) params.end = end;
      const r = await api.get("/reports/summary", { params });
      setRows(r.data.items || []);
      setTotals(r.data.totals || { grand_total: 0, tx_count: 0 });
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Failed to load");
      setRows([]);
      setTotals({ grand_total: 0, tx_count: 0 });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-6">
      <div className="card p-4">
        <div className="flex flex-wrap gap-3 items-center">
            <h3 className="text-lg font-semibold text-slate-700 flex-1">Reports</h3>
            <div>
              <label className="label text-xs">Start Date</label>
              <input className="input" type="date" value={start} onChange={e => setStart(e.target.value)} />
            </div>
            <div>
              <label className="label text-xs">End Date</label>
              <input className="input" type="date" value={end} onChange={e => setEnd(e.target.value)} />
            </div>
            <div className="self-end">
              <button className="btn btn-secondary" onClick={load} disabled={loading}>{loading ? "Loading..." : "Refresh"}</button>
            </div>
        </div>
      </div>
      
      {error && <div className="card p-3 text-sm text-red-700 bg-red-50 border-red-200">{String(error)}</div>}

      <div className="card p-5">
        <div className="flex items-center justify-between mb-4 pb-4 border-b">
          <div className="font-semibold text-slate-700">Summary by Category</div>
          <div className="text-sm text-slate-600 text-right">
            <div>Total: <span className="font-semibold text-slate-800">{fmtRp(totals.grand_total)}</span></div>
            <div className="text-xs text-slate-500">{totals.tx_count} transactions</div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-slate-600">
              <tr>
                <th className="p-2 font-semibold">Category</th>
                <th className="p-2 font-semibold text-right">Transactions</th>
                <th className="p-2 font-semibold text-right">Total Amount</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} className="border-t border-slate-200 hover:bg-slate-50">
                  <td className="p-3 font-medium">{r.category_name}</td>
                  <td className="p-3 text-right">{r.count}</td>
                  <td className="p-3 text-right font-mono">{fmtRp(r.total)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 && !loading && (
            <div className="text-center p-6 text-slate-500">No data for the selected period.</div>
          )}
          {loading && (
            <div className="text-center p-6 text-slate-500">Generating report...</div>
          )}
        </div>
      </div>
    </div>
  );
}
