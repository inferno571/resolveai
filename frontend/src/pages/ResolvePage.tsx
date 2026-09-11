import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Send, AlertCircle, Info, Tag, Terminal,
  Cpu, Layers, Sparkles, BookOpen, Clock
} from 'lucide-react';
import { api, type ResolveResponse } from '../api';

const COMMON_TAGS = [
  'python', 'pip', 'venv', 'git', 'windows', 'linux', 'macos', 'virtualenv', 'permission-denied', 'merge-conflict'
];

const TOOL_OPTIONS = [
  { value: '', label: 'Auto-detect tool' },
  { value: 'python', label: 'python' },
  { value: 'pip', label: 'pip' },
  { value: 'venv', label: 'venv / virtualenv' },
  { value: 'git', label: 'git' },
];

const OS_OPTIONS = [
  { value: '', label: 'Auto-detect OS' },
  { value: 'windows', label: 'windows' },
  { value: 'linux', label: 'linux' },
  { value: 'macos', label: 'macos' },
];

export function ResolvePage() {
  const navigate = useNavigate();
  const [problem, setProblem] = useState('');
  const [tool, setTool] = useState('');
  const [os, setOs] = useState('');
  const [version, setVersion] = useState('');
  const [errorLog, setErrorLog] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [mode, setMode] = useState('full');
  const [provider, setProvider] = useState('gemini');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const toggleTag = (tagName: string) => {
    if (selectedTags.includes(tagName)) {
      setSelectedTags(selectedTags.filter(t => t !== tagName));
    } else {
      setSelectedTags([...selectedTags, tagName]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!problem.trim() || problem.trim().length < 8) {
      setError('Please enter a specific problem description (at least 8 characters).');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response: ResolveResponse = await api.resolve(
        {
          problem: problem.trim(),
          tool: tool || undefined,
          operating_system: os || undefined,
          version: version || undefined,
          error_log: errorLog.trim() || undefined,
        },
        mode,
        provider
      );

      // Navigate to resolution page with the returned data
      navigate(`/resolve/${response.query_id}`, { state: { response, queryInput: { problem, tool, os, version, errorLog, tags: selectedTags } } });
    } catch (err: any) {
      setError(err.message || 'Failed to resolve. Make sure the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', gap: 24 }}>
      {/* Left / Main Question Formulation Form */}
      <div style={{ flex: 1, minWidth: 0 }}>
        {/* Title Header */}
        <div style={{ marginBottom: 20 }}>
          <h1 style={{ fontSize: 24, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>
            Ask a Troubleshooting Question
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
            ResolveAI searches authoritative manuals (RAG) and past solved tickets (CBR) to generate an explainable, cited resolution.
          </p>
        </div>

        {/* Stack Overflow Style Guidance Box */}
        <div className="so-guidance-box">
          <div className="so-guidance-title">
            <Info size={18} />
            <span>Writing a good troubleshooting request</span>
          </div>
          <ul className="so-guidance-list">
            <li><b>Summarize your problem</b> with clear symptoms and tool context in the title or description.</li>
            <li><b>Specify your environment</b> (e.g. Python 3.12 on Windows 11) for accurate CBR case similarity.</li>
            <li><b>Paste the exact error traceback</b> or terminal log snippet into the error log field.</li>
            <li><b>Tag relevant technologies</b> so ResolveAI can load focused documentation passages.</li>
          </ul>
        </div>

        {/* Ask Form */}
        <form onSubmit={handleSubmit}>
          {/* Card 1: Problem Title / Summary */}
          <div className="so-ask-card">
            <label className="so-ask-label">Title / Problem Summary *</label>
            <div className="so-ask-desc">
              Be specific and imagine you're asking a fellow engineer (e.g., "pip install fails with 'Permission denied' error when installing packages globally").
            </div>
            <input
              type="text"
              className="so-input"
              placeholder="e.g., ModuleNotFoundError: No module named 'numpy' even though pip install succeeded"
              value={problem}
              onChange={(e) => setProblem(e.target.value)}
            />
          </div>

          {/* Card 2: Environment Details */}
          <div className="so-ask-card">
            <label className="so-ask-label">Environment & Platform</label>
            <div className="so-ask-desc">
              Specifying your tool and OS enables exact CBR structured case matching.
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>
                  Tool
                </label>
                <select
                  className="so-input"
                  value={tool}
                  onChange={(e) => setTool(e.target.value)}
                >
                  {TOOL_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>
                  Operating System
                </label>
                <select
                  className="so-input"
                  value={os}
                  onChange={(e) => setOs(e.target.value)}
                >
                  {OS_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>
                  Version (Optional)
                </label>
                <input
                  type="text"
                  className="so-input"
                  placeholder="e.g., 3.12 or 2.40"
                  value={version}
                  onChange={(e) => setVersion(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Card 3: Error Traceback / Terminal Logs */}
          <div className="so-ask-card">
            <label className="so-ask-label">
              <Terminal size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }} />
              Terminal Traceback / Error Log (Optional)
            </label>
            <div className="so-ask-desc">
              Paste console output, stack traces, or terminal logs. We extract error codes for BM25 & CBR lexical search.
            </div>
            <textarea
              className="so-textarea so-textarea-code"
              rows={5}
              placeholder="Paste raw error message or traceback here:
PermissionError: [Errno 13] Permission denied: 'C:\\Python312\\Lib\\site-packages\\numpy'"
              value={errorLog}
              onChange={(e) => setErrorLog(e.target.value)}
            />
          </div>

          {/* Card 4: Tags */}
          <div className="so-ask-card">
            <label className="so-ask-label">
              <Tag size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }} />
              Tags
            </label>
            <div className="so-ask-desc">
              Select or toggle tags to describe what your issue is about:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
              {COMMON_TAGS.map(t => {
                const isActive = selectedTags.includes(t);
                return (
                  <button
                    type="button"
                    key={t}
                    onClick={() => toggleTag(t)}
                    className={`so-tag ${isActive ? 'so-tag-active' : ''}`}
                  >
                    {isActive ? `✓ ${t}` : t}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Card 5: Retrieval Mode & LLM Provider */}
          <div className="so-ask-card" style={{ background: '#fafbfc' }}>
            <label className="so-ask-label">
              <Cpu size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }} />
              Troubleshooting Engine & Model
            </label>
            <div className="so-ask-desc">
              Select the hybrid retrieval pipeline configuration:
            </div>
            
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginRight: 6 }}>
                  Pipeline:
                </span>
                <div className="so-filter-group" style={{ verticalAlign: 'middle' }}>
                  <button
                    type="button"
                    className={`so-filter-btn ${mode === 'full' ? 'active' : ''}`}
                    onClick={() => setMode('full')}
                  >
                    Hybrid (RAG + CBR)
                  </button>
                  <button
                    type="button"
                    className={`so-filter-btn ${mode === 'rag_only' ? 'active' : ''}`}
                    onClick={() => setMode('rag_only')}
                  >
                    RAG Only
                  </button>
                  <button
                    type="button"
                    className={`so-filter-btn ${mode === 'cbr_only' ? 'active' : ''}`}
                    onClick={() => setMode('cbr_only')}
                  >
                    CBR Only
                  </button>
                  <button
                    type="button"
                    className={`so-filter-btn ${mode === 'llm_only' ? 'active' : ''}`}
                    onClick={() => setMode('llm_only')}
                  >
                    LLM Baseline
                  </button>
                </div>
              </div>

              <div>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginRight: 6 }}>
                  LLM:
                </span>
                <div className="so-filter-group" style={{ verticalAlign: 'middle' }}>
                  <button
                    type="button"
                    className={`so-filter-btn ${provider === 'gemini' ? 'active' : ''}`}
                    onClick={() => setProvider('gemini')}
                  >
                    Gemini 3.8 Flash
                  </button>
                  <button
                    type="button"
                    className={`so-filter-btn ${provider === 'ollama' ? 'active' : ''}`}
                    onClick={() => setProvider('ollama')}
                  >
                    Ollama Local
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div style={{
              padding: '10px 14px',
              backgroundColor: 'var(--so-red-light)',
              border: '1px solid var(--so-red-border)',
              color: 'var(--so-red)',
              borderRadius: 'var(--radius-xs)',
              marginBottom: 16,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: 13,
            }}>
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          {/* Submit Button */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 20 }}>
            <button
              type="submit"
              className="so-btn-primary"
              style={{ padding: '10px 18px', fontSize: 14 }}
              disabled={loading || problem.trim().length < 8}
            >
              {loading ? (
                <>
                  <div className="spinner" />
                  <span>Retrieving Evidence & Generating Solution...</span>
                </>
              ) : (
                <>
                  <Send size={15} />
                  <span>Post Your Question / Get Resolution</span>
                </>
              )}
            </button>

            <button
              type="button"
              className="so-btn-outline"
              onClick={() => {
                setProblem("pip install fails with 'Permission denied' error when installing packages globally");
                setTool("pip");
                setOs("windows");
                setErrorLog("PermissionError: [Errno 13] Permission denied: 'C:\\Python312\\Lib\\site-packages\\numpy'");
                setSelectedTags(["pip", "windows", "permission-denied"]);
              }}
            >
              Load Example Issue
            </button>
          </div>
        </form>
      </div>

      {/* Right Sidebar (Stack Overflow Style) */}
      <div className="so-right-sidebar">
        {/* Yellow Box: The Overflow Blog / Guide */}
        <div className="so-yellow-box">
          <div className="so-yellow-box-header">The ResolveAI Guide</div>
          <div className="so-yellow-box-content">
            <div className="so-yellow-item">
              <Layers size={14} />
              <span><b>Hybrid RAG:</b> Retrieves official documentation passages from indexed manuals.</span>
            </div>
            <div className="so-yellow-item">
              <Sparkles size={14} />
              <span><b>CBR Casebase:</b> Calculates multi-field similarity across problem, evidence, and OS.</span>
            </div>
            <div className="so-yellow-item">
              <BookOpen size={14} />
              <span><b>Explainable Citations:</b> Every solution provides exact documentation provenance.</span>
            </div>
          </div>
        </div>

        {/* Info Card: Agentic RAG Knowledge */}
        <div className="so-promo-card">
          <div className="so-promo-title">Verified Knowledge Base</div>
          <div className="so-promo-subtitle">
            20 preloaded technical troubleshooting cases ready for semantic similarity search.
          </div>
          <div className="so-promo-code">
            BAAI/bge-small-en-v1.5<br />
            ChromaDB + SQLite FTS5<br />
            Gemini 3.8 Flash Connected
          </div>
        </div>

        {/* Quick Tips */}
        <div style={{ border: '1px solid var(--border-base)', borderRadius: 'var(--radius-xs)', padding: 14 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <Clock size={14} />
            <span>Recent Solved Topics</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ fontSize: 12, color: 'var(--so-link)' }}>
              • pip global install permission errors
            </div>
            <div style={{ fontSize: 12, color: 'var(--so-link)' }}>
              • Python version mismatch in venv
            </div>
            <div style={{ fontSize: 12, color: 'var(--so-link)' }}>
              • Git fatal: refusing to merge unrelated histories
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
