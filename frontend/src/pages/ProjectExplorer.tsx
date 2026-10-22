import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Download,
  ArrowUpDown,
  ChevronRight,
  ExternalLink,
  RefreshCw,
  FolderGit2,
} from 'lucide-react';
import { fetchProjects } from '../services/api';
import { Project } from '../types';
import { RiskBadge } from '../components/common/RiskBadge';

interface ProjectExplorerProps {
  onSelectProject: (projectId: string) => void;
}

export const ProjectExplorer: React.FC<ProjectExplorerProps> = ({ onSelectProject }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Pagination State
  const [search, setSearch] = useState('');
  const [sector, setSector] = useState('ALL');
  const [region, setRegion] = useState('ALL');
  const [riskLevel, setRiskLevel] = useState('ALL');
  const [status, setStatus] = useState('ALL');
  const [sortBy, setSortBy] = useState('current_risk_score');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');
  const [page, setPage] = useState(1);
  const pageSize = 15;

  const loadProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchProjects({
        skip: (page - 1) * pageSize,
        limit: pageSize,
        search: search.trim() || undefined,
        sector,
        region,
        risk_level: riskLevel,
        status,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setProjects(res.items);
      setTotal(res.total);
    } catch (err: any) {
      setError(err.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, [search, sector, region, riskLevel, status, sortBy, sortOrder, page]);

  const toggleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
    setPage(1);
  };

  const exportToCsv = () => {
    if (!projects.length) return;
    const headers = [
      'Project Code',
      'Project Name',
      'Sector',
      'Region',
      'Agency',
      'Approved Budget (Cr)',
      'Actual Expenditure (Cr)',
      'Physical Progress (%)',
      'Risk Score',
      'Risk Level',
      'Predicted Delay Days',
      'Status',
    ];

    const rows = projects.map((p) => [
      p.project_code,
      `"${p.project_name.replace(/"/g, '""')}"`,
      p.sector,
      p.region,
      p.implementing_agency,
      p.approved_budget,
      p.actual_expenditure,
      p.current_physical_progress,
      p.current_risk_score,
      p.current_risk_level,
      p.predicted_delay_days,
      p.project_status,
    ]);

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `paimana_projects_export_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-5">
      {/* Page Title & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            Project Explorer
          </h2>
          <p className="text-xs text-slate-400">
            Monitor, filter, and drill down into sanctioned infrastructure schemes ({total} records)
          </p>
        </div>

        <button
          onClick={exportToCsv}
          className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-850 px-3.5 py-1.5 text-xs font-semibold text-slate-200 hover:border-teal-500 hover:text-white transition"
        >
          <Download className="h-4 w-4 text-teal-400" />
          <span>Export Filtered CSV</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-4 space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Search Input */}
          <div className="relative lg:col-span-2">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by code, title, agency..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 py-1.5 pl-9 pr-4 text-xs text-slate-200 placeholder-slate-500 focus:border-teal-500 focus:outline-none"
            />
          </div>

          {/* Sector Filter */}
          <select
            value={sector}
            onChange={(e) => {
              setSector(e.target.value);
              setPage(1);
            }}
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

          {/* Risk Level Filter */}
          <select
            value={riskLevel}
            onChange={(e) => {
              setRiskLevel(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="CRITICAL">Critical Risk (75-100)</option>
            <option value="HIGH">High Risk (50-74)</option>
            <option value="MODERATE">Moderate Risk (30-49)</option>
            <option value="LOW">Low Risk (0-29)</option>
          </select>

          {/* Status Filter */}
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="DELAYED">Delayed</option>
            <option value="COMPLETED">Completed</option>
            <option value="STALLED">Stalled</option>
          </select>
        </div>
      </div>

      {/* Projects Table */}
      <div className="rounded-xl border border-slate-800 bg-[#0F172A] shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 bg-[#0B132B] text-slate-400">
              <tr>
                <th className="py-3 px-4 font-semibold">Project Identifier</th>
                <th className="py-3 px-4 font-semibold">Sector & Region</th>
                <th
                  className="py-3 px-4 font-semibold cursor-pointer hover:text-white"
                  onClick={() => toggleSort('approved_budget')}
                >
                  <div className="flex items-center gap-1">
                    <span>Budget & Spend</span>
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th
                  className="py-3 px-4 font-semibold cursor-pointer hover:text-white"
                  onClick={() => toggleSort('current_physical_progress')}
                >
                  <div className="flex items-center gap-1">
                    <span>Physical Progress</span>
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th
                  className="py-3 px-4 font-semibold cursor-pointer hover:text-white"
                  onClick={() => toggleSort('predicted_delay_days')}
                >
                  <div className="flex items-center gap-1">
                    <span>Predicted Delay</span>
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th
                  className="py-3 px-4 font-semibold cursor-pointer hover:text-white"
                  onClick={() => toggleSort('current_risk_score')}
                >
                  <div className="flex items-center gap-1">
                    <span>Risk Level</span>
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th className="py-3 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading && projects.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <RefreshCw className="mx-auto h-6 w-6 animate-spin text-teal-400 mb-2" />
                    <span>Loading projects...</span>
                  </td>
                </tr>
              ) : projects.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <FolderGit2 className="mx-auto h-8 w-8 text-slate-600 mb-2" />
                    <span className="font-semibold text-slate-300">No projects match your filter criteria</span>
                    <p className="text-xs text-slate-500 mt-1">Try resetting the search keyword or sector filters.</p>
                  </td>
                </tr>
              ) : (
                projects.map((p) => {
                  return (
                    <tr
                      key={p.id}
                      onClick={() => onSelectProject(p.id)}
                      className="cursor-pointer hover:bg-slate-800/40 transition group"
                    >
                      {/* Code & Name */}
                      <td className="py-3.5 px-4">
                        <div className="font-mono text-[11px] font-semibold text-teal-400">
                          {p.project_code}
                        </div>
                        <div className="font-medium text-slate-200 line-clamp-1 max-w-xs group-hover:text-white">
                          {p.project_name}
                        </div>
                        <div className="text-[10px] text-slate-500">{p.implementing_agency}</div>
                      </td>

                      {/* Sector & Region */}
                      <td className="py-3.5 px-4 text-slate-300">
                        <div>{p.sector}</div>
                        <div className="text-[10px] text-slate-500">{p.region} Region</div>
                      </td>

                      {/* Budget vs Expenditure */}
                      <td className="py-3.5 px-4">
                        <div className="font-mono text-white">₹ {p.actual_expenditure.toLocaleString()} Cr</div>
                        <div className="text-[10px] text-slate-400">
                          of ₹ {p.approved_budget.toLocaleString()} Cr ({p.current_financial_progress.toFixed(0)}%)
                        </div>
                      </td>

                      {/* Physical Progress Bar */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-semibold text-white w-9">
                            {p.current_physical_progress.toFixed(0)}%
                          </span>
                          <div className="w-20 bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div
                              className="bg-teal-500 h-full rounded-full transition-all"
                              style={{ width: `${Math.min(100, p.current_physical_progress)}%` }}
                            />
                          </div>
                        </div>
                        {p.current_financial_progress > p.current_physical_progress + 15 && (
                          <div className="text-[10px] text-rose-400 mt-0.5">
                            Burn {(p.current_financial_progress - p.current_physical_progress).toFixed(0)}% ahead
                          </div>
                        )}
                      </td>

                      {/* Predicted Delay */}
                      <td className="py-3.5 px-4">
                        {p.predicted_delay_days > 0 ? (
                          <span className="font-mono font-semibold text-amber-400">
                            +{p.predicted_delay_days} days
                          </span>
                        ) : (
                          <span className="text-emerald-400 font-medium">On Schedule</span>
                        )}
                        <div className="text-[10px] text-slate-500">Target: {p.expected_completion_date}</div>
                      </td>

                      {/* Risk Score */}
                      <td className="py-3.5 px-4">
                        <RiskBadge level={p.current_risk_level} score={p.current_risk_score} size="sm" />
                      </td>

                      {/* Action */}
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectProject(p.id);
                          }}
                          className="inline-flex items-center gap-1 rounded border border-slate-700 bg-slate-800 px-2.5 py-1 text-[11px] font-medium text-slate-200 hover:border-teal-500 hover:text-white transition"
                        >
                          <span>Dossier</span>
                          <ChevronRight className="h-3 w-3 text-slate-400" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="flex items-center justify-between border-t border-slate-800 px-4 py-3 bg-[#0B132B] text-xs text-slate-400">
          <div>
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total} schemes
          </div>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="rounded border border-slate-700 bg-slate-800 px-2.5 py-1 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700 transition"
            >
              Previous
            </button>
            <span className="px-2 font-mono text-slate-200">
              Page {page} of {Math.max(1, Math.ceil(total / pageSize))}
            </span>
            <button
              disabled={page * pageSize >= total}
              onClick={() => setPage(page + 1)}
              className="rounded border border-slate-700 bg-slate-800 px-2.5 py-1 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700 transition"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
