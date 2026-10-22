import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  RefreshCw,
  Clock,
  IndianRupee,
  Layers,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  Building2,
  MapPin,
  ExternalLink,
  ShieldAlert,
  Sparkles,
} from 'lucide-react';
import { fetchProjectDetails, fetchProjectRisk, triggerProjectPrediction, updateAlertStatus } from '../services/api';
import { RiskDetail, Alert } from '../types';
import { RiskBadge } from '../components/common/RiskBadge';

interface ProjectDetailProps {
  projectId: string;
  onBack: () => void;
  onBenchmark?: (projectId: string) => void;
}

export const ProjectDetail: React.FC<ProjectDetailProps> = ({
  projectId,
  onBack,
  onBenchmark,
}) => {
  const [project, setProject] = useState<any>(null);
  const [risk, setRisk] = useState<RiskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [repredicting, setRepredicting] = useState(false);
  const [activeTab, setActiveTab] = useState<'risk' | 'milestones' | 'updates' | 'alerts'>('risk');
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [projData, riskData] = await Promise.all([
        fetchProjectDetails(projectId),
        fetchProjectRisk(projectId),
      ]);
      setProject(projData);
      setRisk(riskData);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, [projectId]);

  const handleRepredict = async () => {
    setRepredicting(true);
    try {
      const newRisk = await triggerProjectPrediction(projectId);
      setRisk(newRisk);
      const updatedProj = await fetchProjectDetails(projectId);
      setProject(updatedProj);
      setActionSuccess('Prediction updated in real-time using current monitoring data.');
      setTimeout(() => setActionSuccess(null), 4000);
    } catch (err: any) {
      alert('Failed to re-run prediction: ' + err.message);
    } finally {
      setRepredicting(false);
    }
  };

  const handleResolveAlert = async (alertId: string) => {
    try {
      await updateAlertStatus(alertId, 'RESOLVED', 'Acknowledged and addressed by Project Officer.');
      const updatedProj = await fetchProjectDetails(projectId);
      setProject(updatedProj);
    } catch (err: any) {
      alert('Error updating alert: ' + err.message);
    }
  };

  if (loading || !project || !risk) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="flex items-center gap-3 text-teal-400">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span className="text-sm font-medium">Loading project dossier and risk model...</span>
        </div>
      </div>
    );
  }

  const costVariance = risk.forecast_final_cost - project.approved_budget;
  const isOverrun = costVariance > 0;

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:text-white hover:border-slate-600 transition"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <div className="flex items-center gap-2.5">
              <span className="font-mono text-xs font-bold text-teal-400 bg-teal-950/60 px-2 py-0.5 rounded border border-teal-800">
                {project.project_code}
              </span>
              <RiskBadge level={risk.risk_level} score={risk.risk_score} size="md" />
              <span className="rounded bg-slate-800 text-slate-300 text-xs px-2 py-0.5 border border-slate-700">
                {project.project_status}
              </span>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-white mt-1">
              {project.project_name}
            </h2>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          {onBenchmark && (
            <button
              onClick={() => onBenchmark(project.id)}
              className="rounded-lg border border-slate-700 bg-slate-800 px-3.5 py-1.5 text-xs font-semibold text-slate-200 hover:border-teal-500 hover:text-white transition flex items-center gap-1.5"
            >
              <span>Benchmark with Peers</span>
              <ExternalLink className="h-3.5 w-3.5 text-teal-400" />
            </button>
          )}

          <button
            onClick={handleRepredict}
            disabled={repredicting}
            className="flex items-center gap-1.5 rounded-lg bg-teal-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-teal-500 transition disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${repredicting ? 'animate-spin' : ''}`} />
            <span>{repredicting ? 'Evaluating ML...' : 'Re-Run Prediction'}</span>
          </button>
        </div>
      </div>

      {actionSuccess && (
        <div className="rounded-lg border border-emerald-800 bg-emerald-950/40 p-3 text-xs text-emerald-300 flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Meta Specs Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 rounded-xl border border-slate-800 bg-[#0F172A] p-4 text-xs">
        <div>
          <span className="text-slate-400">Implementing Agency</span>
          <div className="font-semibold text-white mt-0.5 flex items-center gap-1.5">
            <Building2 className="h-3.5 w-3.5 text-teal-400" />
            <span>{project.implementing_agency}</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">{project.department}</div>
        </div>

        <div>
          <span className="text-slate-400">Sector & Geographic Zone</span>
          <div className="font-semibold text-white mt-0.5 flex items-center gap-1.5">
            <MapPin className="h-3.5 w-3.5 text-teal-400" />
            <span>{project.sector}</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">{project.region} Region</div>
        </div>

        <div>
          <span className="text-slate-400">Planned Start & End</span>
          <div className="font-semibold text-white mt-0.5 flex items-center gap-1.5">
            <Calendar className="h-3.5 w-3.5 text-teal-400" />
            <span>{project.planned_start_date}</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Target: {project.expected_completion_date}</div>
        </div>

        <div>
          <span className="text-slate-400">Model Engine Version</span>
          <div className="font-semibold text-teal-300 mt-0.5 font-mono">
            {risk.model_version}
          </div>
          <div className="text-[10px] text-slate-500">
            {risk.is_fallback ? 'Calibrated Heuristic Fallback' : 'Active Gradient Boosting Pipeline'}
          </div>
        </div>
      </div>

      {/* Key Metric Highlights Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Approved Outlay */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
          <div className="text-[11px] font-medium uppercase text-slate-400">Sanctioned Outlay</div>
          <div className="mt-2 text-2xl font-bold font-mono text-white">
            ₹ {project.approved_budget.toLocaleString()} Cr
          </div>
          {project.revised_budget && (
            <div className="mt-1 text-xs text-amber-400">
              Revised: ₹ {project.revised_budget.toLocaleString()} Cr
            </div>
          )}
        </div>

        {/* Incurred Expenditure */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
          <div className="text-[11px] font-medium uppercase text-slate-400">Actual Expenditure</div>
          <div className="mt-2 text-2xl font-bold font-mono text-teal-400">
            ₹ {project.actual_expenditure.toLocaleString()} Cr
          </div>
          <div className="mt-1 text-xs text-slate-400">
            {project.current_financial_progress.toFixed(1)}% of sanction disbursed
          </div>
        </div>

        {/* Forecast Final Cost */}
        <div className={`rounded-xl border p-4 ${
          isOverrun ? 'border-rose-900/50 bg-rose-950/20' : 'border-slate-800 bg-slate-900/80'
        }`}>
          <div className="text-[11px] font-medium uppercase text-slate-400">Forecast Final Cost</div>
          <div className={`mt-2 text-2xl font-bold font-mono ${isOverrun ? 'text-rose-400' : 'text-emerald-400'}`}>
            ₹ {risk.forecast_final_cost.toLocaleString()} Cr
          </div>
          <div className="mt-1 text-xs font-medium">
            {isOverrun ? (
              <span className="text-rose-400">+₹ {costVariance.toLocaleString()} Cr Overrun</span>
            ) : (
              <span className="text-emerald-400">Within Sanction</span>
            )}
          </div>
        </div>

        {/* Predicted Schedule Delay */}
        <div className={`rounded-xl border p-4 ${
          risk.predicted_delay_days > 60 ? 'border-amber-900/50 bg-amber-950/20' : 'border-slate-800 bg-slate-900/80'
        }`}>
          <div className="text-[11px] font-medium uppercase text-slate-400">Predicted Delay</div>
          <div className={`mt-2 text-2xl font-bold font-mono ${
            risk.predicted_delay_days > 60 ? 'text-amber-400' : 'text-slate-200'
          }`}>
            {risk.predicted_delay_days > 0 ? `+${risk.predicted_delay_days} Days` : 'On Time'}
          </div>
          <div className="mt-1 text-xs text-slate-400">
            Probability of delay: {(risk.delay_probability * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex border-b border-slate-800 text-xs font-medium">
        <button
          onClick={() => setActiveTab('risk')}
          className={`py-3 px-5 border-b-2 font-semibold transition ${
            activeTab === 'risk'
              ? 'border-teal-500 text-teal-400 bg-slate-900/40'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          Predictive Risk & Explainability (XAI)
        </button>
        <button
          onClick={() => setActiveTab('milestones')}
          className={`py-3 px-5 border-b-2 font-semibold transition ${
            activeTab === 'milestones'
              ? 'border-teal-500 text-teal-400 bg-slate-900/40'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          Milestones Tracker ({project.milestones?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('updates')}
          className={`py-3 px-5 border-b-2 font-semibold transition ${
            activeTab === 'updates'
              ? 'border-teal-500 text-teal-400 bg-slate-900/40'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          Monthly Updates History ({project.progress_updates?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('alerts')}
          className={`py-3 px-5 border-b-2 font-semibold transition ${
            activeTab === 'alerts'
              ? 'border-teal-500 text-teal-400 bg-slate-900/40'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          Active Warnings ({project.alerts?.length || 0})
        </button>
      </div>

      {/* Tab 1: Risk & Explainability */}
      {activeTab === 'risk' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Risk Breakdown Summary */}
            <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-5">
              <h3 className="text-sm font-semibold text-white mb-2">Composite Risk Scoring</h3>
              <p className="text-xs text-slate-400 mb-4">
                Calibrated 0-100 index combining cost risk, schedule slippage, physical-financial gap, and milestone bottlenecks.
              </p>

              <div className="flex items-center justify-center p-6 bg-slate-950/60 rounded-xl border border-slate-800/80 mb-4">
                <div className="text-center">
                  <div className="text-4xl font-extrabold font-mono text-white">
                    {risk.risk_score.toFixed(1)}
                  </div>
                  <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mt-1">
                    Index Score / 100
                  </div>
                  <div className="mt-2.5">
                    <RiskBadge level={risk.risk_level} size="lg" />
                  </div>
                </div>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1.5 border-b border-slate-800 text-slate-300">
                  <span>Cost Overrun Probability:</span>
                  <span className="font-mono font-bold text-white">
                    {(risk.cost_overrun_probability * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-800 text-slate-300">
                  <span>Schedule Delay Probability:</span>
                  <span className="font-mono font-bold text-white">
                    {(risk.delay_probability * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-800 text-slate-300">
                  <span>Physical Execution Rate:</span>
                  <span className="font-mono font-bold text-teal-400">
                    {project.current_physical_progress.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between py-1.5 text-slate-300">
                  <span>Financial Burn Rate:</span>
                  <span className="font-mono font-bold text-amber-400">
                    {project.current_financial_progress.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Top Contributing Factors (SHAP Drivers) */}
            <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-[#0F172A] p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-teal-400" />
                    <span>Explainable Risk Drivers (XAI)</span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    Feature attributions identifying root causes behind the {risk.risk_score.toFixed(1)} risk score
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                {risk.explanation.top_factors.map((factor, idx) => (
                  <div
                    key={idx}
                    className="rounded-lg border border-slate-800 bg-slate-900/80 p-3.5 space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-200">{factor.factor}</span>
                      <span className="font-mono text-xs font-semibold text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-900">
                        {factor.impact}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">{factor.description}</p>
                  </div>
                ))}
              </div>

              {/* Recommended Actions */}
              <div className="mt-5 rounded-lg border border-teal-900/60 bg-teal-950/20 p-4">
                <h4 className="text-xs font-bold text-teal-300 uppercase tracking-wider mb-2">
                  Prescriptive Corrective Actions
                </h4>
                <ul className="space-y-1.5 text-xs text-slate-300 list-disc list-inside">
                  {risk.explanation.recommended_actions.map((act, i) => (
                    <li key={i}>{act}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Milestones Tracker */}
      {activeTab === 'milestones' && (
        <div className="rounded-xl border border-slate-800 bg-[#0F172A] overflow-hidden">
          <div className="p-4 border-b border-slate-800">
            <h3 className="text-sm font-semibold text-white">Work Breakdown Structure (WBS) Milestones</h3>
            <p className="text-xs text-slate-400">Contractual deliverables on the project critical path</p>
          </div>
          <div className="divide-y divide-slate-800/60">
            {project.milestones?.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">No milestones recorded.</div>
            ) : (
              project.milestones.map((m: any, idx: number) => (
                <div key={m.id} className="p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-800 text-xs font-bold text-slate-300 border border-slate-700 flex-shrink-0 mt-0.5">
                      {idx + 1}
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">{m.milestone_name}</div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        Target Date: <span className="font-mono text-slate-300">{m.planned_date}</span>
                        {m.actual_date && (
                          <span> | Completed: <span className="font-mono text-emerald-400">{m.actual_date}</span></span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="w-28 text-right">
                      <div className="font-mono text-xs font-semibold text-slate-200">
                        {m.completion_percentage.toFixed(0)}%
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
                        <div
                          className={`h-full rounded-full ${
                            m.status === 'COMPLETED' ? 'bg-emerald-400' : m.status === 'DELAYED' ? 'bg-rose-500' : 'bg-teal-400'
                          }`}
                          style={{ width: `${m.completion_percentage}%` }}
                        />
                      </div>
                    </div>

                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-medium border ${
                        m.status === 'COMPLETED'
                          ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
                          : m.status === 'DELAYED'
                          ? 'bg-rose-950 text-rose-400 border-rose-800'
                          : 'bg-slate-800 text-slate-300 border-slate-700'
                      }`}
                    >
                      {m.status}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Monthly Progress Updates */}
      {activeTab === 'updates' && (
        <div className="rounded-xl border border-slate-800 bg-[#0F172A] overflow-hidden">
          <div className="p-4 border-b border-slate-800">
            <h3 className="text-sm font-semibold text-white">Periodic Progress Logs</h3>
            <p className="text-xs text-slate-400">Monthly inspection vouchers and ground-truth measurements</p>
          </div>
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 bg-[#0B132B] text-slate-400">
              <tr>
                <th className="py-3 px-4 font-semibold">Reporting Date</th>
                <th className="py-3 px-4 font-semibold">Planned Progress</th>
                <th className="py-3 px-4 font-semibold">Actual Progress</th>
                <th className="py-3 px-4 font-semibold">Cumulative Spend</th>
                <th className="py-3 px-4 font-semibold">Reported Field Bottlenecks</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {project.progress_updates?.map((u: any) => (
                <tr key={u.id} className="hover:bg-slate-800/30">
                  <td className="py-3 px-4 font-mono font-semibold text-teal-400">{u.reporting_date}</td>
                  <td className="py-3 px-4 font-mono text-slate-300">{u.planned_progress.toFixed(1)}%</td>
                  <td className="py-3 px-4 font-mono text-white font-semibold">{u.actual_progress.toFixed(1)}%</td>
                  <td className="py-3 px-4 font-mono text-slate-300">₹ {u.cumulative_expenditure.toLocaleString()} Cr</td>
                  <td className="py-3 px-4 text-slate-400">
                    {u.reported_issues ? (
                      <span className="text-amber-300 font-medium">{u.reported_issues}</span>
                    ) : (
                      <span className="text-slate-600">Routine progress; no escalation.</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 4: Project Early Warnings */}
      {activeTab === 'alerts' && (
        <div className="space-y-4">
          {project.alerts?.length === 0 ? (
            <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-8 text-center text-xs text-slate-400">
              <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-500 mb-2" />
              <span className="font-semibold text-slate-200">No active early warnings for this project</span>
              <p className="text-slate-500 mt-1">Variance parameters are operating within safe contract boundaries.</p>
            </div>
          ) : (
            project.alerts.map((a: Alert) => (
              <div
                key={a.id}
                className="rounded-xl border border-slate-800 bg-[#0F172A] p-5 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <RiskBadge level={a.severity} size="sm" />
                    <span className="text-xs font-mono text-slate-400">[{a.alert_type}]</span>
                  </div>
                  <span
                    className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                      a.status === 'RESOLVED'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        : a.status === 'ACKNOWLEDGED'
                        ? 'bg-amber-950 text-amber-400 border border-amber-800'
                        : 'bg-rose-950 text-rose-400 border border-rose-800'
                    }`}
                  >
                    {a.status}
                  </span>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-white">{a.title}</h4>
                  <p className="text-xs text-slate-400 mt-1">{a.description}</p>
                </div>

                <div className="rounded-lg bg-slate-900/80 p-3 border border-slate-800 text-xs">
                  <span className="font-semibold text-teal-400 uppercase text-[10px] tracking-wider block mb-1">
                    Mandated Remedy
                  </span>
                  <p className="text-slate-300">{a.recommended_action}</p>
                </div>

                {a.status !== 'RESOLVED' && (
                  <div className="flex justify-end pt-2">
                    <button
                      onClick={() => handleResolveAlert(a.id)}
                      className="rounded bg-teal-600 px-3 py-1 text-xs font-semibold text-white hover:bg-teal-500 transition"
                    >
                      Mark as Resolved
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
