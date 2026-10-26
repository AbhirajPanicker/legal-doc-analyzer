import { useState, useEffect } from 'react';
import {
  Lightbulb, Search, BookOpen, ShieldCheck,
  Sparkles, ArrowRight, Copy, Check, Info, HelpCircle
} from 'lucide-react';
import toast from 'react-hot-toast';
import { decodeJargon, getJargonPresets } from '../services/api';

const POPULAR_PILLS = [
  { id: 'indemnification', label: 'Indemnification' },
  { id: 'force_majeure', label: 'Force Majeure' },
  { id: 'limitation_of_liability', label: 'Liability Cap' },
  { id: 'severability', label: 'Severability' },
  { id: 'liquidated_damages', label: 'Liquidated Damages' },
  { id: 'non_disclosure', label: 'Confidentiality' },
];

export default function JargonDecoder() {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  // Auto-decode default term on mount so page is never empty
  useEffect(() => {
    handleDecode('Indemnification');
  }, []);

  const handleDecode = async (textToDecode) => {
    const text = textToDecode || inputText;
    if (!text.trim()) {
      toast.error('Please enter a legal term or paste a clause to decode.');
      return;
    }
    setLoading(true);
    try {
      const res = await decodeJargon(text);
      setResult(res.data);
      if (textToDecode) setInputText(textToDecode);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to decode legal term.');
    } finally {
      setLoading(false);
    }
  };

  const copyResult = () => {
    if (!result) return;
    const text = `Term: ${result.term}\n\nPlain English: ${result.plain_english}\n\nAnalogy: ${result.real_life_analogy}\n\nWhy Lawyers Put It In: ${result.why_it_matters}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('Copied ELI5 explanation to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="page-content" style={{ maxWidth: 1040, margin: '0 auto', padding: '24px 20px' }}>
      {/* Hero Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '4px 12px', borderRadius: 20, background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.25)', color: 'var(--primary-light, #60a5fa)', fontSize: 12, fontWeight: 600, marginBottom: 8 }}>
          <Lightbulb size={14} /> Explain Like I'm 5 (ELI5) Mode
        </div>
        <h1 style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
          Legal Jargon Decoder
        </h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4, marginBottom: 0 }}>
          Demystify intimidating legal clauses, Latin phrases, and contract doctrines into plain English with relatable real-world analogies.
        </p>
      </div>

      {/* Input Search Box */}
      <div className="card" style={{ padding: 20, marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 14 }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleDecode()}
              placeholder="Paste any confusing legal clause, Latin term, or phrase (e.g. 'Indemnify and hold harmless', 'Force Majeure')..."
              style={{
                width: '100%',
                padding: '12px 14px 12px 42px',
                borderRadius: 8,
                border: '1px solid var(--border, #d4dae8)',
                background: 'var(--surface-2, #f7f9fc)',
                color: 'var(--text-primary, #0d1528)',
                fontSize: 14,
                outline: 'none',
                transition: 'border-color 0.2s, box-shadow 0.2s, background 0.2s',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'var(--navy-500, #2a52a8)';
                e.target.style.background = '#ffffff';
                e.target.style.boxShadow = '0 0 0 3px rgba(42, 82, 168, 0.12)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'var(--border, #d4dae8)';
                e.target.style.background = 'var(--surface-2, #f7f9fc)';
                e.target.style.boxShadow = 'none';
              }}
            />
          </div>
          <button
            onClick={() => handleDecode()}
            disabled={loading}
            className="btn btn-primary"
            style={{ padding: '12px 24px', display: 'flex', alignItems: 'center', gap: 8, fontWeight: 600 }}
          >
            {loading ? <span className="spinner-border spinner-border-sm" /> : <Sparkles size={16} />}
            Decode (ELI5)
          </button>
        </div>

        {/* Popular Quick Pills */}
        <div>
          <span style={{ fontSize: 12, color: 'var(--text-muted)', marginRight: 10, fontWeight: 600 }}>
            Quick Topics:
          </span>
          <div style={{ display: 'inline-flex', flexWrap: 'wrap', gap: 6, marginTop: 4 }}>
            {POPULAR_PILLS.map((pill) => (
              <button
                key={pill.id}
                onClick={() => handleDecode(pill.label)}
                style={{
                  background: 'var(--surface-2, #f1f5f9)',
                  border: '1px solid var(--border, #d4dae8)',
                  borderRadius: 16,
                  padding: '4px 12px',
                  fontSize: 12,
                  color: 'var(--text-secondary, #475569)',
                  cursor: 'pointer',
                  fontWeight: 500,
                  transition: 'all 0.15s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
                  e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.4)';
                  e.currentTarget.style.color = 'var(--navy-600, #204080)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'var(--surface-2, #f1f5f9)';
                  e.currentTarget.style.borderColor = 'var(--border, #d4dae8)';
                  e.currentTarget.style.color = 'var(--text-secondary, #475569)';
                }}
              >
                {pill.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Result Display */}
      {result && (
        <div className="card" style={{ padding: 24, border: '1px solid rgba(59, 130, 246, 0.3)', background: 'var(--navy-900, #0f172a)' }}>
          {/* Header & Category */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', paddingBottom: 16, marginBottom: 20 }}>
            <div>
              <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#60a5fa' }}>
                {result.category || 'Legal Concept'}
              </span>
              <h2 style={{ fontSize: 22, fontWeight: 700, color: '#f8fafc', margin: '4px 0 0' }}>
                {result.term}
              </h2>
            </div>
            <button
              onClick={copyResult}
              className="btn btn-secondary"
              style={{ fontSize: 12, padding: '6px 12px', display: 'flex', alignItems: 'center', gap: 6 }}
            >
              {copied ? <Check size={14} color="#22c55e" /> : <Copy size={14} />}
              {copied ? 'Copied' : 'Copy'}
            </button>
          </div>

          {/* 3 Pillars of ELI5 Translation */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
            {/* 1. Plain English */}
            <div style={{ background: 'rgba(59, 130, 246, 0.06)', border: '1px solid rgba(59, 130, 246, 0.2)', borderRadius: 10, padding: 18 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#60a5fa', fontWeight: 700, fontSize: 14, marginBottom: 8 }}>
                <span>🎈</span> In Plain English (What it means)
              </div>
              <p style={{ fontSize: 14, lineHeight: 1.6, color: '#e2e8f0', margin: 0 }}>
                {result.plain_english}
              </p>
            </div>

            {/* 2. Real Life Analogy */}
            <div style={{ background: 'rgba(168, 85, 247, 0.06)', border: '1px solid rgba(168, 85, 247, 0.2)', borderRadius: 10, padding: 18 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#c084fc', fontWeight: 700, fontSize: 14, marginBottom: 8 }}>
                <span>🍕</span> Real-Life Analogy
              </div>
              <p style={{ fontSize: 14, lineHeight: 1.6, color: '#e2e8f0', margin: 0 }}>
                {result.real_life_analogy}
              </p>
            </div>

            {/* 3. Why it matters */}
            <div style={{ background: 'rgba(16, 185, 129, 0.06)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: 10, padding: 18 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#34d399', fontWeight: 700, fontSize: 14, marginBottom: 8 }}>
                <span>🎯</span> Why Lawyers Put It In
              </div>
              <p style={{ fontSize: 14, lineHeight: 1.6, color: '#e2e8f0', margin: 0 }}>
                {result.why_it_matters}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
