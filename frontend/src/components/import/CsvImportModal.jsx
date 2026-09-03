import React, { useState } from 'react';
import { providerAPI } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import { Modal } from '../common/Modal';
import { UploadCloud, FileSpreadsheet, Download, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';

export const CsvImportModal = ({ isOpen, onClose, onSuccess }) => {
  const { showSuccess, showError } = useToast();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      showError('Please select a CSV file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      const res = await providerAPI.importCsv(formData);
      setResult(res.data);
      if (res.data.imported_count > 0) {
        showSuccess(`Imported ${res.data.imported_count} trainees successfully!`);
        if (onSuccess) onSuccess();
      } else {
        showError('No records could be imported. Please review validation errors.');
      }
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to upload CSV');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Batch Ingest Trainee Outcomes (CSV)" maxWidth="max-w-2xl">
      <div className="space-y-5">
        {/* Template info banner */}
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs">
          <div className="flex items-center gap-2 text-slate-300">
            <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
            <span>Required headers: <code>name, course, assessment_score, skills...</code></span>
          </div>
          <a
            href={providerAPI.downloadSampleCsvUrl}
            download="skillpulse_trainee_import_template.csv"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 font-semibold hover:bg-emerald-500/20 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            Download Sample CSV
          </a>
        </div>

        {/* Upload form */}
        {!result ? (
          <form onSubmit={handleUpload} className="space-y-4">
            <div className="border-2 border-dashed border-slate-700 hover:border-emerald-500/50 rounded-2xl p-8 text-center bg-slate-950/40 transition-colors">
              <input
                type="file"
                id="csv-file-input"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
              />
              <label
                htmlFor="csv-file-input"
                className="cursor-pointer flex flex-col items-center justify-center gap-2"
              >
                <div className="p-3.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <div className="text-sm font-semibold text-slate-200">
                  {file ? file.name : 'Click to select or drag & drop CSV file'}
                </div>
                <div className="text-xs text-slate-400">
                  {file ? `${(file.size / 1024).toFixed(1)} KB` : 'Supports standard UTF-8 encoded .csv files'}
                </div>
              </label>
            </div>

            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!file || uploading}
                className="px-5 py-2 rounded-xl text-xs font-bold bg-emerald-600 text-white hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-950 disabled:opacity-50 flex items-center gap-2"
              >
                {uploading ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Validating & Ingesting...</span>
                  </>
                ) : (
                  'Validate & Import Data'
                )}
              </button>
            </div>
          </form>
        ) : (
          /* Validation Result View */
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <div className="text-xs text-slate-400">Total Rows</div>
                <div className="text-xl font-bold text-white mt-1">{result.total_records}</div>
              </div>
              <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/30">
                <div className="text-xs text-emerald-400">Successfully Ingested</div>
                <div className="text-xl font-bold text-emerald-300 mt-1">{result.imported_count}</div>
              </div>
              <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/30">
                <div className="text-xs text-rose-400">Failed Records</div>
                <div className="text-xl font-bold text-rose-300 mt-1">{result.failed_count}</div>
              </div>
            </div>

            {/* Error inspector */}
            {result.errors && result.errors.length > 0 && (
              <div className="p-4 rounded-xl bg-slate-950 border border-rose-500/30 space-y-2">
                <div className="flex items-center gap-2 text-xs font-bold text-rose-400">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Validation Errors Detected ({result.errors.length})</span>
                </div>
                <div className="max-h-40 overflow-y-auto space-y-1.5 text-xs text-slate-300">
                  {result.errors.map((err, idx) => (
                    <div key={idx} className="p-2 rounded bg-slate-900/80 border border-slate-800 flex justify-between">
                      <span>Row {err.row} {err.trainee_id ? `(${err.trainee_id})` : ''}</span>
                      <span className="text-rose-400">{err.error}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={handleReset}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
              >
                Upload Another File
              </button>
              <button
                onClick={onClose}
                className="px-5 py-2 rounded-xl text-xs font-bold bg-emerald-600 text-white hover:bg-emerald-500 transition-all"
              >
                Done
              </button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};
