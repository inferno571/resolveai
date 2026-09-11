import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Search, Filter, ChevronDown, ChevronUp,
  CheckCircle, Database, HelpCircle,
  ExternalLink
} from 'lucide-react';
import { api, type CaseData } from '../api';

export function CasesPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [cases, setCases] = useState<CaseData[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [filterTool, setFilterTool] = useState(searchParams.get('tool') || '');
  const [filterOS, setFilterOS] = useState(searchParams.get('os') || '');
  const [filterStatus, setFilterStatus] = useState(searchParams.get('status') || '');
  const [activeTab, setActiveTab] = useState<'newest' | 'active' | 'verified'>('newest');
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [stats, setStats] = useState<{ total_cases: number; verified_cases: number; by_tool: Record<string, number>; by_os: Record<string, number> } | null>(null);

  useEffect(() => {
    loadCases();
    loadStats();
  }, [filterTool, filterOS, filterStatus]);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) setSearchQuery(q);
  }, [searchParams]);

  const loadCases = async () => {
    setLoading(true);
    try {
      const data = await api.getCases({
        tool: filterTool || undefined,
        operating_system: filterOS || undefined,
        verification_status: filterStatus || undefined,
        limit: 100,
      });
      setCases(data);
    } catch (err) {
      console.error('Failed to load cases:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await api.getCaseStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const filteredCases = cases.filter(c => {
    const q = searchQuery.toLowerCase();
    const matchesSearch = !q ||
      c.problem.toLowerCase().includes(q) ||
      c.error_code.toLowerCase().includes(q) ||
      c.verified_solution.toLowerCase().includes(q) ||
      c.tool.toLowerCase().includes(q);

    if (activeTab === 'verified') {
      return matchesSearch && c.verification_status === 'verified';
    }
    return matchesSearch;
  });

  return (
    <div style={{ display: 'flex', gap: 24 }}>
      {/* Main Questions / Cases Feed */}
      <div style={{ flex: 1, minWidth: 0 }}>
        {/* Top Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h1 style={{ fontSize: 24, fontWeight: 500, color: 'var(--text-primary)' }}>
            All Solved Questions & Cases
          </h1>
          <button
            className="so-btn-primary"
            onClick={() => navigate('/')}
          >
            Ask Question
          </button>
        </div>

        {/* Count and Filter Tabs Bar (Exactly like Stack Overflow) */}
        <div className="so-filter-bar">
          <div style={{ fontSize: 16, color: 'var(--text-primary)' }}>
            <b>{filteredCases.length}</b> questions
          </div>

          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <div className="so-filter-group">
              <button
                className={`so-filter-btn ${activeTab === 'newest' ? 'active' : ''}`}
                onClick={() => setActiveTab('newest')}
              >
                Newest
              </button>
              <button
                className={`so-filter-btn ${activeTab === 'active' ? 'active' : ''}`}
                onClick={() => setActiveTab('active')}
              >
                Active
              </button>
              <button
                className={`so-filter-btn ${activeTab === 'verified' ? 'active' : ''}`}
                onClick={() => setActiveTab('verified')}
              >
                Verified Only
              </button>
            </div>

            <button
              className="so-btn-outline"
              onClick={() => {
                setFilterTool('');
                setFilterOS('');
                setFilterStatus('');
                setSearchQuery('');
              }}
            >
              <Filter size={13} />
              <span>Reset</span>
            </button>
          </div>
        </div>

        {/* Filter Controls Row */}
        <div style={{
          display: 'flex',
          gap: 10,
          padding: '10px 12px',
          background: '#f8f9fa',
          border: '1px solid var(--border-base)',
          borderRadius: 'var(--radius-xs)',
          marginBottom: 16,
          flexWrap: 'wrap',
          alignItems: 'center',
        }}>
          <div style={{ flex: 1, minWidth: 200, position: 'relative' }}>
            <Search size={14} style={{ position: 'absolute', left: 8, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              className="so-input"
              style={{ paddingLeft: 28, fontSize: 12 }}
              placeholder="Filter by error message or keyword..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <select
            className="so-input"
            style={{ width: 130, fontSize: 12 }}
            value={filterTool}
            onChange={(e) => setFilterTool(e.target.value)}
          >
            <option value="">All Tools</option>
            <option value="python">Python</option>
            <option value="pip">pip</option>
            <option value="venv">venv</option>
            <option value="git">Git</option>
          </select>

          <select
            className="so-input"
            style={{ width: 130, fontSize: 12 }}
            value={filterOS}
            onChange={(e) => setFilterOS(e.target.value)}
          >
            <option value="">All Platforms</option>
            <option value="windows">Windows</option>
            <option value="linux">Linux</option>
            <option value="macos">macOS</option>
          </select>
        </div>

        {/* Question Rows (Stack Overflow Style) */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
            <div className="spinner" style={{ margin: '0 auto 12px auto', borderTopColor: 'var(--so-blue)' }} />
            <div>Loading verified cases from database...</div>
          </div>
        ) : filteredCases.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 20px', border: '1px dashed var(--border-dark)', borderRadius: 'var(--radius-xs)' }}>
            <HelpCircle size={32} style={{ color: 'var(--text-muted)', marginBottom: 8 }} />
            <h3 style={{ fontSize: 16, color: 'var(--text-primary)', marginBottom: 6 }}>No Questions Found</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16 }}>
              No cases matched your current search filters.
            </p>
            <button className="so-btn-primary" onClick={() => navigate('/')}>
              Ask a New Question
            </button>
          </div>
        ) : (
          <div style={{ borderTop: '1px solid var(--border-base)' }}>
            {filteredCases.map((c) => {
              const isExpanded = expandedId === c.id;
              return (
                <div key={c.id} className="so-question-row">
                  {/* Left Stats Box (Votes, Answers/Verified, Views) */}
                  <div className="so-question-stats">
                    <div className="so-stat-item">
                      <span>0 votes</span>
                    </div>
                    <div className={`so-stat-item ${c.verification_status === 'verified' ? 'verified-box' : ''}`}>
                      <CheckCircle size={12} />
                      <span>1 answer</span>
                    </div>
                    <div className="so-stat-item" style={{ color: 'var(--text-muted)', fontSize: 11 }}>
                      <span>24 views</span>
                    </div>
                  </div>

                  {/* Summary & Tags */}
                  <div className="so-question-summary">
                    <div
                      className="so-question-title"
                      onClick={() => setExpandedId(isExpanded ? null : c.id)}
                    >
                      {c.problem}
                    </div>

                    <div className="so-question-excerpt">
                      {c.symptoms || c.supporting_evidence || c.error_code}
                    </div>

                    <div className="so-question-meta-row">
                      {/* Tags */}
                      <div className="so-question-tags">
                        {c.tool && (
                          <span
                            className="so-tag"
                            onClick={(e) => { e.stopPropagation(); setFilterTool(c.tool); }}
                          >
                            {c.tool}
                          </span>
                        )}
                        {c.operating_system && (
                          <span
                            className="so-tag"
                            onClick={(e) => { e.stopPropagation(); setFilterOS(c.operating_system); }}
                          >
                            {c.operating_system}
                          </span>
                        )}
                        {c.version && (
                          <span className="so-tag">v{c.version}</span>
                        )}
                        {c.error_code && (
                          <span className="so-tag" style={{ background: '#fcf0f0', color: '#b91c1c' }}>
                            {c.error_code.split(':')[0]}
                          </span>
                        )}
                      </div>

                      {/* User Card */}
                      <div className="so-user-card">
                        <div className="so-avatar">T</div>
                        <div>
                          <span style={{ color: 'var(--so-link)' }}>Technician</span>
                          <span style={{ marginLeft: 4 }}>• verified case</span>
                        </div>
                        <button
                          className="so-btn-outline"
                          style={{ padding: '2px 6px', fontSize: 11, marginLeft: 6 }}
                          onClick={() => setExpandedId(isExpanded ? null : c.id)}
                        >
                          {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                          <span>{isExpanded ? 'Collapse' : 'Solution'}</span>
                        </button>
                      </div>
                    </div>

                    {/* Expandable Solution Detail View */}
                    {isExpanded && (
                      <div style={{
                        marginTop: 14,
                        padding: 14,
                        background: '#fafbfc',
                        border: '1px solid var(--border-base)',
                        borderRadius: 'var(--radius-xs)',
                      }}>
                        {c.error_code && (
                          <div style={{ marginBottom: 10 }}>
                            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                              Error Code
                            </div>
                            <div className="so-code-block" style={{ margin: '4px 0 0 0', padding: 8, fontSize: 12 }}>
                              <code>{c.error_code}</code>
                            </div>
                          </div>
                        )}

                        <div style={{ marginBottom: 10 }}>
                          <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                            Verified Solution (CBR Ground Truth)
                          </div>
                          <div className="so-code-block" style={{ margin: '4px 0 0 0', padding: 10, fontSize: 12.5, whiteSpace: 'pre-wrap' }}>
                            {c.verified_solution}
                          </div>
                        </div>

                        {c.source_url && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11 }}>
                            <span style={{ color: 'var(--text-muted)' }}>Documentation Source:</span>
                            <a href={c.source_url} target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                              <span>{c.source_url}</span>
                              <ExternalLink size={10} />
                            </a>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Right Sidebar (Stack Overflow Blog / Meta / Stats) */}
      <div className="so-right-sidebar">
        {/* Yellow Notice Box */}
        <div className="so-yellow-box">
          <div className="so-yellow-box-header">The Overflow Blog</div>
          <div className="so-yellow-box-content">
            <div className="so-yellow-item">
              <span>✏️</span>
              <span>Scaling Python packaging troubleshooting with Hybrid RAG</span>
            </div>
            <div className="so-yellow-item">
              <span>✏️</span>
              <span>Why structured CBR beats generic semantic search for CLI errors</span>
            </div>
          </div>
          <div className="so-yellow-box-header" style={{ borderTop: '1px solid var(--so-yellow-border)' }}>
            Featured on Meta
          </div>
          <div className="so-yellow-box-content">
            <div className="so-yellow-item">
              <span>💬</span>
              <span>ResolveAI evaluation: LLM-only vs CBR-RAG accuracy</span>
            </div>
            <div className="so-yellow-item">
              <span>💬</span>
              <span>Verified feedback retention active for technical tickets</span>
            </div>
          </div>
        </div>

        {/* CBR Metrics Card */}
        {stats && (
          <div style={{ border: '1px solid var(--border-base)', borderRadius: 'var(--radius-xs)', padding: 14 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Database size={15} color="var(--so-orange)" />
              <span>Casebase Statistics</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Total Solved Cases:</span>
                <b>{stats.total_cases}</b>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Verified Ground Truth:</span>
                <b style={{ color: 'var(--so-green)' }}>{stats.verified_cases}</b>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Indexed Tools:</span>
                <b>{Object.keys(stats.by_tool).length} ({Object.keys(stats.by_tool).join(', ')})</b>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Platforms:</span>
                <b>{Object.keys(stats.by_os).length} ({Object.keys(stats.by_os).join(', ')})</b>
              </div>
            </div>
          </div>
        )}

        {/* Collectives Box */}
        <div style={{ border: '1px solid var(--border-base)', borderRadius: 'var(--radius-xs)', padding: 14 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
            Knowledge Collectives
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span>🐍 Python & Pip</span>
              <span className="badge-green">Active</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span>🌿 Git Version Control</span>
              <span className="badge-green">Active</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span>📦 Virtual Environments</span>
              <span className="badge-green">Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
