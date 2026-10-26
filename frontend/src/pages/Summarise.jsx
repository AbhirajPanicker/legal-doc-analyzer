/**
 * Summarise page — select a document and generate a structured executive summary.
 */
import { useEffect, useState, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import {
  FileText, Sparkles, AlertTriangle, Users, Calendar,
  DollarSign, ShieldAlert, Scale, ChevronDown, ChevronUp,
  Info, Clock, RefreshCw, CheckCircle, FileDown, Printer,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { listDocuments, summariseDocument } from '../services/api';
import { exportSummaryMarkdown, printReport } from '../services/reportExporter';

// ── Severity colour map ───────────────────────────────────────────────────────
const SEVERITY = {
  high:   { bg: '#fff1f1', border: '#fca5a5', text: '#dc2626', dot: '#ef4444' },
  medium: { bg: '#fffbeb', border: '#fcd34d', text: '#d97706', dot: '#f59e0b' },
  low:    { bg: '#f0fdf4', border: '#86efac', text: '#16a34a', dot: '#22c55e' },
};

// ── Small helpers ─────────────────────────────────────────────────────────────
function SectionCard({ icon: Icon, title, color = 'var(--navy-500)', children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={{
      border: '1px solid var(--border)', borderRadius: 12,
      overflow: 'hidden', marginBottom: 14,
      boxShadow: 'var(--shadow-sm)',
    }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          width: '100%', display: 'flex', alignItems: 'center', gap: 10,
          padding: '13px 16px', background: 'var(--surface)',
          border: 'none', cursor: 'pointer', textAlign: 'left',
        }}
      >
        <span style={{
          width: 32, height: 32, borderRadius: 8,
          background: `${color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexShrink: 0,
        }}>
          <Icon size={15} color={color} />
        </span>
        <span style={{ fontWeight: 700, fontSize: 13.5, flex: 1 }}>{title}</span>
        {open ? <ChevronUp size={14} color="var(--text-muted)" /> : <ChevronDown size={14} color="var(--text-muted)" />}
      </button>
      {open && (
        <div style={{ padding: '0 16px 16px', background: 'var(--surface-2)', borderTop: '1px solid var(--border)' }}>
          {children}
        </div>
      )}
    </div>
  );
}

function EmptyField({ text = 'Not specified in document' }) {
  return <span style={{ color: 'var(--text-muted)', fontStyle: 'italic', fontSize: 13 }}>{text}</span>;
}

// ── Main component ────────────────────────────────────────────────────────────
export default function Summarise() {
  const location = useLocation();
  const [docs, setDocs] = useState([]);
  const [docsLoading, setDocsLoading] = useState(true);
  const [selectedDocId, setSelectedDocId] = useState(location.state?.docId || '');
  const [summary, setSummary] = useState(null);
  const [generating, setGenerating] = useState(false);

  // Load document list on mount
  useEffect(() => {
    listDocuments()
      .then(r => {
        const ready = r.data.documents.filter(d => d.status === 'ready');
        setDocs(ready);
        if (location.state?.docId && ready.some(d => d.id === location.state.docId)) {
          setSelectedDocId(location.state.docId);
        }
      })
      .catch(() => toast.error('Failed to load documents.'))
      .finally(() => setDocsLoading(false));
  }, [location.state?.docId]);

  const handleGenerate = useCallback(async () => {
    if (!selectedDocId) return;
    setSummary(null);
    setGenerating(true);
    try {
      const r = await summariseDocument(selectedDocId);
      setSummary(r.data);
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Summarisation failed. Please try again.';
      toast.error(msg);
    } finally {
      setGenerating(false);
    }
  }, [selectedDocId]);

  const selectedDoc = docs.find(d => d.id === selectedDocId);

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '28px 32px' }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, margin: '0 0 4px', display: 'flex', alignItems: 'center', gap: 10 }}>
          <Sparkles size={20} color="var(--gold-500)" />
          Document Summariser
        </h1>
        <p style={{ fontSize: 13.5, color: 'var(--text-muted)', margin: 0 }}>
          Generate a structured executive summary — parties, obligations, financial terms, risk flags, and more.
        </p>
      </div>

      {/* Controls card */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <span className="card-title">Select Document</span>
        </div>
        <div className="card-body" style={{ display: 'flex', gap: 12, alignItems: 'flex-end', flexWrap: 'wrap' }}>
          {docsLoading ? (
            <div className="spinner" />
          ) : docs.length === 0 ? (
            <div className="alert alert-info" style={{ flex: 1 }}>
              No ready documents found. Upload and index a PDF on the Documents page first.
            </div>
          ) : (
            <>
              <div style={{ flex: 1, minWidth: 260 }}>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6 }}>
                  Choose a document
                </label>
                <select
                  id="doc-select"
                  value={selectedDocId}
                  onChange={e => { setSelectedDocId(e.target.value); setSummary(null); }}
                  style={{
                    width: '100%', padding: '9px 12px', borderRadius: 8,
                    border: '1.5px solid var(--border)', background: 'var(--surface)',
                    fontSize: 13.5, color: 'var(--text-primary)', cursor: 'pointer',
                    outline: 'none',
                  }}
                >
                  <option value="">— Select a document —</option>
                  {docs.map(d => (
                    <option key={d.id} value={d.id}>
                      {d.original_name} ({d.page_count} pages)
                    </option>
                  ))}
                </select>
              </div>
              <button
                id="generate-summary-btn"
                className="btn btn-primary"
                disabled={!selectedDocId || generating}
                onClick={handleGenerate}
                style={{ height: 40, paddingInline: 22, whiteSpace: 'nowrap' }}
              >
                {generating ? (
                  <><div className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> Generating…</>
                ) : (
                  <><Sparkles size={14} /> Generate Summary</>
                )}
              </button>
            </>
          )}
        </div>
      </div>

      {/* Generating skeleton */}
      {generating && (
        <div className="card" style={{ padding: 40, textAlign: 'center', animation: 'fadeInUp .3s ease both' }}>
          <div className="spinner" style={{ margin: '0 auto 16px', width: 36, height: 36, borderWidth: 3 }} />
          <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 6 }}>Analysing document…</div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            The AI is reading and structuring the document. This may take 15–30 seconds for large files.
          </div>
        </div>
      )}

      {/* Summary output */}
      {summary && !generating && (
        <div style={{ animation: 'fadeInUp .4s ease both' }}>

          {/* Printable header */}
          <div className="print-only-header">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ margin: '0 0 4px', fontSize: 20 }}>LexAnalyzer — Legal Executive Summary</h2>
                <div style={{ fontSize: 13, color: '#4b5563' }}>Document: <strong>{selectedDoc?.original_name}</strong></div>
              </div>
              <div style={{ textAlign: 'right', fontSize: 12, color: '#6b7280' }}>
                <div>Date: {new Date().toLocaleDateString()}</div>
                <div>Mode: {summary.llm_used ? 'AI-Powered' : 'Offline Rule Engine'}</div>
              </div>
            </div>
          </div>

          {/* Action bar & LLM / offline badge */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
            {summary.llm_used ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12.5,
                color: '#16a34a', background: '#f0fdf4', border: '1px solid #86efac',
                borderRadius: 99, padding: '3px 12px', fontWeight: 600 }}>
                <CheckCircle size={12} /> AI-powered summary
              </span>
            ) : summary.llm_configured ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12.5,
                color: '#dc2626', background: '#fff1f1', border: '1px solid #fca5a5',
                borderRadius: 99, padding: '3px 12px', fontWeight: 600 }}>
                <AlertTriangle size={12} /> API key invalid or failed — offline extraction used
              </span>
            ) : (
              <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12.5,
                color: '#d97706', background: '#fffbeb', border: '1px solid #fcd34d',
                borderRadius: 99, padding: '3px 12px', fontWeight: 600 }}>
                <Info size={12} /> Offline extraction (add API key for richer results)
              </span>
            )}

            <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }} className="no-print">
              <button
                id="export-md-btn"
                className="btn btn-secondary btn-sm"
                onClick={() => {
                  exportSummaryMarkdown(selectedDoc?.original_name, summary);
                  toast.success('Summary exported as Markdown!');
                }}
                title="Download Markdown Report"
                style={{ gap: 6, fontSize: 12.5 }}
              >
                <FileDown size={14} /> Export .MD
              </button>
              <button
                id="export-pdf-btn"
                className="btn btn-primary btn-sm"
                onClick={() => printReport(`Legal_Summary_${selectedDoc?.original_name || 'Report'}`)}
                title="Print or Save as PDF"
                style={{ gap: 6, fontSize: 12.5 }}
              >
                <Printer size={14} /> Save PDF / Print
              </button>
              <button
                className="btn btn-secondary btn-sm"
                onClick={handleGenerate}
                title="Re-generate"
                style={{ gap: 6, fontSize: 12.5 }}
              >
                <RefreshCw size={12} /> Regenerate
              </button>
            </div>
          </div>

          {/* One-line summary banner */}
          {summary.one_line_summary && (
            <div style={{
              background: 'linear-gradient(135deg, var(--navy-800), var(--navy-600))',
              borderRadius: 12, padding: '18px 22px', marginBottom: 16,
              color: '#fff', display: 'flex', alignItems: 'flex-start', gap: 12,
            }}>
              <Sparkles size={18} color="var(--gold-400)" style={{ flexShrink: 0, marginTop: 2 }} />
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, opacity: 0.6, letterSpacing: '.06em',
                  textTransform: 'uppercase', marginBottom: 4 }}>Executive Summary</div>
                <div style={{ fontSize: 14.5, lineHeight: 1.6, fontWeight: 500 }}>{summary.one_line_summary}</div>
              </div>
            </div>
          )}

          {/* Document type + doc info row */}
          <div style={{ display: 'flex', gap: 12, marginBottom: 14, flexWrap: 'wrap' }}>
            {summary.document_type && (
              <div style={{
                flex: 1, minWidth: 200, background: 'var(--surface)', border: '1px solid var(--border)',
                borderRadius: 10, padding: '14px 16px',
              }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '.05em',
                  textTransform: 'uppercase', marginBottom: 4 }}>Document Type</div>
                <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--navy-600)' }}>{summary.document_type}</div>
              </div>
            )}
            {summary.governing_law && (
              <div style={{
                flex: 1, minWidth: 200, background: 'var(--surface)', border: '1px solid var(--border)',
                borderRadius: 10, padding: '14px 16px',
              }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '.05em',
                  textTransform: 'uppercase', marginBottom: 4 }}>Governing Law</div>
                <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--navy-600)' }}>{summary.governing_law}</div>
              </div>
            )}
          </div>

          {/* Parties */}
          <SectionCard icon={Users} title="Parties Involved" color="var(--navy-500)">
            <div style={{ paddingTop: 14 }}>
              {summary.parties.length === 0 ? <EmptyField /> : (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
                  {summary.parties.map((p, i) => (
                    <div key={i} style={{
                      background: 'var(--surface)', border: '1.5px solid var(--border)',
                      borderRadius: 10, padding: '10px 14px', minWidth: 180,
                    }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)',
                        textTransform: 'uppercase', letterSpacing: '.05em', marginBottom: 3 }}>{p.role}</div>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>{p.name}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </SectionCard>

          {/* Key dates */}
          <SectionCard icon={Calendar} title="Key Dates" color="#7c3aed">
            <div style={{ paddingTop: 14 }}>
              {summary.key_dates.length === 0 ? <EmptyField /> : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {summary.key_dates.map((kd, i) => (
                    <div key={i} style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      background: 'var(--surface)', border: '1px solid var(--border)',
                      borderRadius: 8, padding: '9px 14px', fontSize: 13.5,
                    }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)' }}>
                        <Clock size={12} /> {kd.label}
                      </span>
                      <span style={{ fontWeight: 600 }}>{kd.date}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </SectionCard>

          {/* Financial terms */}
          <SectionCard icon={DollarSign} title="Financial Terms" color="#059669">
            <div style={{ paddingTop: 14 }}>
              {summary.financial_terms.length === 0 ? <EmptyField /> : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {summary.financial_terms.map((ft, i) => (
                    <div key={i} style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      background: 'var(--surface)', border: '1px solid var(--border)',
                      borderRadius: 8, padding: '9px 14px', fontSize: 13.5,
                    }}>
                      <span style={{ color: 'var(--text-muted)' }}>{ft.label}</span>
                      <span style={{ fontWeight: 700, color: '#059669' }}>{ft.value}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </SectionCard>

          {/* Obligations */}
          <SectionCard icon={CheckCircle} title="Key Obligations" color="var(--navy-400)">
            <div style={{ paddingTop: 14 }}>
              {summary.obligations.length === 0 ? <EmptyField /> : (
                <ul style={{ margin: 0, padding: '0 0 0 18px', display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {summary.obligations.map((ob, i) => (
                    <li key={i} style={{ fontSize: 13.5, lineHeight: 1.6, color: 'var(--text-secondary)' }}>{ob}</li>
                  ))}
                </ul>
              )}
            </div>
          </SectionCard>

          {/* Termination */}
          {summary.termination_conditions && (
            <SectionCard icon={AlertTriangle} title="Termination Conditions" color="#d97706" defaultOpen={false}>
              <div style={{ paddingTop: 14, fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                {summary.termination_conditions}
              </div>
            </SectionCard>
          )}

          {/* Risk flags */}
          <SectionCard icon={ShieldAlert} title="Risk Flags" color="#dc2626" defaultOpen={true}>
            <div style={{ paddingTop: 14 }}>
              {summary.risk_flags.length === 0 ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13.5, color: '#16a34a' }}>
                  <CheckCircle size={15} /> No risk flags identified in this document.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {summary.risk_flags.map((rf, i) => {
                    const s = SEVERITY[rf.severity] || SEVERITY.low;
                    return (
                      <div key={i} style={{
                        background: s.bg, border: `1px solid ${s.border}`,
                        borderRadius: 8, padding: '10px 14px',
                        display: 'flex', gap: 10, alignItems: 'flex-start',
                      }}>
                        <span style={{
                          width: 8, height: 8, borderRadius: '50%', background: s.dot,
                          flexShrink: 0, marginTop: 5,
                        }} />
                        <div style={{ flex: 1 }}>
                          <span style={{
                            fontSize: 11, fontWeight: 700, textTransform: 'uppercase',
                            letterSpacing: '.04em', color: s.text, marginRight: 8,
                          }}>{rf.severity}</span>
                          <span style={{ fontSize: 13.5, color: 'var(--text-primary)', lineHeight: 1.6 }}>
                            {rf.description}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </SectionCard>

        </div>
      )}

      {/* Empty state — no summary yet */}
      {!summary && !generating && (
        <div className="empty-state" style={{ marginTop: 48 }}>
          <div className="empty-icon"><Scale size={28} /></div>
          <div style={{ fontWeight: 600, fontSize: 15 }}>No summary generated yet</div>
          <div style={{ fontSize: 13, marginTop: 6, color: 'var(--text-muted)' }}>
            Select a document above and click <strong>Generate Summary</strong>
          </div>
        </div>
      )}
    </div>
  );
}
