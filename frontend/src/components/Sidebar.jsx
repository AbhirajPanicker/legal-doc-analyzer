import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, FileText, MessageSquare, Scale, BookOpen,
  Sparkles, ShieldAlert, LogOut, User, ScanEye, Lightbulb,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const NAV = [
  { to: '/',               icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/documents',      icon: FileText,        label: 'Documents' },
  { to: '/summarise',      icon: Sparkles,        label: 'Summarise' },
  { to: '/clauses',        icon: ShieldAlert,     label: 'Clause Analysis' },
  { to: '/blind-spots',    icon: ScanEye,         label: 'Blind-Spot Detector' },
  { to: '/jargon-decoder', icon: Lightbulb,       label: 'Jargon Decoder (ELI5)' },
  { to: '/chat',           icon: MessageSquare,   label: 'Document Chat' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  // Generate initials avatar from name or email
  const initials = user
    ? (user.full_name?.trim()
        ? user.full_name.trim().split(/\s+/).map(w => w[0]).join('').toUpperCase().slice(0, 2)
        : user.email[0].toUpperCase())
    : '?';

  return (
    <aside className="app-sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">
          <Scale size={18} color="#fff" />
        </div>
        <div className="sidebar-title">LexAnalyzer</div>
        <div className="sidebar-sub">Legal Document AI</div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div style={{ fontSize: 10, fontWeight: 700, color: 'rgba(255,255,255,0.25)',
          letterSpacing: '.08em', padding: '8px 12px 4px', textTransform: 'uppercase' }}>
          Navigation
        </div>
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Icon size={16} className="nav-item-icon" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User profile + logout */}
      {user && (
        <div style={{
          marginTop: 'auto',
          borderTop: '1px solid rgba(255,255,255,0.08)',
          padding: '14px 12px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
            {/* Avatar */}
            <div style={{
              width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
              background: 'linear-gradient(135deg, var(--navy-600), var(--navy-400))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 12, fontWeight: 800, color: '#fff',
            }}>
              {initials}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{
                fontSize: 12.5, fontWeight: 700, color: 'rgba(255,255,255,0.9)',
                overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
              }}>
                {user.full_name || 'My Account'}
              </div>
              <div style={{
                fontSize: 11, color: 'rgba(255,255,255,0.35)',
                overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
              }}>
                {user.email}
              </div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            style={{
              width: '100%', display: 'flex', alignItems: 'center', gap: 8,
              background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)',
              borderRadius: 8, padding: '7px 12px', cursor: 'pointer',
              color: '#f87171', fontSize: 12.5, fontWeight: 600,
              transition: 'background .15s',
            }}
            onMouseEnter={e => e.currentTarget.style.background = 'rgba(239,68,68,0.18)'}
            onMouseLeave={e => e.currentTarget.style.background = 'rgba(239,68,68,0.08)'}
          >
            <LogOut size={13} />
            Sign Out
          </button>
        </div>
      )}

      {/* Footer */}
      <div className="sidebar-footer" style={user ? { paddingTop: 0, borderTop: 'none' } : {}}>
        {!user && (
          <div className="sidebar-badge">
            <Scale size={12} />
            AI Legal Intelligence
          </div>
        )}
      </div>
    </aside>
  );
}
