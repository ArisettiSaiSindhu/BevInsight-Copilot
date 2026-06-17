import React, { useRef, useEffect } from 'react';
import { Send, Sparkles, User, HelpCircle } from 'lucide-react';

export default function ChatInterface({ 
  chatHistory, 
  question, 
  setQuestion, 
  submitQuestion, 
  chatLoading, 
  setInspectQuery 
}) {
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory, chatLoading]);

  return (
    <div className="flex flex-col h-full bg-slate-900/40">
      {/* Scrollable Timeline */}
      <div className="flex-grow overflow-y-auto p-6 space-y-4">
        {chatHistory.map((chat) => (
          <div key={chat.id} className={`flex flex-col ${chat.sender === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`max-w-[80%] rounded-2xl p-4 border ${chat.sender === 'user' ? 'bg-blue-500/10 border-blue-500/20 text-slate-100 rounded-tr-sm' : 'bg-slate-950/60 border-white/5 rounded-tl-sm'}`}>
              <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                {chat.sender === 'user' ? <User className="w-3.5 h-3.5" /> : <Sparkles className="w-3.5 h-3.5 text-teal-400" />}
                <span>{chat.sender === 'user' ? 'Corporate Analyst' : 'BevInsight AI Agent'}</span>
                {chat.confidence !== undefined && (
                  <span className={`ml-auto px-2 py-0.5 rounded text-[9px] ${chat.confidence > 80 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}`}>Confidence: {chat.confidence}%</span>
                )}
              </div>
              
              {chat.sender === 'system' ? (
                <div className="text-sm text-slate-300 space-y-3 leading-relaxed" dangerouslySetInnerHTML={{ __html: chat.text }}></div>
              ) : (
                <p className="text-sm font-medium">{chat.text}</p>
              )}
              
              {/* Reasoning block */}
              {chat.reasoning && (
                <div className="mt-4 pt-3 border-t border-white/5">
                  <span className="text-[9px] uppercase tracking-wider font-bold text-slate-400 block mb-1">Explainability Logic</span>
                  <pre className="text-[10px] font-mono text-slate-400 whitespace-pre-wrap">{chat.reasoning}</pre>
                </div>
              )}
              
              {chat.sql && (
                <div className="mt-3 flex gap-2">
                  <button onClick={() => setInspectQuery({ sql: chat.sql, results: chat.results })} className="text-[10px] font-mono font-bold bg-slate-900 border border-white/5 text-teal-400 py-1.5 px-3 rounded hover:bg-slate-800 transition">
                    Inspect Raw Query & Table Data
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
        {chatLoading && (
          <div className="flex flex-col items-start">
            <div className="bg-slate-950/60 border border-white/5 rounded-2xl rounded-tl-sm p-4 w-[320px] space-y-3">
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block animate-pulse">Agent processing query...</span>
              <div className="space-y-2">
                <div className="shimmer bg-slate-800/40 h-2.5 w-full rounded"></div>
                <div className="shimmer bg-slate-800/40 h-2.5 w-3/4 rounded"></div>
                <div className="shimmer bg-slate-800/40 h-2.5 w-1/2 rounded"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Form */}
      <div className="p-4 bg-slate-950/40 border-t border-white/5 sticky bottom-0">
        <form onSubmit={submitQuestion} className="flex gap-3 max-w-4xl mx-auto">
          <input 
            type="text" 
            value={question} 
            onChange={(e) => setQuestion(e.target.value)} 
            placeholder="Ask a data question (e.g. 'Show products affected by stockouts')..." 
            className="flex-grow bg-slate-900 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-400 transition" 
          />
          <button type="submit" className="bg-gradient-to-r from-blue-500 to-teal-400 text-slate-950 font-bold px-5 rounded-xl hover:scale-105 transition flex items-center gap-1.5 shadow-lg shadow-teal-400/10">
            <Send className="w-4 h-4" />
            <span>Analyze</span>
          </button>
        </form>
      </div>
    </div>
  );
}
