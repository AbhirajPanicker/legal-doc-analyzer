/**
 * Contract Blind-Spot Detector Page
 * Identifies potential missing terms, ambiguous language, undefined terms,
 * uncompleted attachments, and unanswered questions requiring human legal review.
 */
import { useEffect, useState, useCallback, useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  ScanEye, AlertTriangle, AlertCircle, CheckCircle2,
  FileSearch, RefreshCw, FileDown, Printer,
  HelpCircle, Search, Filter, Sparkles, BookOpen, ChevronRight, FileText,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { listDocuments, detectBlindSpots } from '../services/api';
import { exportBlindSpotMarkdown, printReport } from '../services/reportExporter';

// ── Category badge color mappings ─────────────────────────────────────────────
const CATEGORY_STYLES = {
  'Potential Gap': {
    badgeBg: 'rgba(147, 51, 234, 0.12)',
    badgeText: '#9333ea',
    border: 'rgba(147, 51, 234, 0.3)',
    icon: '🛡️',
  },
  'Ambiguity': {
    badgeBg: 'rgba(245, 158, 11, 0.12)',
    badgeText: '#d97706',
    border: 'rgba(245, 158, 11, 0.3)',
    icon: '🔍',
  },
  'Missing Reference': {
    badgeBg: 'rgba(239, 68, 68, 0.12)',
    badgeText: '#dc2626',
    border: 'rgba(239, 68, 68, 0.3)',
    icon: '📎',
  },
  'Needs Human Review': {
    badgeBg: 'rgba(59, 130, 246, 0.12)',
    badgeText: '#2563eb',
    border: 'rgba(59, 130, 246, 0.3)',
    icon: '⚖️',
  },
};

const SEVERITY_STYLES = {
  High: {
    bg: 'rgba(239, 68, 68, 0.08)',
    badgeBg: 'rgba(239, 68, 68, 0.18)',
    text: '#dc2626',
    border: '#fca5a5',
    label: 'HIGH SEVERITY',
  },
  Medium: {
    bg: 'rgba(245, 158, 11, 0.08)',
    badgeBg: 'rgba(245, 158, 11, 0.18)',
    text: '#d97706',
    border: '#fcd34d',
    label: 'MEDIUM SEVERITY',
  },
  Low: {
    bg: 'rgba(34, 197, 94, 0.07)',
    badgeBg: 'rgba(34, 197, 94, 0.15)',
    text: '#16a34a',
    border: '#86efac',
    label: 'LOW SEVERITY',
  },
};

export default function BlindSpots() {
  const [docs, setDocs] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const location = useLocation();
  const navigate = useNavigate();

  // Load documents
  useEffect(() => {
    listDocuments()
      .then(res => {
        const readyDocs = (res.data.documents || []).filter(d => d.status === 'ready');
        setDocs(readyDocs);

        // Pre-select from route state or URL search param
        const queryParams = new URLSearchParams(location.search);
        const urlDocId = queryParams.get('docId') || location.state?.docId;

        if (urlDocId && readyDocs.some(d => d.id === urlDocId)) {
          setSelectedDocId(urlDocId);
        } else if (readyDocs.length > 0) {
          setSelectedDocId(readyDocs[0].id);
        }
      })
      .catch(() => toast.error('Failed to load document list.'));
  }, [location.search, location.state]);

  // Run analysis when selected document changes
  const runDetection = useCallback((docId) => {
    if (!docId) return;
    setLoading(true);
    setAnalysis(null);

    detectBlindSpots(docId)
      .then(res => {
        setAnalysis(res.data);
      })
      .catch(err => {
        const msg = err.response?.data?.detail || err.message || 'Blind-spot analysis failed.';
        toast.error(msg);
      })
      .finally(() => setLoading(false));
  }, []);

  // Note: No auto-trigger on mount; waits for user to click 'Audit Agreement'
  const selectedDoc = docs.find(d => d.id === selectedDocId);

  // Filter findings
  const filteredFindings = useMemo(() => {
    if (!analysis?.findings) return [];
    return analysis.findings.filter(f => {
      // Category filter
      if (activeCategory !== 'ALL' && f.category !== activeCategory) return false;
      // Severity filter
      if (severityFilter !== 'ALL' && f.severity !== severityFilter) return false;
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesTitle = f.title?.toLowerCase().includes(q);
        const matchesExpl = f.explanation?.toLowerCase().includes(q);
        const matchesEvid = f.evidence?.toLowerCase().includes(q);
        const matchesQues = f.human_review_question?.toLowerCase().includes(q);
        const matchesType = f.gap_type?.toLowerCase().includes(q);
        return matchesTitle || matchesExpl || matchesEvid || matchesQues || matchesType;
      }
      return true;
    });
  }, [analysis, activeCategory, severityFilter, searchQuery]);

  return (
    <div className="page-content">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, marginBottom: 24 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: 'linear-gradient(135deg, #4f46e5, #06b6d4)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(79, 70, 229, 0.25)',
            }}>
              <ScanEye size={20} color="#fff" />
            </div>
            <h1 style={{ fontSize: 24, fontWeight: 800, margin: 0, color: 'var(--text-primary)' }} className="font-display">
              Contract Blind-Spot Detector
            </h1>
          </div>
          <p style={{ fontSize: 13.5, color: 'var(--text-muted)', margin: '6px 0 0' }}>
            Uncover potential missing clauses, ambiguous drafting, unattached exhibits, and unanswered assumptions requiring human legal counsel review.
          </p>
        </div>

        {/* Action Buttons */}
        {analysis && (
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <button
              className="btn btn-secondary"
              onClick={() => exportBlindSpotMarkdown(selectedDoc?.original_name, analysis)}
              style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12.5 }}
            >
              <FileDown size={14} /> Export Audit (.md)
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => printReport()}
              style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12.5 }}
            >
              <Printer size={14} /> Print Report
            </button>
          </div>
        )}
      </div>

      {/* Document Selector Card */}
      <div className="card" style={{ marginBottom: 22, padding: '16px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flex: 1, minWidth: 260 }}>
            <FileText size={18} color="var(--navy-600)" />
            <div style={{ flex: 1 }}>
              <label htmlFor="blind-spot-doc-select" style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '.06em', display: 'block', marginBottom: 4 }}>
                Target Agreement for Audit
              </label>
              {docs.length === 0 ? (
                <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>No ready documents found. Please upload a PDF first.</span>
              ) : (
                <select
                  id="blind-spot-doc-select"
                  className="form-control"
                  value={selectedDocId}
                  onChange={e => {
                    setSelectedDocId(e.target.value);
                    setAnalysis(null);
                  }}
                  style={{ width: '100%', maxWidth: 440, fontSize: 13.5, fontWeight: 600, padding: '6px 12px' }}
                >
                  {docs.map(d => (
                    <option key={d.id} value={d.id}>
                      {d.original_name} ({d.page_count} {d.page_count === 1 ? 'page' : 'pages'})
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>

          <button
            className="btn btn-primary"
            onClick={() => runDetection(selectedDocId)}
            disabled={loading || !selectedDocId}
            style={{ display: 'flex', alignItems: 'center', gap: 6 }}
          >
            {loading ? <RefreshCw size={14} className="animate-spin" /> : <ScanEye size={14} />}
            {loading ? 'Auditing Agreement...' : (analysis ? 'Re-Audit Agreement' : 'Audit Agreement')}
          </button>
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="card" style={{ padding: '60px 24px', textAlign: 'center', marginBottom: 24 }}>
          <div style={{
            width: 56, height: 56, borderRadius: '50%', margin: '0 auto 16px',
            background: 'rgba(79, 70, 229, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <RefreshCw size={26} color="var(--navy-600)" className="animate-spin" />
          </div>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 6px', color: 'var(--text-primary)' }}>
            Auditing Document for Contract Blind Spots...
          </h3>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 500, margin: '0 auto' }}>
            Evaluating ambiguous standards of care, missing default remedies, unfulfilled placeholders, and unanswered assumptions across all pages.
          </p>
        </div>
      )}

      {/* Ready to audit / Not started state */}
      {!loading && !analysis && (
        <div className="card" style={{ padding: '56px 24px', textAlign: 'center', marginBottom: 24 }}>
          <div style={{
            width: 60, height: 60, borderRadius: 16, margin: '0 auto 16px',
            background: 'linear-gradient(135deg, rgba(79, 70, 229, 0.12), rgba(6, 182, 212, 0.12))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 16px rgba(79, 70, 229, 0.12)',
          }}>
            <ScanEye size={28} color="var(--navy-600)" />
          </div>
          <h3 style={{ fontSize: 17, fontWeight: 700, margin: '0 0 8px', color: 'var(--text-primary)' }}>
            Ready to Audit Agreement
          </h3>
          <p style={{ fontSize: 13.5, color: 'var(--text-muted)', maxWidth: 480, margin: '0 auto 20px', lineHeight: 1.6 }}>
            Select an agreement above and click <strong>"Audit Agreement"</strong> to detect potential missing clauses, vague standards, unattached exhibits, and unaddressed assumptions.
          </p>
          <button
            className="btn btn-primary"
            disabled={!selectedDocId}
            onClick={() => runDetection(selectedDocId)}
            style={{ padding: '9px 20px', fontSize: 13.5, display: 'inline-flex', alignItems: 'center', gap: 8 }}
          >
            <ScanEye size={15} /> Audit Agreement
          </button>
        </div>
      )}

      {/* Analysis Content */}
      {!loading && analysis && (
        <>
          {/* Executive Takeaway Hero Card */}
          <div className="card" style={{
            marginBottom: 24,
            background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95))',
            color: '#fff',
            border: '1px solid rgba(255,255,255,0.1)',
            boxShadow: '0 12px 32px rgba(0,0,0,0.25)',
          }}>
            <div className="card-body" style={{ padding: '26px 28px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 14 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Sparkles size={18} color="var(--gold-400)" />
                  <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--gold-400)' }}>
                    Executive Audit Overview
                  </span>
                </div>
                <div style={{ fontSize: 11.5, color: 'rgba(255,255,255,0.6)', display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span>Engine:</span>
                  <span style={{
                    background: analysis.llm_used ? 'rgba(34,197,94,0.2)' : 'rgba(245,158,11,0.2)',
                    color: analysis.llm_used ? '#86efac' : '#fde68a',
                    padding: '2px 8px', borderRadius: 12, fontWeight: 700, fontSize: 11,
                  }}>
                    {analysis.llm_used ? 'AI Deep Analysis' : 'Deterministic Heuristic Mode'}
                  </span>
                </div>
              </div>

              <div style={{ fontSize: 15, lineHeight: 1.65, fontWeight: 500, color: 'rgba(255,255,255,0.92)', marginBottom: 22 }}>
                {analysis.executive_takeaway}
              </div>

              {/* Stats Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 14 }}>
                <div style={{ background: 'rgba(255,255,255,0.06)', borderRadius: 10, padding: '12px 16px', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '.04em' }}>Total Findings</div>
                  <div style={{ fontSize: 24, fontWeight: 800, marginTop: 4, color: '#fff' }}>{analysis.total_findings}</div>
                </div>
                <div style={{ background: 'rgba(239,68,68,0.12)', borderRadius: 10, padding: '12px 16px', border: '1px solid rgba(239,68,68,0.25)' }}>
                  <div style={{ fontSize: 11, color: '#fca5a5', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '.04em' }}>🔴 High Severity</div>
                  <div style={{ fontSize: 24, fontWeight: 800, marginTop: 4, color: '#fca5a5' }}>{analysis.high_severity_count}</div>
                </div>
                <div style={{ background: 'rgba(245,158,11,0.12)', borderRadius: 10, padding: '12px 16px', border: '1px solid rgba(245,158,11,0.25)' }}>
                  <div style={{ fontSize: 11, color: '#fde68a', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '.04em' }}>🟡 Medium</div>
                  <div style={{ fontSize: 24, fontWeight: 800, marginTop: 4, color: '#fde68a' }}>{analysis.medium_severity_count}</div>
                </div>
                <div style={{ background: 'rgba(34,197,94,0.12)', borderRadius: 10, padding: '12px 16px', border: '1px solid rgba(34,197,94,0.25)' }}>
                  <div style={{ fontSize: 11, color: '#bbf7d0', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '.04em' }}>🟢 Low</div>
                  <div style={{ fontSize: 24, fontWeight: 800, marginTop: 4, color: '#bbf7d0' }}>{analysis.low_severity_count}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Filters & Tabs */}
          <div className="card" style={{ marginBottom: 20, padding: '14px 18px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {/* Category tabs */}
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', borderBottom: '1px solid var(--border)', paddingBottom: 12 }}>
                {[
                  { id: 'ALL', label: 'All Categories', count: analysis.total_findings },
                  { id: 'Potential Gap', label: 'Potential Gap', count: analysis.categories_summary?.['Potential Gap'] || 0 },
                  { id: 'Ambiguity', label: 'Ambiguity', count: analysis.categories_summary?.['Ambiguity'] || 0 },
                  { id: 'Missing Reference', label: 'Missing Reference', count: analysis.categories_summary?.['Missing Reference'] || 0 },
                  { id: 'Needs Human Review', label: 'Needs Human Review', count: analysis.categories_summary?.['Needs Human Review'] || 0 },
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveCategory(tab.id)}
                    style={{
                      padding: '6px 14px',
                      borderRadius: 20,
                      fontSize: 12.5,
                      fontWeight: 700,
                      cursor: 'pointer',
                      border: 'none',
                      transition: 'all .15s ease',
                      background: activeCategory === tab.id ? 'var(--navy-800)' : 'var(--surface-2)',
                      color: activeCategory === tab.id ? '#fff' : 'var(--text-secondary)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                    }}
                  >
                    <span>{tab.label}</span>
                    <span style={{
                      background: activeCategory === tab.id ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.08)',
                      padding: '1px 6px',
                      borderRadius: 10,
                      fontSize: 11,
                    }}>
                      {tab.count}
                    </span>
                  </button>
                ))}
              </div>

              {/* Search & Severity bar */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 220 }}>
                  <Search size={15} color="var(--text-muted)" />
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Search findings, clauses, or review questions..."
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    style={{ fontSize: 13, padding: '6px 10px', width: '100%' }}
                  />
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Filter size={14} color="var(--text-muted)" />
                  <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)' }}>Severity:</span>
                  {['ALL', 'High', 'Medium', 'Low'].map(sev => (
                    <button
                      key={sev}
                      onClick={() => setSeverityFilter(sev)}
                      style={{
                        padding: '4px 10px',
                        borderRadius: 6,
                        fontSize: 11.5,
                        fontWeight: 700,
                        border: '1px solid var(--border)',
                        cursor: 'pointer',
                        background: severityFilter === sev ? 'var(--navy-700)' : 'transparent',
                        color: severityFilter === sev ? '#fff' : 'var(--text-secondary)',
                      }}
                    >
                      {sev}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Zero findings state */}
          {filteredFindings.length === 0 && (
            <div className="card" style={{ padding: '48px 24px', textAlign: 'center', marginBottom: 24 }}>
              <div style={{
                width: 48, height: 48, borderRadius: '50%', margin: '0 auto 14px',
                background: 'rgba(34, 197, 94, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <CheckCircle2 size={24} color="#16a34a" />
              </div>
              <h3 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 6px', color: 'var(--text-primary)' }}>
                {analysis.total_findings === 0
                  ? 'No Contract Blind Spots Detected'
                  : 'No Findings Match the Selected Filter'}
              </h3>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 460, margin: '0 auto' }}>
                {analysis.total_findings === 0
                  ? 'No material omissions, ambiguous care standards, or missing exhibit references were detected in this agreement.'
                  : 'Try selecting "All Categories" or clearing the search query to view other observations.'}
              </p>
            </div>
          )}

          {/* Finding Cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 28 }}>
            {filteredFindings.map((finding, idx) => {
              const catStyle = CATEGORY_STYLES[finding.category] || CATEGORY_STYLES['Potential Gap'];
              const sevStyle = SEVERITY_STYLES[finding.severity] || SEVERITY_STYLES.Medium;

              return (
                <div
                  key={finding.id || idx}
                  className="card"
                  style={{
                    border: `1px solid var(--border)`,
                    borderLeft: `5px solid ${sevStyle.text}`,
                    boxShadow: '0 2px 10px rgba(0,0,0,0.04)',
                    overflow: 'hidden',
                  }}
                >
                  <div className="card-body" style={{ padding: '20px 22px' }}>
                    {/* Top metadata row */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8, marginBottom: 10 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                        {/* Category Badge */}
                        <span style={{
                          background: catStyle.badgeBg,
                          color: catStyle.badgeText,
                          fontSize: 11,
                          fontWeight: 800,
                          padding: '3px 9px',
                          borderRadius: 20,
                          display: 'flex',
                          alignItems: 'center',
                          gap: 4,
                          letterSpacing: '.03em',
                        }}>
                          <span>{catStyle.icon}</span>
                          {finding.category}
                        </span>

                        {/* Gap Type Tag */}
                        <span style={{
                          background: 'var(--surface-2)',
                          color: 'var(--text-secondary)',
                          fontSize: 11,
                          fontWeight: 700,
                          padding: '3px 9px',
                          borderRadius: 6,
                          border: '1px solid var(--border)',
                        }}>
                          {finding.gap_type}
                        </span>

                        {/* Page Pill */}
                        <span style={{
                          fontSize: 11,
                          fontWeight: 700,
                          color: 'var(--text-muted)',
                          background: 'var(--surface-2)',
                          padding: '3px 8px',
                          borderRadius: 6,
                        }}>
                          {finding.page_number ? `📄 Page ${finding.page_number}` : '🌐 Agreement-Wide'}
                        </span>
                      </div>

                      {/* Severity Pill */}
                      <span style={{
                        background: sevStyle.badgeBg,
                        color: sevStyle.text,
                        fontSize: 10.5,
                        fontWeight: 800,
                        padding: '3px 10px',
                        borderRadius: 20,
                        letterSpacing: '.05em',
                      }}>
                        {sevStyle.label}
                      </span>
                    </div>

                    {/* Title */}
                    <h3 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 8px', color: 'var(--text-primary)' }}>
                      {finding.title}
                    </h3>

                    {/* Explanation */}
                    <p style={{ fontSize: 13.5, lineHeight: 1.65, color: 'var(--text-secondary)', margin: '0 0 14px' }}>
                      {finding.explanation}
                    </p>

                    {/* Evidence Box */}
                    {finding.evidence && (
                      <div style={{
                        background: 'var(--surface-2)',
                        borderRadius: 8,
                        padding: '12px 16px',
                        borderLeft: `3px solid var(--navy-500)`,
                        marginBottom: 14,
                      }}>
                        <div style={{ fontSize: 11, fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 4 }}>
                          Supporting Evidence / Clause Language
                        </div>
                        <div style={{ fontSize: 13, fontStyle: 'italic', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                          "{finding.evidence}"
                        </div>
                      </div>
                    )}

                    {/* Human Review Question Callout */}
                    <div style={{
                      background: 'rgba(79, 70, 229, 0.05)',
                      border: '1px solid rgba(79, 70, 229, 0.2)',
                      borderRadius: 10,
                      padding: '12px 16px',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 12,
                    }}>
                      <HelpCircle size={18} color="var(--navy-600)" style={{ flexShrink: 0, marginTop: 2 }} />
                      <div>
                        <div style={{ fontSize: 11.5, fontWeight: 800, color: 'var(--navy-600)', textTransform: 'uppercase', letterSpacing: '.05em', marginBottom: 2 }}>
                          Question for Legal Counsel Review
                        </div>
                        <div style={{ fontSize: 13.5, fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.5 }}>
                          {finding.human_review_question}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Legal Disclaimer Footer */}
          <div className="alert alert-info" style={{ marginTop: 20 }}>
            <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 2 }} />
            <span style={{ fontSize: 12.5, lineHeight: 1.6 }}>
              <strong>Preliminary Observation Notice:</strong> {analysis.disclaimer}
            </span>
          </div>
        </>
      )}
    </div>
  );
}
