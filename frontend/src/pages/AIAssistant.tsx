import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  Send,
  Sparkles,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  CheckCircle,
  HelpCircle,
} from 'lucide-react';
import { sendAssistantMessage } from '../services/api';
import { ChatResponse, ChatReferencedProject } from '../types';
import { RiskBadge } from '../components/common/RiskBadge';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  toolsUsed?: string[];
  referencedProjects?: ChatReferencedProject[];
  followups?: string[];
  timestamp: string;
}

interface AIAssistantProps {
  onSelectProject: (projectId: string) => void;
}

export const AIAssistant: React.FC<AIAssistantProps> = ({ onSelectProject }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text:
        'Welcome to **PAIMANA Infrastructure Intelligence Assistant**. I use governed, read-only tools to query verified project monitoring data, milestone schedules, and machine learning risk evaluations.\n\nHow can I assist your infrastructure monitoring review today?',
      toolsUsed: ['system_initialization'],
      followups: [
        'Which 5 projects currently have the highest risk?',
        'Which projects may exceed their approved budgets?',
        'What critical milestones are overdue across railway projects?',
        'Show all active CRITICAL early warnings.',
      ],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: textToSend.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!messageText) setInput('');
    setLoading(true);

    try {
      const res: ChatResponse = await sendAssistantMessage(textToSend.trim(), conversationId);
      setConversationId(res.conversation_id);

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: res.response,
        toolsUsed: res.tools_used,
        referencedProjects: res.referenced_projects,
        followups: res.suggested_followups,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: 'Sorry, I encountered an issue communicating with the backend tool orchestrator: ' + err.message,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] rounded-xl border border-slate-800 bg-[#0F172A] shadow-sm overflow-hidden">
      {/* Assistant Header */}
      <div className="flex items-center justify-between border-b border-slate-800 bg-[#0B132B] px-5 py-3.5">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-600/20 text-teal-400 border border-teal-500/30">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              PAIMANA Grounded AI Assistant
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800">
                Governed Tool Execution
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              Zero hallucinations • Verified against live infrastructure databases
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <ShieldCheck className="h-4 w-4 text-teal-400" />
          <span className="hidden sm:inline">Read-Only Decision Support</span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          return (
            <div
              key={m.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed ${
                  isUser
                    ? 'bg-teal-600 text-white rounded-br-none'
                    : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none shadow-md'
                }`}
              >
                {/* Tools invoked badge */}
                {!isUser && m.toolsUsed && m.toolsUsed.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5 mb-2.5 pb-2 border-b border-slate-800">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase">
                      Tools Invoked:
                    </span>
                    {m.toolsUsed.map((tool) => (
                      <span
                        key={tool}
                        className="rounded bg-slate-800 text-teal-300 font-mono text-[10px] px-2 py-0.5 border border-slate-700"
                      >
                        {tool}()
                      </span>
                    ))}
                  </div>
                )}

                {/* Formatted Text */}
                <div className="whitespace-pre-wrap">{m.text}</div>

                {/* Referenced Project Dossier Cards */}
                {!isUser && m.referencedProjects && m.referencedProjects.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-800 space-y-2">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase block">
                      Referenced Project Records:
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {m.referencedProjects.map((p) => (
                        <div
                          key={p.project_id}
                          onClick={() => onSelectProject(p.project_id)}
                          className="cursor-pointer rounded-lg border border-slate-800 bg-slate-950/70 p-2.5 hover:border-teal-500/60 transition group"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-[10px] font-bold text-teal-400">
                              {p.project_code}
                            </span>
                            <RiskBadge level={p.risk_level} score={p.risk_score} size="sm" />
                          </div>
                          <div className="text-[11px] font-medium text-slate-200 line-clamp-1 mt-1 group-hover:text-white">
                            {p.project_name}
                          </div>
                          <div className="text-[10px] text-slate-500 mt-0.5 flex items-center justify-between">
                            <span>{p.sector}</span>
                            <span className="text-teal-400 flex items-center gap-0.5">
                              Open Dossier <ExternalLink className="h-2.5 w-2.5" />
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-2 text-[10px] text-right opacity-60 font-mono">
                  {m.timestamp}
                </div>
              </div>

              {/* Follow-up Prompt Pills */}
              {!isUser && m.followups && m.followups.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2.5 max-w-2xl">
                  {m.followups.map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSend(q)}
                      className="rounded-full border border-slate-700 bg-slate-900/90 px-3 py-1 text-[11px] text-slate-300 hover:border-teal-500 hover:text-white transition flex items-center gap-1.5"
                    >
                      <Sparkles className="h-3 w-3 text-teal-400" />
                      <span>{q}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-teal-400 bg-slate-900/60 p-3 rounded-xl border border-slate-800 w-fit">
            <RefreshCw className="h-3.5 w-3.5 animate-spin" />
            <span>Consulting PAIMANA monitoring records & risk engine...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form Bar */}
      <div className="border-t border-slate-800 bg-[#0B132B] p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask a question about project delays, budget breaches, or overdue milestones..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:border-teal-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-600 text-white hover:bg-teal-500 disabled:opacity-50 transition"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
        <div className="mt-2 text-[10px] text-slate-500 text-center">
          PAIMANA Assistant queries live SQLite/PostgreSQL tables using parameterized tools. Strictly no unrestricted SQL.
        </div>
      </div>
    </div>
  );
};
