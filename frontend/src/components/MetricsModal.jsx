import React from 'react';
import { X, Award, CheckCircle2, AlertOctagon, TrendingDown, Layers } from 'lucide-react';
import { BENCHMARK_SUMMARY } from '../data/demoData';

export default function MetricsModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const { metrics, significance } = BENCHMARK_SUMMARY;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(5, 8, 16, 0.85)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '850px',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '32px',
        position: 'relative'
      }}>
        
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            color: '#94a3b8',
            borderRadius: '50%',
            width: '36px',
            height: '36px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer'
          }}
        >
          <X size={18} />
        </button>

        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <Award size={28} color="#10b981" />
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f8fafc' }}>
              Development Benchmark Results (71 Clinical Cases)
            </h2>
            <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
              Comparative evaluation of Arm A (Base LLM), Arm B (Safety Prompt), and Arm C (Proposed RAG + Safety System).
            </p>
          </div>
        </div>

        {/* Metrics Grid Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '16px',
          marginBottom: '28px'
        }}>
          
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '12px', padding: '16px' }}>
            <div style={{ fontSize: '0.8rem', color: '#fca5a5', fontWeight: 700, textTransform: 'uppercase' }}>
              Unsafe Rec Rate (Arm A)
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#f87171', margin: '4px 0' }}>
              {(metrics.ARM_A.unsafe_recommendation_rate * 100).toFixed(2)}%
            </div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Unconstrained LLM Baseline</div>
          </div>

          <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '12px', padding: '16px' }}>
            <div style={{ fontSize: '0.8rem', color: '#6ee7b7', fontWeight: 700, textTransform: 'uppercase' }}>
              Unsafe Rec Rate (Arm C)
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#34d399', margin: '4px 0' }}>
              {(metrics.ARM_C.unsafe_recommendation_rate * 100).toFixed(2)}%
            </div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Proposed System (0.00% Unsafe)</div>
          </div>

          <div style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '12px', padding: '16px' }}>
            <div style={{ fontSize: '0.8rem', color: '#93c5fd', fontWeight: 700, textTransform: 'uppercase' }}>
              Clinical Answer Accuracy
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#60a5fa', margin: '4px 0' }}>
              {(metrics.ARM_C.clinical_answer_accuracy * 100).toFixed(2)}%
            </div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>On Determinable Cases</div>
          </div>

        </div>

        {/* Full Comparative Table */}
        <div style={{ marginBottom: '24px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '12px' }}>
            Comparative Research Metrics Table
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', color: '#94a3b8', textAlign: 'left' }}>
                  <th style={{ padding: '10px' }}>Metric</th>
                  <th style={{ padding: '10px' }}>Arm A (Base LLM)</th>
                  <th style={{ padding: '10px' }}>Arm B (Safety Prompt)</th>
                  <th style={{ padding: '10px' }}>Arm C (Proposed System)</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <td style={{ padding: '10px', fontWeight: 600 }}>Unsafe Recommendation Rate (↓)</td>
                  <td style={{ padding: '10px', color: '#f87171', fontWeight: 700 }}>64.58%</td>
                  <td style={{ padding: '10px', color: '#34d399', fontWeight: 700 }}>0.00%</td>
                  <td style={{ padding: '10px', color: '#34d399', fontWeight: 700 }}>0.00%</td>
                </tr>
                <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <td style={{ padding: '10px', fontWeight: 600 }}>Safe Abstention Rate (↑)</td>
                  <td style={{ padding: '10px' }}>35.42%</td>
                  <td style={{ padding: '10px', color: '#34d399' }}>100.00%</td>
                  <td style={{ padding: '10px', color: '#34d399' }}>100.00%</td>
                </tr>
                <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <td style={{ padding: '10px', fontWeight: 600 }}>Clinical Answer Accuracy (↑)</td>
                  <td style={{ padding: '10px' }}>100.00%</td>
                  <td style={{ padding: '10px' }}>100.00%</td>
                  <td style={{ padding: '10px', color: '#60a5fa', fontWeight: 700 }}>100.00%</td>
                </tr>
                <tr>
                  <td style={{ padding: '10px', fontWeight: 600 }}>Over-Abstention Rate (↓)</td>
                  <td style={{ padding: '10px' }}>0.00%</td>
                  <td style={{ padding: '10px' }}>0.00%</td>
                  <td style={{ padding: '10px', color: '#34d399' }}>0.00%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Significance */}
        <div style={{ background: 'rgba(255, 255, 255, 0.03)', borderRadius: '12px', padding: '16px', border: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#cbd5e1' }}>
            Statistical Significance (McNemar's Chi-Squared Test):
          </div>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '4px' }}>
            Arm A vs. Arm C Unsafe Recommendation Rate: <strong>χ² = {significance.chi2}</strong>, <strong>p &lt; 0.000001</strong> (Statistically Significant at p &lt; 0.05).
          </p>
        </div>

      </div>
    </div>
  );
}
