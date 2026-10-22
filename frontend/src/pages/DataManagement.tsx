import React, { useState } from 'react';
import {
  FileSpreadsheet,
  Upload,
  Download,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  FileCheck,
  XCircle,
} from 'lucide-react';
import { previewCsv, commitCsv } from '../services/api';

export const DataManagement: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [committing, setCommitting] = useState(false);
  const [commitResult, setCommitResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (selectedFile: File) => {
    if (!selectedFile.name.endsWith('.csv')) {
      setError('Please select a valid CSV file (.csv)');
      return;
    }
    setFile(selectedFile);
    setError(null);
    setCommitResult(null);
    setLoading(true);

    try {
      const data = await previewCsv(selectedFile);
      setPreview(data);
    } catch (err: any) {
      setError(err.message || 'Failed to parse CSV file');
    } finally {
      setLoading(false);
    }
  };

  const handleCommit = async () => {
    if (!file) return;
    setCommitting(true);
    try {
      const res = await commitCsv(file);
      setCommitResult(res);
      setPreview(null);
      setFile(null);
    } catch (err: any) {
      setError('Import transaction failed: ' + err.message);
    } finally {
      setCommitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title & Template Download Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <FileSpreadsheet className="h-5 w-5 text-teal-400" />
            <span>Data Ingestion & Schema Validation Studio</span>
          </h2>
          <p className="text-xs text-slate-400">
            Import monthly monitoring updates, validate data integrity, and update risk pipelines
          </p>
        </div>

        <a
          href="/api/v1/data/sample-csv"
          download="paimana_projects_template.csv"
          className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-3.5 py-1.5 text-xs font-semibold text-slate-200 hover:border-teal-500 hover:text-white transition"
        >
          <Download className="h-4 w-4 text-teal-400" />
          <span>Download Sample Template CSV</span>
        </a>
      </div>

      {/* Upload Drag & Drop Area */}
      <div className="rounded-xl border-2 border-dashed border-slate-700 hover:border-teal-500 bg-[#0F172A] p-8 text-center transition">
        <Upload className="mx-auto h-10 w-10 text-slate-400 mb-3" />
        <h3 className="text-sm font-bold text-white">Upload Infrastructure Progress Records (CSV)</h3>
        <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
          Files are automatically checked for date logic, budget constraints, duplicate keys, and schema compatibility before committing.
        </p>

        <label className="mt-4 inline-flex items-center gap-2 cursor-pointer rounded-lg bg-teal-600 px-4 py-2 text-xs font-semibold text-white hover:bg-teal-500 transition">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
            className="hidden"
          />
          <span>Select CSV Document</span>
        </label>
        {file && <div className="mt-2 text-xs font-mono text-teal-400 font-semibold">{file.name}</div>}
      </div>

      {loading && (
        <div className="flex items-center justify-center p-8 text-teal-400 gap-2 text-xs font-semibold">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span>Validating schema fields, row constraints, and date sequences...</span>
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-rose-900/50 bg-rose-950/20 p-4 text-xs text-rose-300 flex items-center gap-2">
          <XCircle className="h-5 w-5 text-rose-400 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {commitResult && (
        <div className="rounded-xl border border-emerald-900/50 bg-emerald-950/30 p-5 space-y-2">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
            <CheckCircle2 className="h-5 w-5" />
            <span>Import Transaction Completed Successfully</span>
          </div>
          <p className="text-xs text-slate-300">{commitResult.message}</p>
          <div className="text-xs font-mono text-emerald-300">
            Imported: {commitResult.imported_count} projects | Skipped: {commitResult.skipped_count}
          </div>
        </div>
      )}

      {/* Validation Preview Card */}
      {preview && (
        <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-5 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <FileCheck className="h-4 w-4 text-teal-400" />
                <span>Pre-Commit Validation Report</span>
              </h3>
              <p className="text-xs text-slate-400">
                Dry-run results: {preview.valid_rows} valid records, {preview.invalid_rows} invalid rows
              </p>
            </div>

            <button
              onClick={handleCommit}
              disabled={!preview.can_commit || committing}
              className={`rounded-lg px-4 py-2 text-xs font-bold transition flex items-center gap-2 ${
                preview.can_commit
                  ? 'bg-emerald-600 text-white hover:bg-emerald-500'
                  : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
              }`}
            >
              {committing && <RefreshCw className="h-3.5 w-3.5 animate-spin" />}
              <span>{preview.can_commit ? 'Commit to Database' : 'Resolve Errors to Commit'}</span>
            </button>
          </div>

          {/* Validation Errors Table if any */}
          {preview.errors.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider">
                Integrity Violations & Warnings ({preview.errors.length})
              </h4>
              <div className="rounded-lg border border-slate-800 overflow-hidden max-h-56 overflow-y-auto">
                <table className="w-full text-left text-xs">
                  <thead className="border-b border-slate-800 bg-[#0B132B] text-slate-400">
                    <tr>
                      <th className="py-2 px-3">Row</th>
                      <th className="py-2 px-3">Column</th>
                      <th className="py-2 px-3">Value</th>
                      <th className="py-2 px-3">Violation Message</th>
                      <th className="py-2 px-3">Severity</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {preview.errors.map((err: any, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-800/40">
                        <td className="py-2 px-3 font-mono text-slate-400">{err.row}</td>
                        <td className="py-2 px-3 font-mono text-teal-400">{err.column}</td>
                        <td className="py-2 px-3 text-slate-300 font-mono">{String(err.value)}</td>
                        <td className="py-2 px-3 text-slate-200">{err.message}</td>
                        <td className="py-2 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              err.severity === 'ERROR'
                                ? 'bg-rose-950 text-rose-400 border border-rose-800'
                                : 'bg-amber-950 text-amber-400 border border-amber-800'
                            }`}
                          >
                            {err.severity}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Data Preview Rows */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Data Sample (First {preview.preview_data.length} Rows)
            </h4>
            <div className="rounded-lg border border-slate-800 overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="border-b border-slate-800 bg-[#0B132B] text-slate-400">
                  <tr>
                    {preview.columns_detected.map((col: string) => (
                      <th key={col} className="py-2.5 px-3 font-mono whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {preview.preview_data.map((row: any, rIdx: number) => (
                    <tr key={rIdx} className="hover:bg-slate-800/30">
                      {preview.columns_detected.map((col: string) => (
                        <td key={col} className="py-2 px-3 text-slate-300 whitespace-nowrap">
                          {row[col] || '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
