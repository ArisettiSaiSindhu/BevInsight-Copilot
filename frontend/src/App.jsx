import React, { useState, useEffect } from 'react';
import { LayoutDashboard, MessageSquare, Sliders, Bell, FileText, Clock, Database, X } from 'lucide-react';
import DashboardKPIs from './components/DashboardKPIs.jsx';
import BusinessHealth from './components/BusinessHealth.jsx';
import ChatInterface from './components/ChatInterface.jsx';
import DecisionSimulator from './components/DecisionSimulator.jsx';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [chatHistory, setChatHistory] = useState([
    {
      id: 'welcome',
      sender: 'system',
      text: 'Welcome back! Ask me anything, or use the **Decision Simulator** to model business parameters.',
      confidence: 100,
      reasoning: 'Welcome hook initialized.'
    }
  ]);
  const [question, setQuestion] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [inspectQuery, setInspectQuery] = useState(null);
  const [execSummary, setExecSummary] = useState(null);

  useEffect(() => {
    fetchDashboard();
    fetchAlerts();
    fetchExecutiveSummary();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await fetch('/api/dashboard');
      const data = await res.json();
      setDashboardData(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchAlerts = async () => {
    try {
      const res = await fetch('/api/alerts');
      const data = await res.json();
      setAlerts(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchExecutiveSummary = async () => {
    try {
      const res = await fetch('/api/executive-summary');
      const data = await res.json();
      setExecSummary(data);
    } catch (err) {
      console.error(err);
    }
  };

  const submitQuestion = async (e) => {
    e.preventDefault();
    const qText = question.trim();
    if (!qText) return;

    setQuestion('');
    setChatHistory((prev) => [...prev, { id: Date.now().toString(), sender: 'user', text: qText }]);
    setChatLoading(true);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: qText })
      });
      const data = await res.json();
      if (data.success) {
        setChatHistory((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            sender: 'system',
            text: data.insights,
            sql: data.sql,
            results: data.results,
            confidence: data.confidence,
            reasoning: data.reasoning
          }
        ]);
        setInspectQuery({ sql: data.sql, results: data.results });
      } else {
        setChatHistory((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            sender: 'system',
            text: `<div class="text-red-500 font-bold">Query Failed</div><p>${data.error}</p>`,
            sql: data.sql || '',
            results: [],
            confidence: 0,
            reasoning: data.reasoning
          }
        ]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col text-slate-100 font-sans bg-slate-950">
      {/* Header */}
      <header className="flex justify-between items-center py-3 px-6 bg-slate-900 border-b border-white/5 sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <LayoutDashboard className="text-teal-400 w-6 h-6" />
          <h1 className="text-lg font-extrabold tracking-tight">
            BevInsight <span className="text-teal-400">Copilot</span>
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={() => window.print()} className="bg-gradient-to-r from-blue-500 to-teal-400 text-slate-950 text-xs font-bold py-1.5 px-4 rounded-lg flex items-center gap-2">
            <FileText className="w-3.5 h-3.5" />
            Generate Board Report
          </button>
        </div>
      </header>

      {/* Main Container */}
      <div className="flex-grow grid grid-cols-12 overflow-hidden h-[calc(100vh-53px)]">
        {/* Navigation Sidebar */}
        <nav className="col-span-1 bg-slate-950 py-6 flex flex-col items-center justify-between border-r border-white/5">
          <div className="flex flex-col gap-4 w-full px-2">
            <button onClick={() => setActiveTab('dashboard')} className={`py-3 px-2 rounded-xl flex flex-col items-center gap-1.5 transition ${activeTab === 'dashboard' ? 'bg-teal-400/15 text-teal-400' : 'text-slate-400'}`}>
              <LayoutDashboard className="w-5 h-5" />
              <span className="text-[9px] font-bold">Dashboard</span>
            </button>
            <button onClick={() => setActiveTab('chat')} className={`py-3 px-2 rounded-xl flex flex-col items-center gap-1.5 transition ${activeTab === 'chat' ? 'bg-teal-400/15 text-teal-400' : 'text-slate-400'}`}>
              <MessageSquare className="w-5 h-5" />
              <span className="text-[9px] font-bold">AI Analyst</span>
            </button>
            <button onClick={() => setActiveTab('simulator')} className={`py-3 px-2 rounded-xl flex flex-col items-center gap-1.5 transition ${activeTab === 'simulator' ? 'bg-teal-400/15 text-teal-400' : 'text-slate-400'}`}>
              <Sliders className="w-5 h-5" />
              <span className="text-[9px] font-bold">Simulator</span>
            </button>
          </div>
        </nav>

        {/* Content Window */}
        <main className="col-span-11 bg-slate-900/40 overflow-y-auto">
          {activeTab === 'dashboard' && (
            <div className="p-6 space-y-6">
              {dashboardData && <DashboardKPIs kpis={dashboardData.kpis} />}
              {dashboardData && <BusinessHealth health={dashboardData.health} />}
              {execSummary && (
                <div className="bg-slate-950 p-6 rounded-xl border border-white/5 space-y-4">
                  <h3 className="text-sm font-bold text-slate-200 uppercase">AI Board Executive Summary</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{execSummary.summary}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'chat' && (
            <ChatInterface 
              chatHistory={chatHistory} 
              question={question} 
              setQuestion={setQuestion} 
              submitQuestion={submitQuestion} 
              chatLoading={chatLoading} 
              setInspectQuery={setInspectQuery} 
            />
          )}

          {activeTab === 'simulator' && <DecisionSimulator />}
        </main>
      </div>

      {/* SQL Inspector Bottom Sheet */}
      {inspectQuery && (
        <div className="fixed bottom-0 right-0 w-[500px] h-[400px] bg-slate-950 border-t border-l border-white/10 z-[100] flex flex-col justify-between shadow-2xl">
          <div className="flex justify-between items-center py-2 px-4 bg-slate-900 border-b border-white/5">
            <span className="text-xs font-bold text-slate-300">Raw Database Inspector</span>
            <button onClick={() => setInspectQuery(null)} className="text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="flex-grow overflow-y-auto p-4 space-y-4 font-mono text-xs">
            <pre className="bg-black/60 p-3 border border-white/5 rounded-lg overflow-x-auto text-[10px] text-slate-200">{inspectQuery.sql}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
