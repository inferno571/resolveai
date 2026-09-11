import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import {
  Layers, Search, HelpCircle,
  Settings, MessageSquare, Terminal, FileText
} from 'lucide-react';
import { ResolvePage } from './pages/ResolvePage';
import { ResolutionPage } from './pages/ResolutionPage';
import { CasesPage } from './pages/CasesPage';
import { AdminPage } from './pages/AdminPage';
import { api } from './api';
import './index.css';

function Header() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/cases?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="so-header">
      <div className="so-header-inner">
        {/* Logo */}
        <NavLink to="/" className="so-logo-link">
          <div className="so-logo-icon">
            <Layers size={18} />
          </div>
          <span className="so-logo-text">
            Resolve<b>AI</b>
          </span>
          <span className="so-logo-badge">Hybrid RAG+CBR</span>
        </NavLink>

        {/* Global Search Bar */}
        <form onSubmit={handleSearchSubmit} className="so-search-container">
          <Search size={15} className="so-search-icon" />
          <input
            type="text"
            className="so-search-input"
            placeholder="Search errors, tools (pip, git, python), or past cases... [ / ]"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <span className="so-search-shortcut">/</span>
        </form>

        {/* Right Status / Actions */}
        <div className="so-header-right">
          <div className="so-provider-pill" title="Active LLM Backend Provider">
            <span className="so-status-dot" />
            <span>Gemini 3.8 Flash</span>
          </div>

          <NavLink to="/" className="so-btn-primary" style={{ padding: '6px 12px', fontSize: '12px' }}>
            Ask Question
          </NavLink>

          <NavLink to="/admin" className="so-header-btn" title="Settings & Admin">
            <Settings size={16} />
          </NavLink>
        </div>
      </div>
    </header>
  );
}

function LeftSidebar() {
  const [caseCount, setCaseCount] = useState<number | null>(null);

  useEffect(() => {
    api.getCaseStats()
      .then(stats => setCaseCount(stats.total_cases))
      .catch(() => setCaseCount(55));
  }, []);

  return (
    <aside className="so-left-sidebar">
      <div className="so-nav-section-title">PUBLIC</div>
      
      <NavLink
        to="/"
        end
        className={({ isActive }) => `so-nav-item ${isActive ? 'active' : ''}`}
      >
        <MessageSquare size={16} />
        <span>Troubleshoot</span>
      </NavLink>

      <NavLink
        to="/cases"
        className={({ isActive }) => `so-nav-item ${isActive ? 'active' : ''}`}
      >
        <HelpCircle size={16} />
        <span>Questions / Cases</span>
        <span className="so-nav-badge">{caseCount ?? 55}</span>
      </NavLink>

      <div className="so-nav-section-title">KNOWLEDGE BASE</div>

      <NavLink
        to="/admin"
        className={({ isActive }) => `so-nav-item ${isActive ? 'active' : ''}`}
      >
        <FileText size={16} />
        <span>RAG Manuals</span>
      </NavLink>

      <NavLink
        to="/cases?status=verified"
        className={({ isActive }) => `so-nav-item ${isActive ? 'active' : ''}`}
      >
        <Terminal size={16} />
        <span>CBR Memory</span>
      </NavLink>

      <div className="so-nav-section-title">SYSTEM</div>

      <NavLink
        to="/admin"
        className={({ isActive }) => `so-nav-item ${isActive ? 'active' : ''}`}
      >
        <Settings size={16} />
        <span>Admin & Metrics</span>
      </NavLink>
    </aside>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Header />
        <div className="so-body-wrapper">
          <LeftSidebar />
          <main className="so-main-content">
            <Routes>
              <Route path="/" element={<ResolvePage />} />
              <Route path="/resolve/:id" element={<ResolutionPage />} />
              <Route path="/cases" element={<CasesPage />} />
              <Route path="/admin" element={<AdminPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
