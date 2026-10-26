/**
 * StatusBanner — shown at the top of every page when the LLM is not configured.
 */
import { AlertTriangle, X } from 'lucide-react';
import { useState } from 'react';

export default function StatusBanner({ llmConfigured }) {
  const [dismissed, setDismissed] = useState(false);
  if (llmConfigured || dismissed) return null;

  return (
    <div className="alert alert-warning animate-fade-in-up"
      style={{ margin: '16px 32px 0', borderRadius: 10 }}>
      <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: 2 }} />
      <div style={{ flex: 1 }}>
        <strong>LLM not configured.</strong> Copy{' '}
        <code style={{ fontSize: 12, background: 'rgba(0,0,0,0.08)', padding: '1px 5px', borderRadius: 4 }}>
          backend/.env.example
        </code>{' '}
        to{' '}
        <code style={{ fontSize: 12, background: 'rgba(0,0,0,0.08)', padding: '1px 5px', borderRadius: 4 }}>
          backend/.env
        </code>{' '}
        and add your Google or OpenAI API key, then restart the backend.
        Document upload and text extraction will still work.
      </div>
      <button
        onClick={() => setDismissed(true)}
        style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 2, color: 'inherit', opacity: .6 }}
        aria-label="Dismiss"
      >
        <X size={15} />
      </button>
    </div>
  );
}
