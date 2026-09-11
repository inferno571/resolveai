import { useEffect, useState } from 'react';
import {
  Settings, Activity, Brain, FileText,
  RefreshCw, Trash2, Check, Sliders, Zap, TestTube
} from 'lucide-react';
import { api, type HealthStatus, type SystemMetrics, type DocumentMeta } from '../api';

function HealthCard({ health }: { health: HealthStatus }) {
  return (
    <div style={{ background: '#ffffff', border: '1px solid var(--border-base)', borderRadius: 'var(--radius-xs)', padding: 18 }}>
      <h3 style={{ fontSize: 15, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
        <Activity size={17} color="var(--so-green)" />
        System & Model Health
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="so-status-dot" style={{ background: health.ollama_model_loaded ? 'var(--so-green)' : health.ollama_connected ? 'var(--so-orange)' : 'var(--so-red)' }} />
          <div>
            <div style={{ fontSize: 13, fontWeight: 500 }}>Ollama Local</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              {health.ollama_model_loaded ? 'Model loaded' : health.ollama_connected ? 'Connected' : 'Offline'}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="so-status-dot" style={{ background: health.gemini_configured ? 'var(--so-green)' : 'var(--so-orange)' }} />
          <div>
            <div style={{ fontSize: 13, fontWeight: 500 }}>Gemini Flash API</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              {health.gemini_configured ? 'Configured & Active' : 'No API key'}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="so-status-dot" />
          <div>
            <div style={{ fontSize: 13, fontWeight: 500 }}>RAG Vector Index</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              {health.chroma_documents} chunks in ChromaDB
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="so-status-dot" />
          <div>
            <div style={{ fontSize: 13, fontWeight: 500 }}>CBR Casebase</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              {health.casebase_size} verified cases in SQLite
            </div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 14, padding: '6px 10px', borderRadius: 'var(--radius-xs)', background: '#f8f9fa', border: '1px solid var(--border-base)', fontSize: 11 }}>
        <span style={{ color: 'var(--text-muted)' }}>Active Embedding Model: </span>
        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{health.embedding_model}</span>
      </div>
    </div>
  );
}

