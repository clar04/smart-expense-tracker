import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Health() {
  const [ok, setOk] = useState(null);
  useEffect(() => { api.get("/health").then(r => setOk(r.data.ok)).catch(() => setOk(false)); }, []);

  const getStatus = () => {
    if (ok === null) {
      return { text: "Checking...", color: "text-slate-600", dot: "bg-slate-400 animate-pulse" };
    }
    if (ok) {
      return { text: "All Systems Operational", color: "text-emerald-600", dot: "bg-emerald-500" };
    }
    return { text: "Backend Not Responding", color: "text-red-600", dot: "bg-red-500" };
  };

  const status = getStatus();

  return (
    <div className="card p-5">
      <h3 className="font-semibold text-slate-700 mb-2">Backend Status</h3>
      <div className="flex items-center gap-3">
        <div className={`w-3 h-3 rounded-full ${status.dot}`}></div>
        <div className={`text-lg font-semibold ${status.color}`}>
          {status.text}
        </div>
      </div>
    </div>
  );
}