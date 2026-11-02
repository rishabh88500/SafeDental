import React from 'react';
import { Activity, ShieldCheck, Database, Award, Server } from 'lucide-react';

export default function Header({ isApiConnected, onOpenMetrics }) {
  return (
    <header className="glass-panel" style={{ padding: '16px 28px', marginBottom: '28px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Brand & Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '46px',
            height: '46px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px',
            boxShadow: '0 0 20px rgba(16, 185, 129, 0.3)'
          }}>
            🦷
          </div>
          <div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 800, background: 'linear-gradient(90deg, #f8fafc 0%, #cbd5e1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              SafeDental
            </h1>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 500 }}>
              Safety-Aware Acute Dental Decision Support Engine
            </p>
          </div>
        </div>

        {/* Right Stats & Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          
          {/* API Status Badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 14px',
            borderRadius: '20px',
            background: isApiConnected ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
            border: `1px solid ${isApiConnected ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
            fontSize: '0.8rem',
            fontWeight: 600,
            color: isApiConnected ? '#34d399' : '#fbbf24'
          }}>
            <Server size={14} />
            {isApiConnected ? 'REST API Connected (localhost:8000)' : 'Client Standalone Demo Engine Active'}
          </div>

          {/* Benchmark Metrics Button */}
          <button 
            onClick={onOpenMetrics}
            className="btn-secondary"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
          >
            <Award size={16} color="#10b981" />
            <span>Dev Set Benchmark (0.00% Unsafe)</span>
          </button>
        </div>

      </div>
    </header>
  );
}
