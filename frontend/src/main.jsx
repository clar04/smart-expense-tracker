import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import "./index.css";
import Health from "./pages/Health.jsx";
import Transactions from "./pages/transactions.jsx";
import Categories from "./pages/categories.jsx";
import Labeling from "./pages/Labeling.jsx";
import Reports from "./pages/Reports.jsx";

// Helper untuk NavLink agar lebih rapi
const navLinkClasses = "px-3 py-2 rounded-md text-sm font-medium transition-colors";
const getNavLinkClass = ({ isActive }) =>
  isActive
    ? `${navLinkClasses} bg-slate-200 text-slate-900`
    : `${navLinkClasses} text-slate-600 hover:bg-slate-100 hover:text-slate-800`;

function Layout({ children }) {
  return (
    <div className="container mx-auto py-8 px-4">
      <header className="bg-white/80 backdrop-blur-lg sticky top-4 z-10 p-3 mb-8 rounded-xl shadow-sm border border-slate-200 flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-800">
          Smart Expense Tracker
        </h1>
        <nav className="flex gap-2">
          <NavLink className={getNavLinkClass} to="/health">Health</NavLink>
          <NavLink className={getNavLinkClass} to="/transactions">Transactions</NavLink>
          <NavLink className={getNavLinkClass} to="/categories">Categories</NavLink>
          <NavLink className={getNavLinkClass} to="/labeling">Labeling</NavLink>
          <NavLink className={getNavLinkClass} to="/reports">Reports</NavLink>
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout><Health /></Layout>} />
        <Route path="/health" element={<Layout><Health /></Layout>} />
        <Route path="/transactions" element={<Layout><Transactions /></Layout>} />
        <Route path="/categories" element={<Layout><Categories /></Layout>} />
        <Route path="/labeling" element={<Layout><Labeling /></Layout>} />
        <Route path="/reports" element={<Layout><Reports /></Layout>} />
      </Routes>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);