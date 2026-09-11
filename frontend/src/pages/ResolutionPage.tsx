import { useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import {
  ArrowLeft, Copy, Check, AlertTriangle, BookOpen, Layers,
  ThumbsUp, ThumbsDown, ChevronDown, ChevronUp, ExternalLink,
  CheckCircle2, Share2, Bookmark
} from 'lucide-react';
import { api, type ResolveResponse, type CaseSimilarityResult } from '../api';

export function ResolutionPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [copiedStep, setCopiedStep] = useState<number | null>(null);
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [showCitations, setShowCitations] = useState(true);
  const [showCases, setShowCases] = useState(true);
  const [votes, setVotes] = useState(1);
  const [hasVoted, setHasVoted] = useState(false);
  const [correctionText, setCorrectionText] = useState('');
  const [showCorrectionForm, setShowCorrectionForm] = useState(false);

  const response: ResolveResponse | undefined = location.state?.response;
  const queryInput = location.state?.queryInput;

  if (!response) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <h2 style={{ fontSize: 20, color: 'var(--text-primary)', marginBottom: 8 }}>
          Resolution Session Not Found
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
          This resolution session may have expired or was loaded without submitting an issue.
        </p>
        <button className="so-btn-primary" onClick={() => navigate('/')}>
          <ArrowLeft size={14} />
          <span>Ask a New Troubleshooting Question</span>
        </button>
      </div>
    );
  }

  const copyCode = (code: string, stepNum: number) => {
    navigator.clipboard.writeText(code);
    setCopiedStep(stepNum);
    setTimeout(() => setCopiedStep(null), 2000);
  };

  const handleVote = async (delta: number) => {
    if (hasVoted) return;
    setVotes(prev => prev + delta);
    setHasVoted(true);
    try {
      await api.submitFeedback({
        query_id: response.query_id,
        resolved: delta > 0,
        rating: delta > 0 ? 5 : 2,
      });
    } catch (err) {
      console.error('Failed to submit vote feedback:', err);
    }
  };

  const handleFeedbackSubmit = async (resolved: boolean) => {
    setFeedbackLoading(true);
    try {
      await api.submitFeedback({
        query_id: response.query_id,
        resolved,
        rating: resolved ? 5 : 1,
        corrected_solution: correctionText.trim() || undefined,
      });
      setFeedbackSent(true);
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    } finally {
      setFeedbackLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', gap: 24 }}>
      {/* Main Question & Solution Column */}
      <div style={{ flex: 1, minWidth: 0 }}>
        {/* Question Header */}
        <div style={{ borderBottom: '1px solid var(--border-base)', paddingBottom: 12, marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
            <h1 style={{ fontSize: 22, fontWeight: 500, color: 'var(--text-primary)', lineHeight: 1.3 }}>
              {queryInput?.problem || response.diagnosis}
            </h1>
            <button
              onClick={() => navigate('/')}
              className="so-btn-primary"
              style={{ flexShrink: 0, padding: '7px 12px', fontSize: 12 }}
            >
              Ask Question
            </button>
          </div>

          <div style={{ display: 'flex', gap: 16, marginTop: 8, fontSize: 12, color: 'var(--text-muted)', flexWrap: 'wrap' }}>
            <span>Asked <b>today</b></span>
            <span>Modified <b>today</b></span>
            <span>Viewed <b>1 time</b></span>
            <span>Engine: <b>{response.llm_provider_used === 'gemini' ? 'Gemini 3.8 Flash' : response.llm_provider_used}</b></span>
            <span>Confidence: <b>{response.confidence.toUpperCase()}</b></span>
          </div>
        </div>

        {/* Question Post (The Problem Details) */}
        <div className="so-post-container" style={{ borderBottom: '1px solid var(--border-base)', paddingBottom: 24 }}>
          {/* Left Voting Column */}
          <div className="so-voting-column">
            <button className="so-vote-btn" onClick={() => setVotes(v => v + 1)} title="This question shows research effort">
              ▲
            </button>
            <span className="so-vote-count">1</span>
            <button className="so-vote-btn" onClick={() => setVotes(v => Math.max(0, v - 1))} title="This question does not show research effort">
              ▼
            </button>
            <Bookmark size={18} style={{ color: 'var(--text-muted)', cursor: 'pointer', marginTop: 8 }} />
            <Share2 size={16} style={{ color: 'var(--text-muted)', cursor: 'pointer', marginTop: 4 }} />
          </div>

          {/* Question Body */}
          <div className="so-post-body">
            <p style={{ marginBottom: 12 }}>
              {queryInput?.problem || 'Technical issue diagnosed below with hybrid RAG + CBR verification.'}
            </p>

            {queryInput?.errorLog && (
              <div>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4 }}>
                  Terminal Traceback / Error Log:
                </div>
                <div className="so-code-block">
                  <pre>{queryInput.errorLog}</pre>
                </div>
              </div>
            )}

            {/* Tags */}
            <div className="so-question-meta-row" style={{ marginTop: 16 }}>
              <div className="so-question-tags">
                {queryInput?.tool && <span className="so-tag">{queryInput.tool}</span>}
                {queryInput?.os && <span className="so-tag">{queryInput.os}</span>}
                {queryInput?.version && <span className="so-tag">v{queryInput.version}</span>}
                {queryInput?.tags?.map((t: string) => (
                  <span key={t} className="so-tag">{t}</span>
                ))}
              </div>

              <div className="so-user-card" style={{ background: '#f8f9fa', padding: '6px 10px', borderRadius: 3, border: '1px solid var(--border-base)' }}>
                <div className="so-avatar">D</div>
                <div>
                  <div style={{ color: 'var(--so-link)', fontWeight: 500 }}>Developer</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>asked just now</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Answers Divider */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '24px 0 16px 0' }}>
          <h2 style={{ fontSize: 18, fontWeight: 500, color: 'var(--text-primary)' }}>
            1 Answer (Hybrid RAG + CBR Verified)
          </h2>
          <div className="so-filter-group">
            <button className="so-filter-btn active">Active</button>
            <button className="so-filter-btn">Oldest</button>
            <button className="so-filter-btn">Votes</button>
          </div>
        </div>

        {/* Accepted Solution Post */}
        <div className="so-post-container" style={{ borderBottom: '1px solid var(--border-base)', paddingBottom: 24 }}>
          {/* Left Voting Column with Green Accepted Check */}
          <div className="so-voting-column">
            <button className="so-vote-btn" onClick={() => handleVote(1)} title="This answer is useful">
              ▲
            </button>
            <span className="so-vote-count">{votes}</span>
            <button className="so-vote-btn" onClick={() => handleVote(-1)} title="This answer is not useful">
              ▼
            </button>
            <span title="Accepted and verified by CBR + RAG">
              <CheckCircle2 size={32} className="so-accepted-check" />
            </span>
          </div>

          {/* Solution Body */}
          <div className="so-post-body">
            {/* Accepted Answer Badge Header */}
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              background: 'var(--so-green-light)',
              border: '1px solid var(--so-green-border)',
              color: 'var(--so-green)',
              padding: '4px 10px',
              borderRadius: 'var(--radius-xs)',
              fontSize: 12,
              fontWeight: 600,
              marginBottom: 16,
            }}>
              <Check size={14} />
              <span>Accepted Solution • Confidence: {response.confidence.toUpperCase()}</span>
            </div>

            {/* Diagnosis Summary Card */}
            <div style={{
              background: '#fcfcfc',
              border: '1px solid var(--border-base)',
              borderLeft: '4px solid var(--so-blue)',
              borderRadius: 'var(--radius-xs)',
              padding: '12px 16px',
              marginBottom: 18,
            }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--so-blue-hover)', textTransform: 'uppercase', marginBottom: 4 }}>
                Diagnosis & Root Cause
              </div>
              <p style={{ fontSize: 13.5, color: 'var(--text-primary)', lineHeight: 1.5 }}>
                {response.diagnosis}
              </p>
            </div>

            {/* Step by Step Instructions */}
            <div style={{ marginBottom: 20 }}>
              <h3 style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 12 }}>
                Resolution Steps:
              </h3>

              {response.steps.map((step) => (
                <div
                  key={step.step_number}
                  style={{
                    marginBottom: 16,
                    padding: '12px 14px',
                    border: '1px solid var(--border-base)',
                    borderRadius: 'var(--radius-xs)',
                    background: '#ffffff',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                    <span style={{
                      width: 22,
                      height: 22,
                      borderRadius: 2,
                      background: 'var(--so-tag-bg)',
                      color: 'var(--so-tag-color)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 700,
                      fontSize: 11,
                      flexShrink: 0,
                    }}>
                      {step.step_number}
                    </span>
                    <div style={{ flex: 1 }}>
                      <p style={{ fontSize: 13, color: 'var(--text-primary)', marginBottom: step.code ? 8 : 0 }}>
                        {step.instruction}
                      </p>

                      {step.code && (
                        <div className="so-code-block" style={{ margin: '8px 0 0 0' }}>
                          <pre>{step.code}</pre>
                          <button
                            className="so-copy-btn"
                            onClick={() => copyCode(step.code!, step.step_number)}
                          >
                            {copiedStep === step.step_number ? (
                              <>
                                <Check size={11} color="var(--so-green)" />
                                <span>Copied!</span>
                              </>
                            ) : (
                              <>
                                <Copy size={11} />
                                <span>Copy</span>
                              </>
                            )}
                          </button>
                        </div>
                      )}

                      {step.warning && (
                        <div style={{
                          marginTop: 8,
                          padding: '6px 10px',
                          background: 'var(--so-yellow)',
                          border: '1px solid var(--so-yellow-border)',
                          borderRadius: 'var(--radius-xs)',
                          fontSize: 12,
                          color: '#6d4c41',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 6,
                        }}>
                          <AlertTriangle size={13} />
                          <span><b>Warning:</b> {step.warning}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Warnings Callout */}
            {response.warnings && response.warnings.length > 0 && (
              <div style={{
                background: 'var(--so-yellow)',
                border: '1px solid var(--so-yellow-border)',
                borderRadius: 'var(--radius-xs)',
                padding: '12px 14px',
                marginBottom: 20,
              }}>
                <div style={{ fontWeight: 600, color: '#795548', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <AlertTriangle size={15} />
                  <span>Important Considerations & Warnings</span>
                </div>
                <ul style={{ paddingLeft: 18, fontSize: 12.5, color: '#5d4037', lineHeight: 1.5 }}>
                  {response.warnings.map((w, idx) => (
                    <li key={idx}>{w}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Citations & Evidence Section (RAG) */}
            {response.citations && response.citations.length > 0 && (
              <div style={{ border: '1px solid var(--border-base)', borderRadius: 'var(--radius-xs)', marginBottom: 20 }}>
                <div
                  onClick={() => setShowCitations(!showCitations)}
                  style={{
                    padding: '10px 14px',
                    background: '#f8f9fa',
                    borderBottom: showCitations ? '1px solid var(--border-base)' : 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 600, fontSize: 13 }}>
                    <BookOpen size={16} color="var(--so-link)" />
                    <span>Official Documentation Citations ({response.citations.length} sources)</span>
                  </div>
                  {showCitations ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>

                {showCitations && (
                  <div style={{ padding: 14 }}>
                    {response.citations.map((cite, idx) => (
                      <div key={idx} style={{ marginBottom: 12, paddingBottom: 12, borderBottom: idx < response.citations.length - 1 ? '1px solid var(--border-light)' : 'none' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                          <span style={{ fontWeight: 600, fontSize: 12.5, color: 'var(--so-link)' }}>
                            {cite.title || cite.source}
                          </span>
                          {cite.url && (
                            <a href={cite.url} target="_blank" rel="noreferrer" style={{ fontSize: 11, display: 'flex', alignItems: 'center', gap: 4 }}>
                              <span>Official Docs</span>
                              <ExternalLink size={11} />
                            </a>
                          )}
                        </div>
                        <p style={{ fontSize: 12, color: 'var(--text-secondary)', background: '#fafbfc', padding: '6px 10px', borderRadius: 3, border: '1px solid var(--border-light)' }}>
                          "{cite.relevant_text}"
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* User Feedback & Revision Box */}
            <div style={{
              background: '#f8f9fa',
              border: '1px solid var(--border-base)',
              borderRadius: 'var(--radius-xs)',
              padding: '16px 20px',
              marginTop: 24,
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
                    Did this answer solve your technical issue?
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Verified solutions are retained in the CBR casebase for future matching.
                  </div>
                </div>

                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    className="so-btn-primary"
                    style={{ padding: '6px 14px', fontSize: 12 }}
                    onClick={() => handleFeedbackSubmit(true)}
                    disabled={feedbackLoading || feedbackSent}
                  >
                    <ThumbsUp size={13} />
                    <span>Yes, Resolved</span>
                  </button>

                  <button
                    className="so-btn-outline"
                    onClick={() => handleFeedbackSubmit(false)}
                    disabled={feedbackLoading || feedbackSent}
                  >
                    <ThumbsDown size={13} />
                    <span>No, Need Help</span>
                  </button>

                  <button
                    className="so-btn-outline"
                    onClick={() => setShowCorrectionForm(!showCorrectionForm)}
                  >
                    Suggest Edit
                  </button>
                </div>
              </div>

              {feedbackSent && (
                <div style={{ marginTop: 12, color: 'var(--so-green)', fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Check size={14} />
                  <span>Thank you! Your feedback has been saved for future CBR retention.</span>
                </div>
              )}

              {showCorrectionForm && (
                <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--border-base)' }}>
                  <label style={{ fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 4 }}>
                    Submit Corrected / Adapted Solution for Casebase:
                  </label>
                  <textarea
                    className="so-textarea"
                    rows={3}
                    placeholder="Enter the commands or solution that worked in your environment..."
                    value={correctionText}
                    onChange={(e) => setCorrectionText(e.target.value)}
                  />
                  <div style={{ marginTop: 8 }}>
                    <button
                      className="so-btn-primary"
                      onClick={() => handleFeedbackSubmit(true)}
                      disabled={!correctionText.trim() || feedbackLoading}
                    >
                      Save to CBR Casebase
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Right Sidebar: CBR Similar Cases (Related Questions) */}
      <div className="so-right-sidebar">
        {/* Similar Cases Card (Stack Overflow Related Questions style) */}
        <div style={{ border: '1px solid var(--border-base)', borderRadius: 'var(--radius-xs)', overflow: 'hidden' }}>
          <div
            onClick={() => setShowCases(!showCases)}
            style={{
              background: '#f8f9fa',
              padding: '10px 12px',
              borderBottom: '1px solid var(--border-base)',
              fontSize: 13,
              fontWeight: 700,
              color: 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Layers size={14} color="var(--so-orange)" />
              <span>Related Solved Cases ({response.similar_cases?.length || 0})</span>
            </div>
            {showCases ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </div>

          {showCases && (
            <div style={{ padding: 12, display: 'flex', flexDirection: 'column', gap: 12 }}>
              {(!response.similar_cases || response.similar_cases.length === 0) ? (
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  No previous cases exceeded the similarity threshold.
                </div>
              ) : (
                response.similar_cases.map((sim: CaseSimilarityResult, index: number) => (
                  <div key={index} style={{ borderBottom: index < response.similar_cases.length - 1 ? '1px solid var(--border-light)' : 'none', paddingBottom: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                      <span className="badge-green">
                        {(sim.total_score * 100).toFixed(0)}% match
                      </span>
                      {sim.case.tool && <span className="so-tag">{sim.case.tool}</span>}
                    </div>
                    <div style={{ fontSize: 12.5, color: 'var(--so-link)', fontWeight: 500, lineHeight: 1.35, marginBottom: 4 }}>
                      {sim.case.problem.length > 80 ? sim.case.problem.slice(0, 80) + '...' : sim.case.problem}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                      {sim.match_explanation}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Knowledge Source Details Box */}
        <div className="so-yellow-box">
          <div className="so-yellow-box-header">Retrieval Metadata</div>
          <div className="so-yellow-box-content">
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
              <span>RAG Chunks Retrieved:</span>
              <b>{response.retrieval_metadata?.rag_chunks_retrieved ?? 0}</b>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
              <span>CBR Cases Matched:</span>
              <b>{response.similar_cases?.length ?? 0}</b>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Dual LLM Provider:</span>
              <b>{response.llm_provider_used === 'gemini' ? 'Gemini 3.8 Flash (latest)' : response.llm_provider_used}</b>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
