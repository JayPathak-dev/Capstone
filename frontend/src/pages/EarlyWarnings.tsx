import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  ShieldAlert,
  Filter,
  RefreshCw,
  Check,
  FileText,
} from 'lucide-react';
import { fetchAlerts, updateAlertStatus } from '../services/api';
import { Alert } from '../types';
import { RiskBadge } from '../components/common/RiskBadge';

interface EarlyWarningsProps {
  onSelectProject: (projectId: string) => void;
}

export const EarlyWarnings: React.FC<EarlyWarningsProps> = ({ onSelectProject }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [severity, setSeverity] = useState('ALL');
  const [status, setStatus] = useState('ALL');
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [resolutionNotes, setResolutionNotes] = useState('');

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const res = await fetchAlerts({
        limit: 100,
        severity,
        status,
      });
      setAlerts(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [severity, status]);

  const handleAcknowledge = async (alertId: string) => {
    try {
      await updateAlertStatus(alertId, 'ACKNOWLEDGED', 'Notified responsible field engineer.');
      loadAlerts();
    } catch (err: any) {
      alert('Failed to acknowledge alert: ' + err.message);
    }
  };

  const handleResolve = async (alertId: string) => {
    try {
      await updateAlertStatus(
        alertId,
        'RESOLVED',
        resolutionNotes.trim() || 'Corrective action implemented and verified on site.'
      );
      setResolvingId(null);
      setResolutionNotes('');
      loadAlerts();
    } catch (err: any) {
      alert('Failed to resolve alert: ' + err.message);
    }
  };

  const critCount = alerts.filter((a) => a.severity === 'CRITICAL').length;
  const highCount = alerts.filter((a) => a.severity === 'HIGH').length;
  const newCount = alerts.filter((a) => a.status === 'NEW').length;

  return (
    <div className="space-y-6">
      {/* Title & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-400" />
            <span>Early Warning & Anomaly Center</span>
          </h2>
          <p className="text-xs text-slate-400">
            Automated alerts triggered by budget burn discrepancies, schedule slippage, and milestone breaches
          </p>
        </div>

        <button
          onClick={loadAlerts}
          className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3.5 py-1.5 text-xs font-semibold text-slate-300 hover:text-white transition"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Ticker / Stat Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-xl border border-rose-900/40 bg-rose-950/20 p-4">
          <div className="text-[11px] font-semibold text-rose-300 uppercase">Critical Severity</div>
          <div className="text-2xl font-bold font-mono text-rose-400 mt-1">{critCount} Alerts</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Requiring Secretary / PMO intervention</div>
        </div>

        <div className="rounded-xl border border-orange-900/40 bg-orange-950/20 p-4">
          <div className="text-[11px] font-semibold text-orange-300 uppercase">High Severity</div>
          <div className="text-2xl font-bold font-mono text-orange-400 mt-1">{highCount} Alerts</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Requiring contractor cure notices</div>
        </div>

        <div className="rounded-xl border border-teal-900/40 bg-teal-950/20 p-4">
          <div className="text-[11px] font-semibold text-teal-300 uppercase">Pending Acknowledgments</div>
          <div className="text-2xl font-bold font-mono text-teal-400 mt-1">{newCount} Unread</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Awaiting Project Officer review</div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-4 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 text-xs text-slate-400 font-semibold mr-2">
          <Filter className="h-3.5 w-3.5" />
          <span>Filters:</span>
        </div>

        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
        >
          <option value="ALL">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
        </select>

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
        >
          <option value="ALL">All Statuses</option>
          <option value="NEW">New (Unreviewed)</option>
          <option value="ACKNOWLEDGED">Acknowledged</option>
          <option value="RESOLVED">Resolved</option>
        </select>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin text-teal-400" />
          </div>
        ) : alerts.length === 0 ? (
          <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-12 text-center text-xs text-slate-400">
            <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-400 mb-2" />
            <span className="font-semibold text-slate-200">No active early warnings matching filters</span>
            <p className="text-slate-500 mt-1">All monitored parameters are running within nominal boundaries.</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className="rounded-xl border border-slate-800 bg-[#0F172A] p-5 shadow-sm space-y-3 hover:border-slate-700 transition"
            >
              {/* Card Header */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <RiskBadge level={alert.severity} size="sm" />
                  <span className="font-mono text-xs font-bold text-teal-400">
                    {alert.project_code}
                  </span>
                  <span className="text-xs text-slate-400">• {alert.sector}</span>
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded font-mono font-semibold uppercase ${
                      alert.status === 'RESOLVED'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        : alert.status === 'ACKNOWLEDGED'
                        ? 'bg-amber-950 text-amber-400 border border-amber-800'
                        : 'bg-rose-950 text-rose-400 border border-rose-800'
                    }`}
                  >
                    {alert.status}
                  </span>
                  <span className="text-[10px] text-slate-500">
                    {alert.created_at ? new Date(alert.created_at).toLocaleDateString() : 'Active'}
                  </span>
                </div>
              </div>

              {/* Title & Description */}
              <div>
                <h3
                  onClick={() => alert.project_id && onSelectProject(alert.project_id)}
                  className="text-sm font-bold text-white hover:text-teal-300 cursor-pointer transition"
                >
                  {alert.title}
                </h3>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed">{alert.description}</p>
              </div>

              {/* Action Prescription Box */}
              <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-3.5 text-xs">
                <div className="flex items-center gap-1.5 text-teal-400 font-semibold text-[11px] uppercase tracking-wider mb-1">
                  <ShieldAlert className="h-3.5 w-3.5" />
                  <span>Mandated Operational Next Step</span>
                </div>
                <p className="text-slate-300">{alert.recommended_action}</p>
              </div>

              {/* Actions Footer */}
              <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
                <button
                  onClick={() => alert.project_id && onSelectProject(alert.project_id)}
                  className="text-xs text-teal-400 hover:text-teal-300 font-medium"
                >
                  View Project Dossier →
                </button>

                <div className="flex items-center gap-2">
                  {alert.status === 'NEW' && (
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      className="rounded border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-200 hover:border-amber-500 hover:text-white transition flex items-center gap-1.5"
                    >
                      <Check className="h-3 w-3 text-amber-400" />
                      <span>Acknowledge</span>
                    </button>
                  )}

                  {alert.status !== 'RESOLVED' && (
                    <>
                      {resolvingId === alert.id ? (
                        <div className="flex items-center gap-2">
                          <input
                            type="text"
                            placeholder="Add resolution remarks..."
                            value={resolutionNotes}
                            onChange={(e) => setResolutionNotes(e.target.value)}
                            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200 focus:outline-none"
                          />
                          <button
                            onClick={() => handleResolve(alert.id)}
                            className="rounded bg-teal-600 px-3 py-1 text-xs font-semibold text-white hover:bg-teal-500 transition"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setResolvingId(null)}
                            className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-400 hover:text-white"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => {
                            setResolvingId(alert.id);
                            setResolutionNotes('');
                          }}
                          className="rounded bg-teal-600/90 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-500 transition flex items-center gap-1.5"
                        >
                          <CheckCircle2 className="h-3 w-3" />
                          <span>Resolve Warning</span>
                        </button>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
