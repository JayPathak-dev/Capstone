import React, { useState, useEffect } from 'react';
import {
  Scale,
  RefreshCw,
  FolderGit2,
  ExternalLink,
  ChevronRight,
  TrendingUp,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { fetchBenchmarking, fetchProjects } from '../services/api';
import { BenchmarkingData, Project } from '../types';
import { RiskBadge } from '../components/common/RiskBadge';

interface BenchmarkingProps {
  initialProjectId?: string;
  onSelectProject: (projectId: string) => void;
}

export const Benchmarking: React.FC<BenchmarkingProps> = ({
  initialProjectId,
  onSelectProject,
}) => {
  const [projectList, setProjectList] = useState<Project[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');
  const [benchData, setBenchData] = useState<BenchmarkingData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load initial project list
    const init = async () => {
      try {
        const res = await fetchProjects({ limit: 50 });
        setProjectList(res.items);
        if (initialProjectId) {
          setSelectedId(initialProjectId);
        } else if (res.items.length > 0) {
          setSelectedId(res.items[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    init();
  }, [initialProjectId]);

  useEffect(() => {
    if (!selectedId) return;
    const runBench = async () => {
      setLoading(true);
      try {
        const data = await fetchBenchmarking(selectedId, 5);
        setBenchData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    runBench();
  }, [selectedId]);

  const target = benchData?.target_project;

  const comparisonChartData = target && benchData ? [
    {
      metric: 'Physical Progress (%)',
      Target: target.physical_progress,
      CohortAverage: benchData.cohort_avg_progress,
    },
    {
      metric: 'Financial Burn (%)',
      Target: target.financial_progress,
      CohortAverage: benchData.cohort_avg_budget > 0 ? (target.actual_expenditure / target.approved_budget) * 100 : 0,
    },
    {
      metric: 'Risk Score / 100',
      Target: target.risk_score,
      CohortAverage: benchData.cohort_avg_risk_score,
    },
  ] : [];

  return (
    <div className="space-y-6">
      {/* Title & Selector Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Scale className="h-5 w-5 text-teal-400" />
            <span>Similar-Project Peer Benchmarking</span>
          </h2>
          <p className="text-xs text-slate-400">
            Empirical multi-dimensional comparison against historical schemes in same sector and budget tier
          </p>
        </div>

        {/* Project Selector Dropdown */}
        <div className="flex items-center gap-3">
          <label className="text-xs text-slate-400 font-semibold">Select Scheme:</label>
          <select
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 focus:border-teal-500 focus:outline-none max-w-xs"
          >
            {projectList.map((p) => (
              <option key={p.id} value={p.id}>
                {p.project_code} — {p.project_name.slice(0, 30)}...
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading || !benchData || !target ? (
        <div className="flex h-96 items-center justify-center">
          <div className="flex items-center gap-3 text-teal-400">
            <RefreshCw className="h-6 w-6 animate-spin" />
            <span className="text-sm font-medium">Calculating multi-factor peer distances...</span>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Target Project Header Card */}
          <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-5 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-teal-400 bg-teal-950/60 px-2 py-0.5 rounded border border-teal-800">
                    {target.project_code}
                  </span>
                  <RiskBadge level={target.risk_level} score={target.risk_score} size="sm" />
                </div>
                <h3 className="text-base font-bold text-white mt-1.5">{target.project_name}</h3>
                <div className="text-xs text-slate-400 mt-0.5">
                  {target.sector} | {target.region} Region | Sanction: ₹ {target.approved_budget.toLocaleString()} Cr
                </div>
              </div>

              <div className="text-right">
                <span className="text-[11px] text-slate-400 uppercase font-semibold">Benchmark Cohort</span>
                <div className="text-sm font-bold text-teal-300 font-mono">
                  {benchData.cohort_count} Comparable Projects
                </div>
              </div>
            </div>

            {/* Metric Comparison Strips */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-3 border-t border-slate-800 text-xs">
              <div>
                <span className="text-slate-400">Physical Delivery Gap</span>
                <div className="font-mono font-bold text-white text-base mt-0.5">
                  {target.physical_progress.toFixed(1)}%
                </div>
                <div className="text-[10px] text-slate-400">
                  Cohort Average: {benchData.cohort_avg_progress.toFixed(1)}%
                </div>
              </div>

              <div>
                <span className="text-slate-400">Risk Vulnerability Score</span>
                <div className="font-mono font-bold text-white text-base mt-0.5">
                  {target.risk_score.toFixed(1)}/100
                </div>
                <div className="text-[10px] text-slate-400">
                  Cohort Average: {benchData.cohort_avg_risk_score.toFixed(1)}/100
                </div>
              </div>

              <div>
                <span className="text-slate-400">Estimated Delay Days</span>
                <div className="font-mono font-bold text-amber-400 text-base mt-0.5">
                  +{target.predicted_delay_days} Days
                </div>
                <div className="text-[10px] text-slate-400">
                  Cohort Average: +{benchData.cohort_avg_delay_days.toFixed(0)} Days
                </div>
              </div>

              <div>
                <span className="text-slate-400">Cohort Overrun Frequency</span>
                <div className="font-mono font-bold text-rose-400 text-base mt-0.5">
                  {(benchData.cohort_cost_overrun_rate * 100).toFixed(0)}%
                </div>
                <div className="text-[10px] text-slate-400">Historic peers over budget</div>
              </div>
            </div>
          </div>

          {/* Side-by-Side: Comparative Chart & Similar Projects List */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Comparative Bar Chart */}
            <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-5 shadow-sm">
              <h4 className="text-sm font-bold text-white mb-1">Target Scheme vs. Peer Cohort</h4>
              <p className="text-xs text-slate-400 mb-4">Normalized variance comparison</p>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={comparisonChartData} margin={{ top: 10, right: 10, left: -10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="metric" stroke="#64748b" fontSize={11} />
                    <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0b132b', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                    />
                    <Legend />
                    <Bar dataKey="Target" name="Selected Scheme" fill="#14b8a6" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="CohortAverage" name="Cohort Average" fill="#64748b" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Closest Peer Matches */}
            <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-5 shadow-sm space-y-3">
              <h4 className="text-sm font-bold text-white">Closest Comparable Infrastructure Peers</h4>
              <p className="text-xs text-slate-400">Ranked by multi-dimensional similarity score</p>

              <div className="space-y-2.5 overflow-y-auto max-h-72 pr-1">
                {benchData.similar_projects.map((peer) => (
                  <div
                    key={peer.project_id}
                    onClick={() => onSelectProject(peer.project_id)}
                    className="cursor-pointer rounded-lg border border-slate-800/80 bg-slate-900/60 p-3 hover:border-teal-500/50 transition group space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[11px] font-bold text-teal-400">
                          {peer.project_code}
                        </span>
                        <RiskBadge level={peer.risk_level} score={peer.risk_score} size="sm" />
                      </div>
                      <span className="font-mono text-xs font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-900">
                        {(peer.similarity_score * 100).toFixed(0)}% Match
                      </span>
                    </div>

                    <div className="text-xs font-semibold text-slate-200 line-clamp-1 group-hover:text-white">
                      {peer.project_name}
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800">
                      <span>Physical: {peer.physical_progress.toFixed(0)}%</span>
                      <span>Budget: ₹ {peer.approved_budget.toLocaleString()} Cr</span>
                      <span>Delay: +{peer.predicted_delay_days}d</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
