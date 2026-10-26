/**
 * Chat page — select a document and ask RAG-powered questions.
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import {
  MessageSquare, Send, FileText, ChevronDown, Bot, User,
  BookOpen, AlertCircle, Info, Loader2, Trash2, History, Lightbulb, Sparkles,
} from 'lucide-react';
import toast from 'react-hot-toast';
import DocumentCard from '../components/DocumentCard';
import { listDocuments, askQuestion } from '../services/api';
import { useAuth } from '../context/AuthContext';

// ── localStorage helpers for chat history ─────────────────────────────────────
const HISTORY_KEY = (userId, docId) => `lexanalyzer_chat_${userId || 'anon'}_${docId}`;
const MAX_STORED_MSGS = 100;

function loadHistory(userId, docId) {
  try {
    const raw = localStorage.getItem(HISTORY_KEY(userId, docId));
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveHistory(userId, docId, messages) {
  try {
    const toSave = messages.slice(-MAX_STORED_MSGS);
    localStorage.setItem(HISTORY_KEY(userId, docId), JSON.stringify(toSave));
  } catch { /* storage full — silently skip */ }
}

function clearHistory(userId, docId) {
  localStorage.removeItem(HISTORY_KEY(userId, docId));
}

// ── Message bubble ─────────────────────────────────────────────────────────────
function Message({ msg }) {
  const isUser = msg.role === 'user';
  const cleanContent = (msg.content || '')
    .replace(/\u00a0/g, ' ')
    .replace(/\u202f/g, ' ')
    .replace(/\u2007/g, ' ');

  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8, opacity: .7, fontSize: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {isUser ? <User size={13} /> : <Bot size={13} />}
          <span>{isUser ? 'You' : 'LexAnalyzer AI'}</span>
        </div>
        {!isUser && msg.eli5 && (
          <span style={{ fontSize: 11, fontWeight: 700, color: '#60a5fa', background: 'rgba(59, 130, 246, 0.15)', padding: '2px 8px', borderRadius: 12, border: '1px solid rgba(59, 130, 246, 0.3)' }}>
            💡 ELI5 Mode
          </span>
        )}
      </div>
      <div className="chat-message-content">{cleanContent}</div>

      {/* Source references */}
      {msg.sources && msg.sources.length > 0 && (
        <div className="chat-sources">
          <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 700, width: '100%', marginBottom: 2 }}>
            📄 Source references:
          </span>
          {msg.sources.map((s, i) => (
            <div key={i} className="source-tag" title={s.snippet}>
              <BookOpen size={10} /> Page {s.page}
            </div>
          ))}
          {/* First snippet preview */}
          {msg.sources[0]?.snippet && (
            <div style={{
              fontSize: 11.5, color: 'var(--text-secondary)', lineHeight: 1.6,
              background: 'var(--surface-2)', borderRadius: 6, padding: '8px 10px',
              width: '100%', marginTop: 4, fontStyle: 'italic',
              borderLeft: '3px solid var(--navy-300)',
            }}>
              "{msg.sources[0].snippet}…"
            </div>
          )}
        </div>
      )}

      {/* LLM not configured warning inside AI message */}
      {!isUser && msg.llm_configured === false && (
        <div className="alert alert-warning" style={{ marginTop: 12, fontSize: 12 }}>
          <AlertCircle size={13} /> LLM not configured — see the banner at the top for setup instructions.
        </div>
      )}
    </div>
  );
}

// ── Document selector ──────────────────────────────────────────────────────────
function DocSelector({ docs, selected, onSelect }) {
  const [open, setOpen] = useState(false);
  const ref = useRef();

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button
        className="btn btn-secondary"
        style={{ maxWidth: 280, overflow: 'hidden' }}
        onClick={() => setOpen(o => !o)}
        id="doc-selector-btn"
      >
        <FileText size={14} />
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1, textAlign: 'left' }}>
          {selected ? selected.original_name : 'Select a document…'}
        </span>
        <ChevronDown size={14} />
      </button>

      {open && (
        <div style={{
          position: 'absolute', top: '110%', left: 0, width: 340,
          background: 'var(--surface)', border: '1px solid var(--border)',
          borderRadius: 10, boxShadow: 'var(--shadow-lg)', zIndex: 50,
          maxHeight: 300, overflow: 'auto', animation: 'fadeInUp .2s ease both',
        }}>
          {docs.length === 0 ? (
            <div style={{ padding: '20px 16px', textAlign: 'center', fontSize: 13, color: 'var(--text-muted)' }}>
              No ready documents. Upload a PDF first.
            </div>
          ) : (
            docs.filter(d => d.status === 'ready').map(doc => (
              <DocumentCard
                key={doc.id}
                doc={doc}
                selected={selected?.id === doc.id}
                onSelect={(d) => { onSelect(d); setOpen(false); }}
                showDelete={false}
              />
            ))
          )}
        </div>
      )}
    </div>
  );
}

