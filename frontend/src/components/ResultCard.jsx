import React from 'react';
import { CheckCircle2, HelpCircle, AlertOctagon, AlertTriangle, BookOpen, ShieldCheck, FileText, Check } from 'lucide-react';

export default function ResultCard({ armName, action, resultData, isLoading }) {
  if (isLoading) {
    return (
      <div className="glass-panel" style={{ padding: '32px', textAlign: 'center' }}>
        <div style={{
          width: '36px',
          height: '36px',
          margin: '0 auto 16px auto',
          border: '3px solid rgba(16, 185, 129, 0.2)',
          borderTopColor: '#10b981',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', fontWeight: 600 }}>Executing Clinical Decision Analysis ({armName})...</p>
        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (!resultData) {
    return (
      <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
        Click <strong>"Run Decision Support Analysis"</strong> to execute pipeline reasoning.
      </div>
    );
  }

  const {
    action: resultAction = action || 'ANSWER',
    answer = '',
    missing_information = [],
    safety_message = '',
    citations = [],
    rules = []
  } = resultData;

  const getActionIcon = (act) => {
    switch (act) {
      case 'ANSWER': return <CheckCircle2 size={18} />;
      case 'ASK': return <HelpCircle size={18} />;
      case 'ABSTAIN': return <AlertTriangle size={18} />;
      case 'ESCALATE': return <AlertOctagon size={18} />;
      default: return null;
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Arm Header & Action Badge */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#06b6d4', letterSpacing: '1px', textTransform: 'uppercase' }}>
            Pipeline Output
          </span>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc' }}>{armName}</h3>
        </div>

        <div className={`badge-action badge-${resultAction}`}>
          {getActionIcon(resultAction)}
          <span>ACTION: {resultAction}</span>
        </div>
      </div>

      {/* Red-Flag Escalation Alert */}
      {resultAction === 'ESCALATE' && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.4)',
          borderRadius: '12px',
          padding: '16px 20px',
          display: 'flex',
          gap: '14px',
          alignItems: 'flex-start'
        }}>
          <AlertOctagon size={24} color="#f87171" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h4 style={{ color: '#f87171', fontWeight: 800, fontSize: '1rem', marginBottom: '4px' }}>
              🚨 CRITICAL SAFETY MEDICAL ESCALATION
            </h4>
            <p style={{ color: '#fca5a5', fontSize: '0.9rem', lineHeight: 1.5 }}>
              {safety_message || "Spreading fascial space infection or airway threat detected. Immediate Emergency Department or Maxillofacial surgery referral required."}
            </p>
          </div>
        </div>
      )}

      {/* Missing Information Checklist (if ASK) */}
      {resultAction === 'ASK' && missing_information.length > 0 && (
        <div style={{
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          borderRadius: '12px',
          padding: '18px 20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: '#fbbf24' }}>
            <HelpCircle size={20} />
            <h4 style={{ fontWeight: 800, fontSize: '0.95rem' }}>
              ADDITIONAL DIAGNOSTIC INFORMATION REQUIRED
            </h4>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '12px' }}>
            The clinical decision-support system cannot safely recommend treatment until the following critical items are established:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {missing_information.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.88rem', color: '#fde68a' }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#f59e0b' }} />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Abstention Rationale (if ABSTAIN) */}
      {resultAction === 'ABSTAIN' && (
        <div style={{
          background: 'rgba(249, 115, 22, 0.1)',
          border: '1px solid rgba(249, 115, 22, 0.3)',
          borderRadius: '12px',
          padding: '18px 20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#fb923c' }}>
            <AlertTriangle size={20} />
            <h4 style={{ fontWeight: 800, fontSize: '0.95rem' }}>
              SAFETY ABSTENTION RATIONALE
            </h4>
          </div>
          <p style={{ fontSize: '0.9rem', color: '#fdba74', lineHeight: 1.5 }}>
            {safety_message || "System withholding advice due to conflicting diagnostic findings or adversarial prompt injection attempt."}
          </p>
        </div>
      )}

      {/* Answer Recommendation Narrative (if ANSWER) */}
      {resultAction === 'ANSWER' && answer && (
        <div style={{
          background: 'rgba(16, 185, 129, 0.05)',
          border: '1px solid rgba(16, 185, 129, 0.2)',
          borderRadius: '12px',
          padding: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: '#34d399' }}>
            <FileText size={20} />
            <h4 style={{ fontWeight: 800, fontSize: '0.95rem' }}>
              EVIDENCE-GROUNDED CLINICAL RECOMMENDATION
            </h4>
          </div>
          <p style={{ fontSize: '0.92rem', color: '#e2e8f0', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
            {answer}
          </p>
        </div>
      )}

      {/* Traceable Citations Panel */}
      {citations.length > 0 && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#93c5fd' }}>
            <BookOpen size={16} />
            <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Traceable Evidence Citations & Guidelines
            </span>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {citations.map((c, i) => (
              <span key={i} className="citation-chip">
                <ShieldCheck size={14} color="#60a5fa" />
                {c}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Triggered Rules Audit Trail */}
      {rules.length > 0 && (
        <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '12px', marginTop: '4px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>
            Triggered Determinability Rules:
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '6px' }}>
            {rules.map((r, i) => (
              <span key={i} style={{ fontSize: '0.8rem', color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>
                • {r}
              </span>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
