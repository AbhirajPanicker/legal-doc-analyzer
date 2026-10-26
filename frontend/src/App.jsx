import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useEffect, useState } from 'react';
import { AuthProvider } from './context/AuthContext';
import RequireAuth from './components/RequireAuth';
import Sidebar from './components/Sidebar';
import StatusBanner from './components/StatusBanner';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Summarise from './pages/Summarise';
import ClauseAnalysis from './pages/ClauseAnalysis';
import BlindSpots from './pages/BlindSpots';
import JargonDecoder from './pages/JargonDecoder';
import Chat from './pages/Chat';
import AuthPage from './pages/AuthPage';
import { getStatus } from './services/api';

function AppShell() {
  const [llmConfigured, setLlmConfigured] = useState(true);

  useEffect(() => {
    getStatus()
      .then(r => setLlmConfigured(r.data.llm_configured))
      .catch(() => {});
  }, []);

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-main">
        <StatusBanner llmConfigured={llmConfigured} />
        <Routes>
          <Route path="/" element={<RequireAuth><Dashboard /></RequireAuth>} />
          <Route path="/documents" element={<RequireAuth><Documents /></RequireAuth>} />
          <Route path="/summarise" element={<RequireAuth><Summarise /></RequireAuth>} />
          <Route path="/clauses" element={<RequireAuth><ClauseAnalysis /></RequireAuth>} />
          <Route path="/blind-spots" element={<RequireAuth><BlindSpots /></RequireAuth>} />
          <Route path="/jargon-decoder" element={<RequireAuth><JargonDecoder /></RequireAuth>} />
          <Route path="/chat" element={<RequireAuth><Chat /></RequireAuth>} />
        </Routes>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public route — no sidebar */}
          <Route path="/login" element={<AuthPage />} />
          {/* All other routes go through the app shell with sidebar */}
          <Route path="/*" element={<AppShell />} />
        </Routes>
        <Toaster
          position="bottom-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'var(--navy-900)',
              color: '#fff',
              borderRadius: '10px',
              fontSize: '13.5px',
              fontFamily: 'Inter, sans-serif',
            },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  );
}
