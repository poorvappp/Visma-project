/**
 * Simple Payroll Frontend (React + TypeScript + Vite)
 * ---------------------------------------------------
 * Run locally:
 *   npm create vite@latest payroll-frontend -- --template react-ts
 *   cd payroll-frontend
 *   npm install
 *   Replace src/App.tsx with this file
 *   npm run dev
 */

import React, { useState } from "react";

type FormState = {
  employeeId: string;
  employeeName: string;
  payPeriodStart: string;
  payPeriodEnd: string;
  hoursWorked: number;
  hourlyRate: number;
  taxRatePercent: number;
  deductions: number;
  notes: string;
};

const initial: FormState = {
  employeeId: "",
  employeeName: "",
  payPeriodStart: "",
  payPeriodEnd: "",
  hoursWorked: 0,
  hourlyRate: 0,
  taxRatePercent: 30,
  deductions: 0,
  notes: ""
};

const API = "http://127.0.0.1:8000";

export default function App() {
  const [form, setForm] = useState<FormState>(initial);
  const [loading, setLoading] = useState(false);

  const update = (k: keyof FormState, v: any) =>
    setForm(prev => ({ ...prev, [k]: v }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/payroll`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Payroll_${form.employeeId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "2rem auto", fontFamily: "Arial" }}>
      <h1>Payroll Generator</h1>
      <form onSubmit={submit}>
        <label>ID <input value={form.employeeId} onChange={e => update("employeeId", e.target.value)} required /></label>
        <label>Name <input value={form.employeeName} onChange={e => update("employeeName", e.target.value)} required /></label>
        <label>Start <input type="date" value={form.payPeriodStart} onChange={e => update("payPeriodStart", e.target.value)} required /></label>
        <label>End <input type="date" value={form.payPeriodEnd} onChange={e => update("payPeriodEnd", e.target.value)} required /></label>
        <label>Hours <input type="number" value={form.hoursWorked} onChange={e => update("hoursWorked", parseFloat(e.target.value))} /></label>
        <label>Rate <input type="number" value={form.hourlyRate} onChange={e => update("hourlyRate", parseFloat(e.target.value))} /></label>
        <label>Tax % <input type="number" value={form.taxRatePercent} onChange={e => update("taxRatePercent", parseFloat(e.target.value))} /></label>
        <label>Deductions <input type="number" value={form.deductions} onChange={e => update("deductions", parseFloat(e.target.value))} /></label>
        <label>Notes <textarea value={form.notes} onChange={e => update("notes", e.target.value)} /></label>
        <button type="submit" disabled={loading}>{loading ? "Generating..." : "Generate PDF"}</button>
      </form>
    </div>
  );
}
