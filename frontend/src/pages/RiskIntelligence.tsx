import React, { useState, useEffect } from 'react';
import {
  Flame,
  AlertTriangle,
  TrendingDown,
  Layers,
  ArrowUpRight,
  Filter,
  RefreshCw,
} from 'lucide-react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ZAxis,
  Cell,
} from 'recharts';
import { fetchProjects, fetchDashboardSummary } from '../services/api';
import { Project, DashboardSummary } from '../types';
import { RiskBadge } from '../components/common/RiskBadge';

interface RiskIntelligenceProps {
  onSelectProject: (projectId: string) => void;
}

export const RiskIntelligence: React.FC<RiskIntelligenceProps> = ({ onSelectProject }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [projRes, sumRes] = await Promise.all([
        fetchProjects({ limit: 100, sort_by: 'current_risk_score', sort_order: 'desc' }),
        fetchDashboardSummary(),
      ]);
      setProjects(projRes.items);
      setSummary(sumRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading || !summary) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="flex items-center gap-3 text-teal-400">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span className="text-sm font-medium">Computing portfolio risk intelligence...</span>
        </div>
      </div>
    );
  }

  // Scatter plot data: X = Physical Progress, Y = Predicted Delay (Days), Z = Risk Score
  const scatterData = projects.map((p) => ({
    x: p.current_physical_progress,
    y: p.predicted_delay_days,
    z: p.current_risk_score,
    name: p.project_name,
    code: p.project_code,
    level: p.current_risk_level,
    id: p.id,
  }));

  const topDistressed = projects.filter((p) => p.current_risk_score >= 50.0).slice(0, 8);

  return (
    <div className="space-y-6">
      {/* Headline */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Flame className="h-5 w-5 text-rose-400" />
            <span>Risk Intelligence & Vulnerability Matrix</span>
          </h2>
          <p className="text-xs text-slate-400">
            Multi-dimensional risk scoring, schedule slippage correlation, and sector exposure
          </p>
        </div>

        <button
          onClick={loadData}
          className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white transition"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Refresh Analysis</span>
        </button>
      </div>

      {/* High-Risk Project Priority Ranking */}
      <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-rose-400" />
              <span>Priority Distressed Infrastructure Watchlist (Score ≥ 50)</span>
            </h3>
            <p className="text-xs text-slate-400">
              Schemes exhibiting severe velocity collapse or financial divergence requiring immediate PMC intervention
            </p>
          </div>
          <span className="text-xs font-mono text-rose-400 bg-rose-950/60 px-2.5 py-0.5 rounded border border-rose-900 font-semibold">
            {topDistressed.length} Projects in Danger Band
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {topDistressed.map((p) => (
            <div
              key={p.id}
              onClick={() => onSelectProject(p.id)}
              className="cursor-pointer rounded-xl border border-slate-800 bg-slate-900/90 p-4 hover:border-teal-500/60 transition group space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-teal-400">{p.project_code}</span>
                <RiskBadge level={p.current_risk_level} score={p.current_risk_score} size="sm" />
              </div>

              <div>
                <h4 className="text-xs font-bold text-slate-200 line-clamp-1 group-hover:text-white">
                  {p.project_name}
                </h4>
                <div className="text-[11px] text-slate-400 mt-0.5">{p.sector} | {p.region}</div>
              </div>

              <div className="pt-2 border-t border-slate-800 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase">Physical</span>
                  <div className="font-mono font-bold text-white">{p.current_physical_progress.toFixed(0)}%</div>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase">Est. Delay</span>
                  <div className="font-mono font-bold text-amber-400">+{p.predicted_delay_days}d</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Two-Column Section: Scatter Matrix & Sector Heatmap */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scatter Correlation Plot */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-[#0F172A] p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Physical Progress vs. Predicted Delay Days</h3>
              <p className="text-xs text-slate-400">Bubble color represents risk severity</p>
            </div>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  type="number"
                  dataKey="x"
                  name="Physical Progress"
                  unit="%"
                  stroke="#64748b"
                  fontSize={11}
                  domain={[0, 100]}
                />
                <YAxis
                  type="number"
                  dataKey="y"
                  name="Predicted Delay"
                  unit=" days"
                  stroke="#64748b"
                  fontSize={11}
                />
                <ZAxis type="number" dataKey="z" range={[60, 200]} name="Risk Score" />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="rounded-lg border border-slate-700 bg-[#0B132B] p-2.5 text-xs text-slate-200 shadow-xl">
                          <div className="font-bold text-teal-400 font-mono">{d.code}</div>
                          <div className="font-semibold text-white mt-0.5">{d.name}</div>
                          <div className="mt-1">Physical Progress: <span className="font-mono text-white font-bold">{d.x}%</span></div>
                          <div>Predicted Delay: <span className="font-mono text-amber-400 font-bold">{d.y} days</span></div>
                          <div>Risk Score: <span className="font-mono text-rose-400 font-bold">{d.z.toFixed(1)}/100</span></div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter
                  name="Projects"
                  data={scatterData}
                  onClick={(entry) => onSelectProject(entry.id)}
                  cursor="pointer"
                >
                  {scatterData.map((entry, index) => {
                    let color = '#10B981';
                    if (entry.level === 'MODERATE') color = '#F59E0B';
                    else if (entry.level === 'HIGH') color = '#F97316';
                    else if (entry.level === 'CRITICAL') color = '#EF4444';
                    return <Cell key={`cell-${index}`} fill={color} />;
                  })}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sector Vulnerability Matrix */}
        <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-5 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white mb-1">Sector Vulnerability Breakdown</h3>
            <p className="text-xs text-slate-400 mb-4">Average composite risk score by sector</p>

            <div className="space-y-3">
              {summary.sector_breakdown.map((sec) => (
                <div key={sec.sector} className="rounded-lg border border-slate-800/80 bg-slate-900/60 p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-white">{sec.sector}</span>
                    <span className={`text-xs font-mono font-bold ${
                      sec.avg_risk_score >= 60 ? 'text-rose-400' : sec.avg_risk_score >= 40 ? 'text-amber-400' : 'text-emerald-400'
                    }`}>
                      {sec.avg_risk_score.toFixed(1)}/100
                    </span>
                  </div>

                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-2">
                    <div
                      className={`h-full rounded-full ${
                        sec.avg_risk_score >= 60 ? 'bg-rose-500' : sec.avg_risk_score >= 40 ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${sec.avg_risk_score}%` }}
                    />
                  </div>

                  <div className="flex justify-between items-center text-[10px] text-slate-400 mt-1.5">
                    <span>{sec.count} schemes | ₹ {sec.approved_budget.toLocaleString()} Cr</span>
                    <span className="text-amber-300">{sec.high_risk_count} in high risk</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
