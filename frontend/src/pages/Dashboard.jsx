/**
 * Dashboard page — overview stats and quick-start guide.
 */
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText, CheckCircle2, AlertCircle, MessageSquare,
  ArrowRight, TrendingUp, Info, ShieldAlert, Sparkles, Zap, ScanText, ScanEye,
} from 'lucide-react';
import { listDocuments } from '../services/api';

function StatCard({ icon: Icon, iconBg, value, label, change }) {
  return (
    <div className="stat-card animate-fade-in-up">
      <div className="stat-icon" style={{ background: iconBg }}>
        <Icon size={20} color="#fff" />
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      {change !== undefined && (
        <div className="stat-change" style={{ color: 'var(--text-muted)' }}>
          <TrendingUp size={12} /> {change}
        </div>
      )}
    </div>
  );
}



export default function Dashboard() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    listDocuments()
      .then(r => setDocs(r.data.documents))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const ready = docs.filter(d => d.status === 'ready').length;
  const errors = docs.filter(d => d.status === 'error').length;

  return (
    <div className="page-content">
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}
          className="font-display">
          Legal Document Analyzer
        </h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 6 }}>
          RAG-powered AI assistant for understanding legal documents
        </p>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 28 }}>
        <StatCard
          icon={FileText}
          iconBg="linear-gradient(135deg, var(--navy-700), var(--navy-500))"
          value={loading ? '—' : docs.length}
          label="Total Documents"
        />
        <StatCard
          icon={CheckCircle2}
          iconBg="linear-gradient(135deg, #16a34a, #22c55e)"
          value={loading ? '—' : ready}
          label="Ready for Q&A"
        />
        <StatCard
          icon={AlertCircle}
          iconBg="linear-gradient(135deg, #dc2626, #f87171)"
          value={loading ? '—' : errors}
          label="Processing Errors"
        />
        <StatCard
          icon={MessageSquare}
          iconBg="linear-gradient(135deg, var(--gold-500), var(--gold-300))"
          value="RAG"
          label="Retrieval Method"
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20 }}>
        {/* Document Intelligence Showcase */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="card-header">
            <span className="card-title">Document Intelligence</span>
          </div>
          <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{
              borderRadius: 12,
              overflow: 'hidden',
              position: 'relative',
              border: '1px solid var(--border)',
              boxShadow: '0 4px 16px rgba(0,0,0,0.12)',
              maxHeight: 200,
            }}>
              <img
                src="/legal_analysis.jpg"
                alt="AI Legal Document Analysis"
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  display: 'block',
                }}
              />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 14.5, marginBottom: 4, color: 'var(--text-primary)' }}>
                AI-Powered Contract & PDF Analysis
              </div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                Upload agreements or legal documents to extract key clauses, identify missing protections, evaluate liabilities, and chat directly with your files.
              </div>
            </div>
            <button
              className="btn btn-primary"
              style={{ alignSelf: 'flex-start', marginTop: 2 }}
              onClick={() => navigate('/documents')}
            >
              Upload a Document <ArrowRight size={15} />
            </button>
          </div>
        </div>

        {/* Quick actions */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Quick Actions</span>
          </div>
          <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {[
              {
                icon: ScanEye,
                color: '#6366f1',
                bg: 'rgba(99,102,241,0.1)',
                title: 'Contract Blind-Spot Detector',
                desc: 'Uncover missing terms, ambiguous language, and unanswered questions.',
                route: '/blind-spots',
              },
              {
                icon: ShieldAlert,
                color: '#ef4444',
                bg: 'rgba(239,68,68,0.1)',
                title: 'Clause & Risk Analysis',
                desc: 'Detect legal clauses, flag missing protections, and get a risk score.',
                route: '/clauses',
              },
              {
                icon: Sparkles,
                color: 'var(--gold-400)',
                bg: 'rgba(251,191,36,0.1)',
                title: 'Executive Summary',
                desc: 'One-click structured briefing: parties, dates, obligations, financial terms.',
                route: '/summarise',
              },
              {
                icon: MessageSquare,
                color: 'var(--navy-400)',
                bg: 'rgba(99,102,241,0.1)',
                title: 'Document Chat (with History)',
                desc: 'Ask questions — conversations are now saved across sessions.',
                route: '/chat',
              },
            ].map(({ icon: Icon, color, bg, title, desc, route }) => (
              <button
                key={route}
                onClick={() => navigate(route)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: '12px 14px', borderRadius: 10,
                  border: '1px solid var(--border)', background: 'var(--surface-2)',
                  cursor: 'pointer', textAlign: 'left',
                  transition: 'background .15s, transform .15s',
                }}
                onMouseEnter={e => { e.currentTarget.style.background = bg; e.currentTarget.style.transform = 'translateX(3px)'; }}
                onMouseLeave={e => { e.currentTarget.style.background = 'var(--surface-2)'; e.currentTarget.style.transform = 'none'; }}
              >
                <div style={{ width: 36, height: 36, borderRadius: 8, background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Icon size={18} color={color} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 700, fontSize: 13 }}>{title}</div>
                  <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 2 }}>{desc}</div>
                </div>
                <ArrowRight size={14} color="var(--text-muted)" style={{ flexShrink: 0 }} />
              </button>
            ))}
          </div>
        </div>

        {/* Recent documents */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Recent Documents</span>
            <button className="btn btn-secondary btn-sm" onClick={() => navigate('/documents')}>
              View All
            </button>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            {loading && (
              <div style={{ padding: 24, textAlign: 'center' }}>
                <div className="spinner" style={{ margin: '0 auto' }} />
              </div>
            )}
            {!loading && docs.length === 0 && (
              <div className="empty-state" style={{ padding: '28px 24px' }}>
                <div className="empty-icon" style={{ width: 48, height: 48, margin: '0 auto 12px' }}>
                  <FileText size={22} />
                </div>
                <div style={{ fontSize: 13, fontWeight: 600 }}>No documents yet</div>
                <div style={{ fontSize: 12, marginTop: 4 }}>Upload your first legal PDF to get started</div>
              </div>
            )}
            {!loading && docs.slice(0, 5).map(doc => (
              <div key={doc.id}
                className="doc-row"
                style={{ borderRadius: 0, borderBottom: '1px solid var(--border)' }}
                onClick={() => navigate('/chat', { state: { docId: doc.id } })}
                role="button" tabIndex={0}
              >
                <div className="doc-row-icon"><FileText size={16} /></div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="doc-row-name" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: 13 }}>
                    {doc.original_name}
                  </div>
                  <div className="doc-row-meta">{doc.page_count} pages</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  {doc.ocr_applied && (
                    <span
                      className="badge"
                      style={{
                        background: 'rgba(59, 130, 246, 0.15)',
                        color: '#60a5fa',
                        border: '1px solid rgba(59, 130, 246, 0.3)',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 3,
                        padding: '1px 6px',
                        fontSize: 10,
                        fontWeight: 600,
                      }}
                      title="Processed via OCR"
                    >
                      <ScanText size={10} /> OCR
                    </span>
                  )}
                  <span className={`badge badge-${doc.status === 'ready' ? 'ready' : doc.status === 'error' ? 'error' : 'processing'}`} style={{ fontSize: 10.5 }}>
                    {doc.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="alert alert-info" style={{ marginTop: 24 }}>
        <Info size={15} style={{ flexShrink: 0, marginTop: 1 }} />
        <span>
          <strong>Legal AI Assistant.</strong> Grounded semantic search, clause detection, and risk analysis.
          This tool is intended for informational purposes only. Not a substitute for formal legal counsel.
        </span>
      </div>
    </div>
  );
}
