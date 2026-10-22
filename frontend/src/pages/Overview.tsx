import React, { useState, useEffect } from 'react';
import {
  FolderGit2,
  AlertTriangle,
  TrendingUp,
  Clock,
  IndianRupee,
  Layers,
  CheckCircle2,
  ArrowUpRight,
  RefreshCw,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { fetchDashboardSummary } from '../services/api';
import { DashboardSummary } from '../types';
import { StatCard } from '../components/common/StatCard';
import { RiskBadge } from '../components/common/RiskBadge';

const RISK_COLORS = {
  low: '#10B981',
  moderate: '#F59E0B',
  high: '#F97316',
  critical: '#EF4444',
};

interface OverviewProps {
  onSelectProject?: (projectId: string) => void;
  onNavigateToAlerts?: () => void;
  onNavigateToProjects?: () => void;
}

export const Overview: React.FC<OverviewProps> = ({
  onSelectProject,
  onNavigateToAlerts,
  onNavigateToProjects,
}) => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSector, setSelectedSector] = useState<string>('ALL');
  const [selectedRegion, setSelectedRegion] = useState<string>('ALL');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const summary = await fetchDashboardSummary(selectedSector, selectedRegion);
      setData(summary);
    } catch (err: any) {
      setError(err.message || 'Failed to load executive summary');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedSector, selectedRegion]);

  if (loading && !data) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="flex items-center gap-3 text-teal-400">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span className="text-sm font-medium">Loading PAIMANA Intelligence Engine...</span>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-xl border border-rose-900/50 bg-rose-950/20 p-8 text-center text-rose-300">
        <AlertTriangle className="mx-auto h-10 w-10 text-rose-400 mb-3" />
        <h3 className="text-base font-bold">Failed to Connect to Backend Engine</h3>
        <p className="mt-1 text-xs text-rose-300/80">{error || 'Make sure the FastAPI server is running on port 8000.'}</p>
        <button
          onClick={loadData}
          className="mt-4 rounded-lg bg-rose-900/40 px-4 py-2 text-xs font-semibold text-rose-200 border border-rose-700 hover:bg-rose-900/60 transition"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const pieData = [
    { name: 'Low Risk (0-29)', value: data.risk_distribution.low, color: RISK_COLORS.low },
    { name: 'Moderate (30-49)', value: data.risk_distribution.moderate, color: RISK_COLORS.moderate },
    { name: 'High (50-74)', value: data.risk_distribution.high, color: RISK_COLORS.high },
    { name: 'Critical (75-100)', value: data.risk_distribution.critical, color: RISK_COLORS.critical },
  ];

  const sectorChartData = data.sector_breakdown.map((s) => ({
    name: s.sector.length > 15 ? s.sector.slice(0, 14) + '...' : s.sector,
    approved: Math.round(s.approved_budget),
    spent: Math.round(s.actual_expenditure),
  }));

  return (
    <div className="space-y-6">
      {/* Top Filter and Headline Bar */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            Portfolio Command & Early Warning Center
          </h2>
          <p className="text-xs text-slate-400">
            Real-time monitoring across {data.total_projects} active infrastructure schemes
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
          >
            <option value="ALL">All Sectors</option>
            <option value="Roads & Highways">Roads & Highways</option>
            <option value="Railways">Railways</option>
            <option value="Urban Mass Transit">Urban Mass Transit</option>
            <option value="Power & Renewable Energy">Power & Renewable Energy</option>
            <option value="Water & Sanitation">Water & Sanitation</option>
            <option value="Ports & Shipping">Ports & Shipping</option>
          </select>

          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
          >
            <option value="ALL">All Regions</option>
            <option value="Northern">Northern</option>
            <option value="Western">Western</option>
            <option value="Southern">Southern</option>
            <option value="Eastern">Eastern</option>
            <option value="Central">Central</option>
            <option value="North-Eastern">North-Eastern</option>
          </select>

          <button
            onClick={loadData}
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white hover:border-slate-600 transition"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Monitored Projects"
          value={data.total_projects}
          subValue={`Avg ${data.average_physical_progress.toFixed(1)}% physical`}
          icon={FolderGit2}
          variant="teal"
        />
        <StatCard
          title="Elevated Risk Watchlist"
          value={data.high_critical_risk_projects}
          subValue={`${((data.high_critical_risk_projects / Math.max(1, data.total_projects)) * 100).toFixed(0)}% of portfolio`}
          icon={AlertTriangle}
          variant={data.high_critical_risk_projects > 5 ? 'danger' : 'warning'}
          change={`${data.high_critical_risk_projects} flagged`}
          isPositive={false}
        />
        <StatCard
          title="Predicted Cost Overruns"
          value={data.predicted_cost_overrun_projects}
          subValue={`Net Variance: ₹ ${(data.net_cost_variance / 1000).toFixed(1)}k Cr`}
          icon={IndianRupee}
          variant="warning"
        />
        <StatCard
          title="Forecast Schedule Slippage"
          value={data.predicted_delay_projects}
          subValue="Projects delay >30d"
          icon={Clock}
          variant="danger"
        />
      </div>

      {/* Secondary Financial KPI Strip */}
      <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <div className="text-[11px] text-slate-400 font-medium uppercase">Approved Capital Outlay</div>
          <div className="text-lg font-bold font-mono text-white mt-1">
            ₹ {(data.total_approved_budget).toLocaleString('en-IN', { maximumFractionDigits: 1 })} Cr
          </div>
        </div>
        <div>
          <div className="text-[11px] text-slate-400 font-medium uppercase">Cumulative Expenditure</div>
          <div className="text-lg font-bold font-mono text-teal-400 mt-1">
            ₹ {(data.total_actual_expenditure).toLocaleString('en-IN', { maximumFractionDigits: 1 })} Cr
          </div>
          <div className="text-[10px] text-slate-400">
            {((data.total_actual_expenditure / Math.max(1, data.total_approved_budget)) * 100).toFixed(1)}% burn rate
          </div>
        </div>
        <div>
          <div className="text-[11px] text-slate-400 font-medium uppercase">Forecast Final Cost</div>
          <div className="text-lg font-bold font-mono text-amber-400 mt-1">
            ₹ {(data.total_forecast_final_cost).toLocaleString('en-IN', { maximumFractionDigits: 1 })} Cr
          </div>
          <div className="text-[10px] text-amber-400 font-medium">
            +₹ {(Math.max(0, data.net_cost_variance)).toLocaleString('en-IN', { maximumFractionDigits: 1 })} Cr overrun
          </div>
        </div>
        <div>
          <div className="text-[11px] text-slate-400 font-medium uppercase">Physical vs Financial Gap</div>
          <div className={`text-lg font-bold font-mono mt-1 ${
            data.average_financial_progress > data.average_physical_progress ? 'text-rose-400' : 'text-emerald-400'
          }`}>
            {(data.average_financial_progress - data.average_physical_progress).toFixed(1)}% pts
          </div>
          <div className="text-[10px] text-slate-400">
            {data.average_financial_progress > data.average_physical_progress ? 'Financial burn outpaces works' : 'Expenditure aligned'}
          </div>
        </div>
      </div>

      {/* Charts Section: 2 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sector Sanction vs Spent */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-[#0F172A] p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Sector Outlay vs. Cumulative Expenditure</h3>
              <p className="text-xs text-slate-400">Capital comparison in ₹ Crores</p>
            </div>
            <button
              onClick={onNavigateToProjects}
              className="flex items-center gap-1 text-xs text-teal-400 hover:text-teal-300 font-medium"
            >
              <span>Explore Projects</span>
              <ArrowUpRight className="h-3.5 w-3.5" />
            </button>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sectorChartData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} angle={-15} textAnchor="end" />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0b132b', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="approved" name="Sanctioned Outlay (₹ Cr)" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                <Bar dataKey="spent" name="Actual Expenditure (₹ Cr)" fill="#14b8a6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Portfolio Risk Distribution Donut */}
        <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-5 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Portfolio Risk Classification</h3>
            <p className="text-xs text-slate-400">Calibrated multi-factor risk index</p>
          </div>
          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0b132b', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-800">
            {pieData.map((p) => (
              <div key={p.name} className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: p.color }} />
                <span className="text-slate-300">{p.name.split(' ')[0]}:</span>
                <span className="font-bold text-white font-mono">{p.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Trends & Priority Alerts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Planned vs Actual Monthly Trajectory */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-[#0F172A] p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Monthly Execution Trajectory</h3>
              <p className="text-xs text-slate-400">Average planned vs actual physical delivery %</p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="h-2 w-2 rounded-full bg-teal-400" /> Planned Progress %
              </span>
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="h-2 w-2 rounded-full bg-amber-400" /> Actual Progress %
              </span>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.monthly_trends} margin={{ top: 10, right: 10, left: -10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0b132b', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Line type="monotone" dataKey="planned_progress" name="Planned %" stroke="#14b8a6" strokeWidth={2.5} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="actual_progress" name="Actual %" stroke="#f59e0b" strokeWidth={2.5} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Priority Early Warning Alerts */}
        <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-5 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-semibold text-white">Active Early Warnings</h3>
              <p className="text-xs text-slate-400">Triggered by ML and divergence rules</p>
            </div>
            <button
              onClick={onNavigateToAlerts}
              className="text-xs text-teal-400 hover:text-teal-300 font-medium"
            >
              View All ({data.recent_alerts.length})
            </button>
          </div>

          <div className="space-y-2.5 overflow-y-auto max-h-72 pr-1">
            {data.recent_alerts.slice(0, 4).map((alert) => (
              <div
                key={alert.id}
                className="rounded-lg border border-slate-800/80 bg-slate-900/60 p-3 hover:border-slate-700 transition"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-[10px] text-teal-400 font-semibold">{alert.project_code}</span>
                  <RiskBadge level={alert.severity} size="sm" />
                </div>
                <div className="text-xs font-semibold text-slate-200 mt-1 line-clamp-1">{alert.title}</div>
                <div className="text-[11px] text-slate-400 mt-0.5 line-clamp-2">{alert.description}</div>
              </div>
            ))}
          </div>

          <button
            onClick={onNavigateToAlerts}
            className="w-full mt-3 rounded-lg border border-slate-700 bg-slate-800/80 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-800 hover:text-white transition"
          >
            Review & Acknowledge Warnings
          </button>
        </div>
      </div>
    </div>
  );
};
