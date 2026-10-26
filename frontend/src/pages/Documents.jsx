/**
 * Documents page — upload, list, view details, and delete documents.
 */
import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText, RefreshCw, MessageSquare, X, ChevronRight,
  FileSearch, Calendar, HardDrive, Hash, ShieldAlert, Sparkles, ScanText, ScanEye,
} from 'lucide-react';
import toast from 'react-hot-toast';
import UploadZone from '../components/UploadZone';
import DocumentCard from '../components/DocumentCard';
import { listDocuments, getDocument, deleteDocument } from '../services/api';

function DetailPanel({ doc, onClose, onDelete, onChat, onSummarise, onClauses, onBlindSpots }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getDocument(doc.id)
      .then(r => setDetail(r.data))
      .catch(() => setDetail(doc))
      .finally(() => setLoading(false));
  }, [doc.id]);

  const d = detail || doc;

  return (
    <div style={{
      width: 340, flexShrink: 0, borderLeft: '1px solid var(--border)',
      background: 'var(--surface)', display: 'flex', flexDirection: 'column',
      animation: 'slideInLeft .25s ease both',
    }}>
      <div style={{ padding: '16px 18px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontWeight: 700, fontSize: 13.5 }}>Document Details</span>
        <button className="btn btn-icon btn-secondary btn-sm" onClick={onClose} aria-label="Close">
          <X size={14} />
        </button>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: '18px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', paddingTop: 40 }}><div className="spinner" style={{ margin: '0 auto' }} /></div>
        ) : (
          <>
            <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
              <div className="doc-row-icon" style={{ width: 46, height: 46 }}><FileText size={22} /></div>
              <div>
                <div style={{ fontWeight: 700, fontSize: 14, lineHeight: 1.3, wordBreak: 'break-word' }}>{d.original_name}</div>
                <span className={`badge badge-${d.status === 'ready' ? 'ready' : d.status === 'error' ? 'error' : 'processing'}`}
                  style={{ marginTop: 6 }}>
                  {d.status}
                </span>
              </div>
            </div>

            {d.error_message && (
              <div className="alert alert-error" style={{ marginBottom: 16, fontSize: 12 }}>
                {d.error_message}
              </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 18 }}>
              {[
                { icon: Hash, label: 'Pages', value: d.page_count || '—' },
                { icon: HardDrive, label: 'Size', value: `${(d.file_size_bytes / 1024).toFixed(1)} KB` },
                { icon: Calendar, label: 'Uploaded', value: new Date(d.upload_time).toLocaleString('en-IN') },
                { icon: FileSearch, label: 'Index', value: d.status === 'ready' ? 'FAISS (local)' : '—' },
                {
                  icon: ScanText,
                  label: 'Extraction',
                  value: d.ocr_applied ? `OCR (${d.scanned_pages?.length || 1} scanned pgs)` : 'Digital text',
                },
              ].map(({ icon: Icon, label, value }) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)' }}>
                    <Icon size={13} /> {label}
                  </span>
                  <span style={{ fontWeight: 600 }}>{value}</span>
                </div>
              ))}
            </div>

            {d.text_preview && (
              <div style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 8, padding: '12px 14px', marginBottom: 16 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 6, letterSpacing: '.04em', textTransform: 'uppercase' }}>
                  Text Preview
                </div>
                <div style={{ fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.7, maxHeight: 160, overflow: 'auto' }}>
                  {d.text_preview}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <div style={{ padding: '14px 18px', borderTop: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            className="btn btn-primary"
            style={{ flex: 1 }}
            disabled={d.status !== 'ready'}
            onClick={() => onChat(d)}
          >
            <MessageSquare size={14} /> Ask Questions
          </button>
          <button className="btn btn-danger btn-icon" onClick={() => onDelete(d)} title="Delete document">
            <X size={14} />
          </button>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            className="btn btn-secondary"
            style={{ flex: 1, fontSize: 12 }}
            disabled={d.status !== 'ready'}
            onClick={() => onClauses(d)}
          >
            <ShieldAlert size={13} color="var(--navy-400)" /> Clause Analysis
          </button>
          <button
            className="btn btn-secondary"
            style={{ flex: 1, fontSize: 12 }}
            disabled={d.status !== 'ready'}
            onClick={() => onSummarise(d)}
          >
            <Sparkles size={13} color="#f59e0b" /> Summarise
          </button>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            className="btn btn-secondary"
            style={{ flex: 1, fontSize: 12 }}
            disabled={d.status !== 'ready'}
            onClick={() => onBlindSpots(d)}
          >
            <ScanEye size={13} color="#6366f1" /> Blind-Spot Detector
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Documents() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const navigate = useNavigate();

  const refresh = useCallback(() => {
    setLoading(true);
    listDocuments()
      .then(r => setDocs(r.data.documents))
      .catch(() => toast.error('Failed to load documents.'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const handleUploaded = (doc) => {
    refresh();
    toast.success(`"${doc.original_name}" uploaded and indexed!`);
  };

  const handleDelete = async (doc) => {
    if (!window.confirm(`Delete "${doc.original_name}"? This cannot be undone.`)) return;
    try {
      await deleteDocument(doc.id);
      toast.success('Document deleted.');
      if (selectedDoc?.id === doc.id) setSelectedDoc(null);
      refresh();
    } catch {
      toast.error('Failed to delete document.');
    }
  };

  return (
    <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
      {/* Left panel */}
      <div style={{ flex: 1, overflow: 'auto', padding: '28px 32px' }}>
        {/* Upload section */}
        <div style={{ marginBottom: 28 }}>
          <h1 style={{ fontSize: 22, fontWeight: 800, margin: '0 0 4px' }}>Documents</h1>
          <p style={{ fontSize: 13.5, color: 'var(--text-muted)', margin: '0 0 20px' }}>
            Upload legal PDFs, view extraction status, and start asking questions.
          </p>
          <div className="card">
            <div className="card-header">
              <span className="card-title">Upload New Document</span>
            </div>
            <div className="card-body">
              <UploadZone onUploaded={handleUploaded} />
            </div>
          </div>
        </div>

        {/* Document list */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">
              Uploaded Documents
              <span style={{ marginLeft: 8, background: 'var(--surface-3)', padding: '2px 8px', borderRadius: 99, fontSize: 12, fontWeight: 600 }}>
                {docs.length}
              </span>
            </span>
            <button className="btn btn-secondary btn-sm" onClick={refresh} title="Refresh">
              <RefreshCw size={13} />
            </button>
          </div>
          <div style={{ padding: '8px 12px' }}>
            {loading && (
              <div style={{ textAlign: 'center', padding: 32 }}>
                <div className="spinner" style={{ margin: '0 auto' }} />
              </div>
            )}
            {!loading && docs.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon"><FileText size={26} /></div>
                <div style={{ fontWeight: 600 }}>No documents uploaded yet</div>
                <div style={{ fontSize: 12.5, marginTop: 4 }}>Upload a PDF above to get started</div>
              </div>
            )}
            {!loading && docs.map(doc => (
              <DocumentCard
                key={doc.id}
                doc={doc}
                selected={selectedDoc?.id === doc.id}
                onSelect={setSelectedDoc}
                onDelete={handleDelete}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Detail panel */}
      {selectedDoc && (
        <DetailPanel
          doc={selectedDoc}
          onClose={() => setSelectedDoc(null)}
          onDelete={handleDelete}
          onChat={(d) => navigate('/chat', { state: { docId: d.id } })}
          onSummarise={(d) => navigate('/summarise', { state: { docId: d.id } })}
          onClauses={(d) => navigate('/clauses', { state: { docId: d.id } })}
          onBlindSpots={(d) => navigate('/blind-spots', { state: { docId: d.id } })}
        />
      )}
    </div>
  );
}
