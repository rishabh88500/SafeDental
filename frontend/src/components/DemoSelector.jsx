import React from 'react';
import { Sparkles, CheckCircle2, HelpCircle, AlertTriangle, AlertOctagon, ShieldAlert } from 'lucide-react';

export default function DemoSelector({ scenarios, selectedId, onSelectScenario }) {
  const getIcon = (label) => {
    switch (label) {
      case 'DETERMINABLE': return <CheckCircle2 size={16} color="#10b981" />;
      case 'UNDERDETERMINED': return <HelpCircle size={16} color="#f59e0b" />;
      case 'SAFETY-CRITICAL': return <AlertOctagon size={16} color="#ef4444" />;
      case 'CONFLICTING': return <AlertTriangle size={16} color="#f97316" />;
      case 'OUT-OF-SCOPE': return <ShieldAlert size={16} color="#a855f7" />;
      default: return <Sparkles size={16} />;
    }
  };

  return (
    <div style={{ marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
        <Sparkles size={16} color="#06b6d4" />
        <span style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', color: '#94a3b8' }}>
          Select Pre-Loaded Clinical Demo Scenario
        </span>
      </div>

      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        {scenarios.map((sc) => {
          const isActive = sc.id === selectedId;
          return (
            <button
              key={sc.id}
              onClick={() => onSelectScenario(sc)}
              className={`tab-chip ${isActive ? 'active' : ''}`}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                borderRadius: '12px'
              }}
            >
              {getIcon(sc.label)}
              <span>{sc.id}: {sc.title}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
