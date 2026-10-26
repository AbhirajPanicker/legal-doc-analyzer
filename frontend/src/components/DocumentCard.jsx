/**
 * DocumentCard — a single row in the document list used on Documents and Chat pages.
 */
import { FileText, Trash2, CheckCircle2, AlertCircle, Clock, ScanText } from 'lucide-react';

function StatusBadge({ status, ocrApplied }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      {ocrApplied && (
        <span
          className="badge"
          style={{
            background: 'rgba(59, 130, 246, 0.15)',
            color: '#60a5fa',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 4,
            padding: '2px 7px',
            fontSize: '11px',
            fontWeight: 600,
          }}
          title="Extracted via OCR from scanned document"
        >
          <ScanText size={11} /> OCR
        </span>
      )}
      {status === 'ready' && <span className="badge badge-ready"><CheckCircle2 size={10} /> Ready</span>}
      {status === 'error' && <span className="badge badge-error"><AlertCircle size={10} /> Error</span>}
      {status !== 'ready' && status !== 'error' && <span className="badge badge-processing"><Clock size={10} /> Processing</span>}
    </div>
  );
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
  });
}

export default function DocumentCard({ doc, selected, onSelect, onDelete, showDelete = true }) {
  return (
    <div
      className={`doc-row ${selected ? 'selected' : ''}`}
      onClick={() => onSelect && onSelect(doc)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onSelect && onSelect(doc)}
    >
      <div className="doc-row-icon">
        <FileText size={18} />
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <div className="doc-row-name" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {doc.original_name}
        </div>
        <div className="doc-row-meta">
          {doc.page_count > 0 && `${doc.page_count} pages · `}
          {formatSize(doc.file_size_bytes)} · {formatDate(doc.upload_time)}
        </div>
        {doc.error_message && (
          <div style={{ fontSize: 11.5, color: 'var(--error)', marginTop: 3 }}>
            {doc.error_message}
          </div>
        )}
      </div>

      <StatusBadge status={doc.status} ocrApplied={doc.ocr_applied} />

      {showDelete && (
        <button
          className="btn btn-icon btn-danger btn-sm"
          onClick={(e) => { e.stopPropagation(); onDelete && onDelete(doc); }}
          title="Delete document"
          aria-label="Delete"
        >
          <Trash2 size={14} />
        </button>
      )}
    </div>
  );
}
