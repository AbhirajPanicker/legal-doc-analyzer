/**
 * Clause Analysis page — detect and risk-assess legal clauses in a document.
 */
import { useEffect, useState, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import {
  ShieldAlert, AlertTriangle, CheckCircle2, AlertCircle,
  ChevronDown, ChevronUp, FileSearch, RefreshCw, Info, Eye, EyeOff,
  FileDown, Printer, Lightbulb, Sparkles,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { listDocuments, analyseDocumentClauses, decodeJargon } from '../services/api';
import { exportClauseMarkdown, printReport } from '../services/reportExporter';

// ── Risk colours ──────────────────────────────────────────────────────────────
const RISK_STYLE = {
  high:   { bg: 'rgba(239,68,68,0.08)',  border: '#fca5a5', text: '#dc2626', dot: '#ef4444', badge: 'rgba(239,68,68,0.15)',  label: 'HIGH RISK' },
  medium: { bg: 'rgba(245,158,11,0.08)', border: '#fcd34d', text: '#d97706', dot: '#f59e0b', badge: 'rgba(245,158,11,0.15)', label: 'MEDIUM RISK' },
  low:    { bg: 'rgba(34,197,94,0.07)',  border: '#86efac', text: '#16a34a', dot: '#22c55e', badge: 'rgba(34,197,94,0.12)',  label: 'LOW RISK' },
};

const OVERALL_STYLE = {
  high:   { gradient: 'linear-gradient(135deg,#7f1d1d,#991b1b)', text: '#fca5a5', icon: '🔴', label: 'HIGH OVERALL RISK' },
  medium: { gradient: 'linear-gradient(135deg,#78350f,#92400e)', text: '#fde68a', icon: '🟡', label: 'MEDIUM OVERALL RISK' },
  low:    { gradient: 'linear-gradient(135deg,#14532d,#166534)', text: '#bbf7d0', icon: '🟢', label: 'LOW OVERALL RISK' },
};

// ── Clause Card ───────────────────────────────────────────────────────────────
function ClauseCard({ clause }) {
  const [expanded, setExpanded] = useState(false);
  const [eli5Data, setEli5Data] = useState(null);
  const [loadingEli5, setLoadingEli5] = useState(false);
  const [showEli5, setShowEli5] = useState(false);
  const rs = RISK_STYLE[clause.risk] || RISK_STYLE.low;

  const handleFetchEli5 = async (e) => {
    e.stopPropagation();
    if (eli5Data) {
      setShowEli5(prev => !prev);
      return;
    }
    setLoadingEli5(true);
    try {
      const textToDecode = clause.text_excerpt || `${clause.clause_name}: ${clause.description}`;
      const res = await decodeJargon(textToDecode);
      setEli5Data(res.data);
      setShowEli5(true);
    } catch {
      toast.error('Could not translate clause to plain English.');
    } finally {
      setLoadingEli5(false);
    }
  };

  return (
    <div style={{ border: `1px solid ${rs.border}`, borderRadius: 12, marginBottom: 12, background: rs.bg, overflow: 'hidden', opacity: clause.missing ? 0.85 : 1 }}>
      <button
        onClick={() => setExpanded(e => !e)}
        style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 12, padding: '14px 18px', background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left' }}
      >
        <span style={{ fontSize: 20, flexShrink: 0 }}>{clause.icon}</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ fontWeight: 700, fontSize: 14 }}>{clause.clause_name}</span>
            {clause.missing && (
              <span style={{ fontSize: 10, fontWeight: 700, background: 'rgba(100,116,139,0.15)', color: 'var(--text-muted)', padding: '2px 7px', borderRadius: 20, textTransform: 'uppercase', letterSpacing: '.04em' }}>NOT FOUND</span>
            )}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>{clause.description?.split('.')[0]}.</div>
        </div>
        <span style={{ flexShrink: 0, fontSize: 10.5, fontWeight: 800, letterSpacing: '.06em', background: rs.badge, color: rs.text, padding: '4px 10px', borderRadius: 20, whiteSpace: 'nowrap' }}>{rs.label}</span>
        {expanded ? <ChevronUp size={14} color="var(--text-muted)" style={{ flexShrink: 0 }} /> : <ChevronDown size={14} color="var(--text-muted)" style={{ flexShrink: 0 }} />}
      </button>

      {expanded && (
        <div style={{ padding: '0 18px 18px', borderTop: `1px solid ${rs.border}` }}>
          <div style={{ fontSize: 13.5, lineHeight: 1.7, color: 'var(--text-primary)', marginTop: 14 }}>{clause.description}</div>

          {clause.text_excerpt && (
            <div style={{ marginTop: 14, padding: '12px 14px', background: 'var(--surface-2)', borderRadius: 8, borderLeft: `4px solid ${rs.dot}` }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '.06em' }}>📄 Extracted from document</div>
              <div style={{ fontSize: 12.5, lineHeight: 1.7, color: 'var(--text-secondary)', fontStyle: 'italic' }}>"{clause.text_excerpt}"</div>
            </div>
          )}

          {/* ELI5 Trigger Button */}
          <div style={{ marginTop: 12 }}>
            <button
              onClick={handleFetchEli5}
              disabled={loadingEli5}
              style={{
                background: showEli5 ? 'rgba(59, 130, 246, 0.2)' : 'rgba(59, 130, 246, 0.08)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                borderRadius: 20,
                color: '#60a5fa',
                fontSize: 12,
                fontWeight: 600,
                padding: '5px 14px',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                cursor: 'pointer',
              }}
            >
              <Lightbulb size={13} />
              {loadingEli5 ? 'Translating to Plain English…' : showEli5 ? 'Hide Plain English (ELI5)' : '💡 Explain in Plain English (ELI5)'}
            </button>
          </div>

          {/* ELI5 Expanded Box */}
          {showEli5 && eli5Data && (
            <div style={{
              marginTop: 10,
              padding: '14px 16px',
              borderRadius: 8,
              background: 'rgba(15, 23, 42, 0.95)',
              border: '1px solid rgba(59, 130, 246, 0.35)',
            }}>
              <div style={{ fontSize: 13, color: '#e2e8f0', lineHeight: 1.6, marginBottom: 8 }}>
                <strong style={{ color: '#60a5fa' }}>🎈 In Plain English: </strong>
                {eli5Data.plain_english}
              </div>
              <div style={{ fontSize: 12.5, color: '#cbd5e1', lineHeight: 1.6, marginBottom: 8 }}>
                <strong style={{ color: '#34d399' }}>🍕 Real-Life Analogy: </strong>
                {eli5Data.real_life_analogy}
              </div>
              {!(eli5Data.category?.toLowerCase().includes('contract performance') || eli5Data.term?.toLowerCase().includes('force majeure')) && eli5Data.hidden_trap && (
                <div style={{ fontSize: 12, color: '#fca5a5', lineHeight: 1.6 }}>
                  <strong>⚠️ The Trap: </strong>
                  {eli5Data.hidden_trap}
                </div>
              )}
            </div>
          )}

          {clause.missing && (
            <div style={{ marginTop: 14, padding: '10px 14px', background: 'rgba(239,68,68,0.06)', borderRadius: 8, border: '1px solid rgba(239,68,68,0.2)', display: 'flex', alignItems: 'flex-start', gap: 8 }}>
              <AlertCircle size={14} color="#ef4444" style={{ flexShrink: 0, marginTop: 2 }} />
              <div style={{ fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                <strong style={{ color: '#dc2626' }}>Clause not found.</strong>{' '}Proceeding without this clause may expose the parties to unnecessary risk.
              </div>
            </div>
          )}

          {clause.standard_note && (
            <div style={{ marginTop: 12, padding: '10px 14px', background: 'var(--surface)', borderRadius: 8, border: '1px solid var(--border)', display: 'flex', alignItems: 'flex-start', gap: 8 }}>
              <Info size={13} color="var(--navy-400)" style={{ flexShrink: 0, marginTop: 2 }} />
              <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.65 }}>
                <strong style={{ color: 'var(--navy-400)' }}>Standard practice: </strong>{clause.standard_note}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Risk Distribution Bar ─────────────────────────────────────────────────────
function RiskBar({ high, medium, low }) {
  const total = high + medium + low || 1;
  return (
    <div style={{ marginTop: 10 }}>
      <div style={{ display: 'flex', borderRadius: 8, overflow: 'hidden', height: 10 }}>
        <div style={{ width: `${(high / total) * 100}%`, background: '#ef4444', transition: 'width .6s ease' }} />
        <div style={{ width: `${(medium / total) * 100}%`, background: '#f59e0b', transition: 'width .6s ease' }} />
        <div style={{ width: `${(low / total) * 100}%`, background: '#22c55e', transition: 'width .6s ease' }} />
      </div>
      <div style={{ display: 'flex', gap: 16, marginTop: 6 }}>
        {[{ color: '#ef4444', label: 'High', count: high }, { color: '#f59e0b', label: 'Medium', count: medium }, { color: '#22c55e', label: 'Low', count: low }].map(({ color, label, count }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 12 }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: color }} />
            <span style={{ color: 'var(--text-muted)' }}>{label}:</span>
            <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function ClauseAnalysis() {
  const location = useLocation();
  const [docs, setDocs] = useState([]);
  const [docsLoading, setDocsLoading] = useState(true);
  const [selectedDocId, setSelectedDocId] = useState(location.state?.docId || '');
  const [analysis, setAnalysis] = useState(null);
  const [analysing, setAnalysing] = useState(false);
  const [showMissing, setShowMissing] = useState(true);
  const [filterRisk, setFilterRisk] = useState('all');

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

  const handleAnalyse = useCallback(async () => {
    if (!selectedDocId) return;
    setAnalysis(null);
    setAnalysing(true);
    try {
      const r = await analyseDocumentClauses(selectedDocId);
      setAnalysis(r.data);
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Clause analysis failed.');
    } finally {
      setAnalysing(false);
    }
  }, [selectedDocId]);

  const selectedDoc = docs.find(d => d.id === selectedDocId);
  const detectedFiltered = analysis
    ? (filterRisk === 'all' ? analysis.detected_clauses : analysis.detected_clauses.filter(c => c.risk === filterRisk))
    : [];
  const missingFiltered = analysis
    ? (filterRisk === 'all' ? analysis.missing_clauses : analysis.missing_clauses.filter(c => c.risk === filterRisk))
    : [];
  const overallStyle = analysis ? (OVERALL_STYLE[analysis.overall_risk] || OVERALL_STYLE.low) : null;

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '28px 32px' }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, margin: '0 0 4px', display: 'flex', alignItems: 'center', gap: 10 }}>
          <ShieldAlert size={22} color="var(--navy-400)" /> Clause & Risk Analysis
        </h1>
        <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: 13.5 }}>
          Automatically detect legal clauses, identify missing protections, and assess contract risk.
        </p>
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', marginBottom: 28, background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 14, padding: '20px 22px', boxShadow: 'var(--shadow-sm)' }}>
        <div style={{ flex: 1 }}>
          <label htmlFor="clause-doc-select" style={{ display: 'block', fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '.06em' }}>Select Document</label>
          {docsLoading ? (
            <div style={{ height: 40, background: 'var(--surface-2)', borderRadius: 8 }} />
          ) : (
            <select
              id="clause-doc-select"
              value={selectedDocId}
              onChange={e => { setSelectedDocId(e.target.value); setAnalysis(null); }}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--surface-2)', color: 'var(--text-primary)', fontSize: 13.5, cursor: 'pointer', outline: 'none' }}
            >
              <option value="">— Choose a document —</option>
              {docs.map(d => <option key={d.id} value={d.id}>{d.original_name}</option>)}
            </select>
          )}
        </div>
        <button
          id="analyse-clauses-btn"
          className="btn btn-primary"
          onClick={handleAnalyse}
          disabled={!selectedDocId || analysing}
          style={{ height: 46, paddingLeft: 22, paddingRight: 22, gap: 8 }}
        >
          {analysing ? <><RefreshCw size={15} className="animate-spin-slow" /> Analysing…</> : <><FileSearch size={15} /> Analyse Clauses</>}
        </button>
      </div>

      {/* Loading */}
      {analysing && (
        <div style={{ textAlign: 'center', padding: '48px 0' }}>
          <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'var(--surface)', border: '3px solid var(--navy-400)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
            <ShieldAlert size={22} color="var(--navy-400)" />
          </div>
          <div style={{ fontSize: 15, fontWeight: 700 }}>Analysing contract clauses…</div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 6 }}>Detecting clauses, assessing risk, and checking for missing protections.</div>
        </div>
      )}

      {/* Empty state */}
      {!analysis && !analysing && (
        <div className="empty-state" style={{ padding: '48px 0' }}>
          <div className="empty-icon" style={{ width: 72, height: 72, margin: '0 auto 18px' }}><ShieldAlert size={30} /></div>
          <div style={{ fontWeight: 700, fontSize: 16 }}>Select a document to begin</div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 6, maxWidth: 360, lineHeight: 1.6 }}>
            Choose an indexed legal document and click "Analyse Clauses" to detect clause types, flag risks, and identify missing protections.
          </div>
        </div>
      )}

      {/* Results */}
      {analysis && !analysing && (
        <div style={{ animation: 'fadeInUp .35s ease both' }}>

          {/* Printable header */}
          <div className="print-only-header">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ margin: '0 0 4px', fontSize: 20 }}>LexAnalyzer — Legal Clause & Risk Audit</h2>
                <div style={{ fontSize: 13, color: '#4b5563' }}>Document: <strong>{selectedDoc?.original_name}</strong></div>
              </div>
              <div style={{ textAlign: 'right', fontSize: 12, color: '#6b7280' }}>
                <div>Date: {new Date().toLocaleDateString()}</div>
                <div>Assessment: <strong>{(analysis.overall_risk || 'low').toUpperCase()} RISK</strong></div>
              </div>
            </div>
          </div>

          {/* Export Action Bar */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 10 }} className="no-print">
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              Audit completed • <strong>{analysis.total_clauses_found}</strong> clauses detected, <strong>{analysis.total_clauses_missing}</strong> standard protections evaluated
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button
                id="clause-export-md-btn"
                className="btn btn-secondary btn-sm"
                onClick={() => {
                  exportClauseMarkdown(selectedDoc?.original_name, analysis);
                  toast.success('Clause audit exported as Markdown!');
                }}
                title="Download Markdown Report"
                style={{ gap: 6, fontSize: 12.5 }}
              >
                <FileDown size={14} /> Export .MD
              </button>
              <button
                id="clause-export-pdf-btn"
                className="btn btn-primary btn-sm"
                onClick={() => printReport(`Clause_Audit_${selectedDoc?.original_name || 'Report'}`)}
                title="Print or Save as PDF"
                style={{ gap: 6, fontSize: 12.5 }}
              >
                <Printer size={14} /> Save PDF / Print
              </button>
            </div>
          </div>

          {/* Overall risk banner */}
          <div style={{ background: overallStyle.gradient, borderRadius: 16, padding: '24px 28px', marginBottom: 24, display: 'flex', gap: 20, alignItems: 'center' }}>
            <div style={{ fontSize: 40, flexShrink: 0 }}>{overallStyle.icon}</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 11, fontWeight: 800, letterSpacing: '.1em', color: `${overallStyle.text}99`, textTransform: 'uppercase', marginBottom: 4 }}>
                Overall Assessment — {selectedDoc?.original_name}
              </div>
              <div style={{ fontSize: 22, fontWeight: 900, color: overallStyle.text }}>{overallStyle.label}</div>
              <div style={{ fontSize: 13, color: `${overallStyle.text}bb`, marginTop: 4, lineHeight: 1.6 }}>{analysis.analysis_note}</div>
            </div>
            <div style={{ textAlign: 'center', flexShrink: 0 }}>
              <div style={{ fontSize: 36, fontWeight: 900, color: overallStyle.text }}>{analysis.total_clauses_found}</div>
              <div style={{ fontSize: 11, color: `${overallStyle.text}aa`, fontWeight: 600 }}>found</div>
              <div style={{ fontSize: 28, fontWeight: 900, color: '#ef4444', marginTop: 4 }}>{analysis.total_clauses_missing}</div>
              <div style={{ fontSize: 11, color: '#fca5a5', fontWeight: 600 }}>missing</div>
            </div>
          </div>

          {/* Risk bar */}
          <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 14, padding: '18px 22px', marginBottom: 24 }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 8 }}>Risk Distribution</div>
            <RiskBar high={analysis.high_risk_count} medium={analysis.medium_risk_count} low={analysis.low_risk_count} />
            {!analysis.llm_used && (
              <div style={{ marginTop: 12, padding: '8px 12px', background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8, display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                <Info size={13} color="#818cf8" style={{ flexShrink: 0, marginTop: 1 }} />
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{analysis.analysis_note}</span>
              </div>
            )}
          </div>

          {/* Filter row */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '.06em' }}>Filter:</span>
            {['all', 'high', 'medium', 'low'].map(r => (
              <button key={r} onClick={() => setFilterRisk(r)} style={{ padding: '5px 14px', borderRadius: 20, border: '1px solid', fontSize: 12, fontWeight: 700, cursor: 'pointer', textTransform: 'capitalize', borderColor: filterRisk === r ? (RISK_STYLE[r]?.dot || 'var(--navy-400)') : 'var(--border)', background: filterRisk === r ? (RISK_STYLE[r]?.badge || 'var(--surface-2)') : 'transparent', color: filterRisk === r ? (RISK_STYLE[r]?.text || 'var(--navy-400)') : 'var(--text-muted)' }}>
                {r === 'all' ? 'All' : `${r} (${r === 'high' ? analysis.high_risk_count : r === 'medium' ? analysis.medium_risk_count : analysis.low_risk_count})`}
              </button>
            ))}
            <div style={{ flex: 1 }} />
            <button onClick={() => setShowMissing(s => !s)} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '5px 14px', borderRadius: 20, border: '1px solid var(--border)', fontSize: 12, fontWeight: 700, cursor: 'pointer', background: showMissing ? 'rgba(239,68,68,0.1)' : 'transparent', color: showMissing ? '#dc2626' : 'var(--text-muted)' }}>
              {showMissing ? <Eye size={13} /> : <EyeOff size={13} />}{showMissing ? 'Hide' : 'Show'} Missing ({filterRisk === 'all' ? analysis.total_clauses_missing : missingFiltered.length})
            </button>
          </div>

          {/* Detected */}
          {detectedFiltered.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontSize: 13, fontWeight: 800, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                <CheckCircle2 size={15} color="#22c55e" /> Detected Clauses ({detectedFiltered.length})
              </div>
              {detectedFiltered.map(c => <ClauseCard key={c.clause_id} clause={c} />)}
            </div>
          )}

          {/* Missing */}
          {showMissing && missingFiltered.length > 0 && (
            <div>
              <div style={{ fontSize: 13, fontWeight: 800, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                <AlertTriangle size={15} color="#ef4444" /> Missing Clauses — Protections Not Found ({missingFiltered.length})
              </div>
              {missingFiltered.map(c => <ClauseCard key={c.clause_id} clause={c} />)}
            </div>
          )}

          {detectedFiltered.length === 0 && (!showMissing || missingFiltered.length === 0) && (
            <div className="empty-state" style={{ padding: '32px 0' }}>
              <div style={{ fontSize: 14, color: 'var(--text-muted)' }}>
                {filterRisk === 'all' ? 'No clauses or missing protections to display.' : `No ${filterRisk}-risk clauses found.`}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