// ── Main Chat page ─────────────────────────────────────────────────────────────
export default function Chat() {
  const { user } = useAuth();
  const location = useLocation();
  const [docs, setDocs] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [eli5Mode, setEli5Mode] = useState(false);
  const bottomRef = useRef();
  const textareaRef = useRef();

  // Load documents on mount
  useEffect(() => {
    listDocuments()
      .then(r => {
        const ready = r.data.documents.filter(d => d.status === 'ready');
        setDocs(r.data.documents);
        // If navigated from Documents page with a pre-selected doc
        if (location.state?.docId) {
          const pre = ready.find(d => d.id === location.state.docId);
          if (pre) setSelectedDoc(pre);
        }
      })
      .catch(() => toast.error('Failed to load documents.'));
  }, [location.state]);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const handleSelectDoc = (doc) => {
    setSelectedDoc(doc);
    // Load persisted history for this document and user
    setMessages(loadHistory(user?.id, doc.id));
    setInput('');
  };

  const handleSend = useCallback(async () => {
    const q = input.trim();
    if (!q || !selectedDoc || sending) return;

    const userMsg = { role: 'user', content: q, timestamp: new Date().toISOString() };
    setMessages(m => {
      const updated = [...m, userMsg];
      saveHistory(user?.id, selectedDoc.id, updated);
      return updated;
    });
    setInput('');
    setSending(true);

    try {
      const { data } = await askQuestion(selectedDoc.id, q, eli5Mode);
      setMessages(m => {
        const updated = [...m, {
          role: 'assistant',
          content: data.answer,
          sources: data.sources,
          llm_configured: data.llm_configured,
          eli5: eli5Mode || data.eli5,
          timestamp: new Date().toISOString(),
        }];
        saveHistory(user?.id, selectedDoc.id, updated);
        return updated;
      });
    } catch (err) {
      const errMsg = err.response?.data?.detail || 'An error occurred. Please try again.';
      setMessages(m => {
        const updated = [...m, { role: 'assistant', content: `❌ ${errMsg}`, sources: [], timestamp: new Date().toISOString() }];
        saveHistory(user?.id, selectedDoc.id, updated);
        return updated;
      });
    } finally {
      setSending(false);
    }
  }, [input, selectedDoc, sending, user?.id, eli5Mode]);

  const handleClearHistory = useCallback(() => {
    if (!selectedDoc) return;
    clearHistory(user?.id, selectedDoc.id);
    setMessages([]);
    toast.success('Chat history cleared.');
  }, [selectedDoc, user?.id]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const STANDARD_SUGGESTIONS = [
    'What are the main obligations of each party?',
    'Are there any termination clauses?',
    'What is the governing law?',
    'Summarize the payment terms.',
  ];

  const ELI5_SUGGESTIONS = [
    'Explain this whole agreement like I\'m 5',
    'What are the biggest financial traps in this contract?',
    'What happens if I want to break this deal?',
    'Who has to pay if someone gets sued?',
  ];

  const SUGGESTIONS = eli5Mode ? ELI5_SUGGESTIONS : STANDARD_SUGGESTIONS;

  return (
    <div style={{ display: 'flex', flex: 1, height: '100%', overflow: 'hidden' }}>
      {/* Sidebar — document selector */}
      <div style={{ width: 260, borderRight: '1px solid var(--border)', background: 'var(--surface)', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '18px 16px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ fontWeight: 700, fontSize: 13.5, marginBottom: 4 }}>Select Document</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Only indexed documents are available</div>
        </div>
        <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
          {docs.filter(d => d.status === 'ready').length === 0 ? (
            <div className="empty-state" style={{ padding: '24px 12px' }}>
              <div className="empty-icon"><FileText size={20} /></div>
              <div style={{ fontSize: 12.5, fontWeight: 600 }}>No ready documents</div>
              <div style={{ fontSize: 11.5, marginTop: 3 }}>Upload a PDF on the Documents page</div>
            </div>
          ) : (
            docs.filter(d => d.status === 'ready').map(doc => (
              <DocumentCard
                key={doc.id}
                doc={doc}
                selected={selectedDoc?.id === doc.id}
                onSelect={handleSelectDoc}
                showDelete={false}
              />
            ))
          )}
        </div>
      </div>

      {/* Main chat area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Top bar */}
        <div style={{
          padding: '12px 20px', borderBottom: '1px solid var(--border)',
          background: 'var(--surface)', display: 'flex', alignItems: 'center', gap: 12,
          flexShrink: 0,
        }}>
          <MessageSquare size={18} style={{ color: 'var(--navy-600)' }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: 14 }}>
              {selectedDoc ? selectedDoc.original_name : 'Document Chat'}
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)' }}>
              {selectedDoc
                ? `${selectedDoc.page_count} pages · Ask anything about this document`
                : 'Select a document from the left panel to begin'}
            </div>
          </div>
          {/* ELI5 Mode Toggle */}
          <button
            onClick={() => {
              setEli5Mode(prev => {
                const next = !prev;
                toast(next ? '👶 ELI5 Mode: Simple English & Analogies Active' : '⚖️ Standard Mode: Strict Legal Responses Active', {
                  icon: next ? '💡' : '⚖️',
                });
                return next;
              });
            }}
            className="btn btn-sm"
            style={{
              gap: 6,
              fontSize: 12,
              background: eli5Mode ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255, 255, 255, 0.05)',
              border: `1px solid ${eli5Mode ? '#3b82f6' : 'var(--border)'}`,
              color: eli5Mode ? '#93c5fd' : 'var(--text-secondary)',
              fontWeight: eli5Mode ? 700 : 500,
              padding: '6px 12px',
            }}
            title="Toggle Explain Like I'm 5 (Plain English & Real-World Analogies)"
          >
            <Lightbulb size={13} color={eli5Mode ? '#60a5fa' : 'currentColor'} />
            {eli5Mode ? 'ELI5 Mode: ON' : 'ELI5 Mode: OFF'}
          </button>

          {/* Clear history button */}
          {selectedDoc && messages.length > 0 && (
            <button
              onClick={handleClearHistory}
              className="btn btn-secondary btn-sm"
              style={{ gap: 5, fontSize: 12 }}
              title="Clear chat history"
            >
              <Trash2 size={13} /> Clear
            </button>
          )}
          {/* Persisted history indicator */}
          {selectedDoc && messages.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, color: 'var(--text-muted)' }}>
              <History size={11} /> {messages.length} msgs saved
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="chat-messages">
          {/* Empty / no doc selected state */}
          {!selectedDoc && (
            <div className="empty-state" style={{ flex: 1, justifyContent: 'center' }}>
              <div className="empty-icon" style={{ width: 72, height: 72, margin: '0 auto 16px' }}>
                <MessageSquare size={30} />
              </div>
              <div style={{ fontWeight: 700, fontSize: 16 }}>Select a document to start</div>
              <div style={{ fontSize: 13, marginTop: 6, maxWidth: 320, lineHeight: 1.6 }}>
                Choose an indexed legal document from the left panel, then ask questions in plain language.
              </div>
            </div>
          )}

          {/* Welcome message on doc select */}
          {selectedDoc && messages.length === 0 && (
            <div className="empty-state" style={{ flex: 1, justifyContent: 'center' }}>
              <div className="empty-icon" style={{ width: 64, height: 64, margin: '0 auto 14px' }}>
                <Bot size={28} />
              </div>
              <div style={{ fontWeight: 700, fontSize: 15 }}>Ready to answer questions</div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 5, marginBottom: 20 }}>
                Document: <strong>{selectedDoc.original_name}</strong>
              </div>
              {/* Suggestion chips */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', maxWidth: 480 }}>
                {SUGGESTIONS.map(s => (
                  <button
                    key={s}
                    className="btn btn-secondary btn-sm"
                    style={{ fontSize: 12 }}
                    onClick={() => { setInput(s); textareaRef.current?.focus(); }}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Actual messages */}
          {messages.map((msg, i) => <Message key={i} msg={msg} />)}

          {/* Thinking indicator */}
          {sending && (
            <div className="chat-message assistant" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <Loader2 size={16} className="animate-spin-slow" />
              <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Retrieving context and generating answer…</span>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input area */}
        <div className="chat-input-area">
          <textarea
            ref={textareaRef}
            id="chat-input"
            className="chat-input"
            placeholder={
              selectedDoc
                ? eli5Mode
                  ? 'Ask anything (ELI5 Mode: answers will use simple English and real-world analogies)…'
                  : 'Ask a question about the document… (Enter to send, Shift+Enter for new line)'
                : 'Select a document first'
            }
            value={input}
            disabled={!selectedDoc || sending}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
          <button
            id="send-btn"
            className="btn btn-primary"
            disabled={!selectedDoc || !input.trim() || sending}
            onClick={handleSend}
            style={{ height: 46, minWidth: 46 }}
            aria-label="Send"
          >
            {sending ? <Loader2 size={16} className="animate-spin-slow" /> : <Send size={16} />}
          </button>
        </div>
      </div>
    </div>
  );
}