export function AdminPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [documents, setDocuments] = useState<DocumentMeta[]>([]);
  const [loading, setLoading] = useState(true);

  // LLM test
  const [testProvider, setTestProvider] = useState('gemini');
  const [testResult, setTestResult] = useState<string | null>(null);
  const [testLoading, setTestLoading] = useState(false);

  // Config editing
  const [editProvider, setEditProvider] = useState('gemini');
  const [editWeights, setEditWeights] = useState({ problem: 0.4, evidence: 0.25, entity: 0.2, environment: 0.15 });
  const [configSaved, setConfigSaved] = useState(false);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [h, m, c, d] = await Promise.all([
        api.getHealth(),
        api.getMetrics(),
        api.getConfig(),
        api.getDocuments(),
      ]);
      setHealth(h);
      setMetrics(m);
      setDocuments(d);
      if (c && typeof c === 'object') {
        if (c.llm_provider) setEditProvider(c.llm_provider);
        if (c.cbr_weights) setEditWeights(c.cbr_weights);
      }
    } catch (err) {
      console.error('Failed to load admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTestLLM = async () => {
    setTestLoading(true);
    setTestResult(null);
    try {
      const result = await api.testLLM(testProvider);
      if (result.status === 'success') {
        setTestResult(`✓ ${result.model}: "${result.response}" (${result.latency_ms}ms)`);
      } else {
        setTestResult(`✗ Error: ${result.error}`);
      }
    } catch (err: any) {
      setTestResult(`✗ ${err.message}`);
    } finally {
      setTestLoading(false);
    }
  };

  const handleSaveConfig = async () => {
    try {
      await api.updateConfig({
        llm_provider: editProvider,
        cbr_weight_problem: editWeights.problem,
        cbr_weight_evidence: editWeights.evidence,
        cbr_weight_entity: editWeights.entity,
        cbr_weight_environment: editWeights.environment,
      });
      setConfigSaved(true);
      setTimeout(() => setConfigSaved(false), 3000);
      loadAll();
    } catch (err) {
      console.error('Config save failed:', err);
    }
  };

  const handleDeleteDoc = async (id: string) => {
    try {
      await api.deleteDocument(id);
      setDocuments(documents.filter(d => d.id !== id));
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <div className="spinner" style={{ margin: '0 auto 12px auto', borderTopColor: 'var(--so-blue)' }} />
        <div style={{ color: 'var(--text-muted)' }}>Loading system configuration & health metrics...</div>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 24, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Settings size={22} color="var(--so-orange)" />
          System Administration & Settings
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
          Monitor system health, inspect CBR retrieval weights, test LLM inference latency, and manage RAG documents.
        </p>
      </div>

      {/* Top Grid: Health + Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        {health && <HealthCard health={health} />}

        {metrics && (
          <div style={{ background: '#ffffff', border: '1px solid var(--border-base)', borderRadius: 'var(--radius-xs)', padding: 18 }}>
            <h3 style={{ fontSize: 15, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <Zap size={17} color="var(--so-orange)" />
              System Troubleshooting Metrics
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, textAlign: 'center' }}>
              <div style={{ background: '#f8f9fa', padding: 10, borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-base)' }}>
                <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--so-blue)' }}>
                  {metrics.total_queries}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Total Queries</div>
              </div>

              <div style={{ background: '#f8f9fa', padding: 10, borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-base)' }}>
                <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--so-green)' }}>
                  {(metrics.positive_feedback_rate * 100).toFixed(0)}%
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Resolution Rate</div>
              </div>

              <div style={{ background: '#f8f9fa', padding: 10, borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-base)' }}>
                <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--so-orange)' }}>
                  {metrics.avg_rating > 0 ? `${metrics.avg_rating}★` : '5.0★'}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Avg Rating</div>
              </div>
            </div>

            {Object.keys(metrics.cases_by_tool).length > 0 && (
              <div style={{ marginTop: 14, paddingTop: 10, borderTop: '1px solid var(--border-base)' }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6 }}>
                  Indexed Cases by Tool
                </div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {Object.entries(metrics.cases_by_tool).map(([tool, count]) => (
                    <span key={tool} className="so-tag">{tool}: {count}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Middle Grid: LLM Config & CBR Weights */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        {/* LLM Provider Card */}
        <div style={{ background: '#ffffff', border: '1px solid var(--border-base)', borderRadius: 'var(--radius-xs)', padding: 18 }}>
          <h3 style={{ fontSize: 15, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <Brain size={17} color="var(--so-blue)" />
            LLM Provider & Test Console
          </h3>

          <div style={{ marginBottom: 14 }}>
            <label style={{ fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 4 }}>
              Active Primary Provider:
            </label>
            <select
              className="so-input"
              value={editProvider}
              onChange={(e) => setEditProvider(e.target.value)}
            >
              <option value="gemini">Google Gemini 3.8 Flash (gemini-flash-latest)</option>
              <option value="ollama">Ollama Qwen3 4B (Local)</option>
            </select>
          </div>

          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 12 }}>
            <select
              className="so-input"
              style={{ width: 140 }}
              value={testProvider}
              onChange={(e) => setTestProvider(e.target.value)}
            >
              <option value="gemini">Gemini</option>
              <option value="ollama">Ollama</option>
            </select>
            <button
              className="so-btn-outline"
              onClick={handleTestLLM}
              disabled={testLoading}
            >
              <TestTube size={13} />
              <span>{testLoading ? 'Testing...' : 'Test Connection'}</span>
            </button>
          </div>

          {testResult && (
            <div style={{
              padding: '8px 12px',
              borderRadius: 'var(--radius-xs)',
              background: testResult.startsWith('✓') ? 'var(--so-green-light)' : 'var(--so-red-light)',
              border: `1px solid ${testResult.startsWith('✓') ? 'var(--so-green-border)' : 'var(--so-red-border)'}`,
              color: testResult.startsWith('✓') ? 'var(--so-green)' : 'var(--so-red)',
              fontSize: 12,
              wordBreak: 'break-word',
            }}>
              {testResult}
            </div>
          )}
        </div>

        {/* CBR Similarity Weights Card */}
        <div style={{ background: '#ffffff', border: '1px solid var(--border-base)', borderRadius: 'var(--radius-xs)', padding: 18 }}>
          <h3 style={{ fontSize: 15, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <Sliders size={17} color="var(--so-orange)" />
            CBR Multi-Field Similarity Weights
          </h3>
          <p style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 12 }}>
            Formula: w_p * Sim(Problem) + w_ev * Sim(Evidence) + w_ent * Overlap(Entity) + w_env * Match(Env) = 1.0
          </p>

          {Object.entries(editWeights).map(([key, val]) => (
            <div key={key} style={{ marginBottom: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                <span style={{ fontSize: 12, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{key} Weight</span>
                <span style={{ fontSize: 12, fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{val.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={val}
                onChange={(e) => setEditWeights({ ...editWeights, [key]: parseFloat(e.target.value) })}
                style={{ width: '100%', accentColor: 'var(--so-orange)' }}
              />
            </div>
          ))}

          <div style={{
            fontSize: 12,
            fontFamily: 'var(--font-mono)',
            fontWeight: 600,
            color: Math.abs(Object.values(editWeights).reduce((a, b) => a + b, 0) - 1.0) < 0.01 ? 'var(--so-green)' : 'var(--so-red)',
            marginTop: 4,
          }}>
            Total Sum: {Object.values(editWeights).reduce((a, b) => a + b, 0).toFixed(2)} (Must equal 1.0)
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <button
          className="so-btn-primary"
          style={{ padding: '8px 24px', fontSize: 13 }}
          onClick={handleSaveConfig}
        >
          {configSaved ? (
            <>
              <Check size={15} />
              <span>Configuration Updated Successfully!</span>
            </>
          ) : (
            <>
              <RefreshCw size={15} />
              <span>Save System Configuration</span>
            </>
          )}
        </button>
      </div>

      {/* Ingested RAG Documents */}
      <div style={{ background: '#ffffff', border: '1px solid var(--border-base)', borderRadius: 'var(--radius-xs)', padding: 18 }}>
        <h3 style={{ fontSize: 15, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
          <FileText size={17} color="var(--so-blue)" />
          Indexed RAG Manuals & Documentation ({documents.length})
        </h3>

        {documents.length === 0 ? (
          <div style={{ color: 'var(--text-muted)', fontSize: 12.5, padding: '12px 0' }}>
            No documentation manuals currently indexed. RAG seed loader can ingest official manuals into ChromaDB.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {documents.map(doc => (
              <div
                key={doc.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-xs)',
                  background: '#f8f9fa',
                  border: '1px solid var(--border-base)',
                }}
              >
                <div>
                  <div style={{ fontWeight: 500, fontSize: 13, color: 'var(--so-link)' }}>{doc.title}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    Source: {doc.source} · {doc.chunk_count} passages indexed
                  </div>
                </div>
                <button
                  className="so-btn-outline"
                  onClick={() => handleDeleteDoc(doc.id)}
                  style={{ color: 'var(--so-red)', borderColor: 'var(--so-red-border)' }}
                >
                  <Trash2 size={13} />
                  <span>Remove</span>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
