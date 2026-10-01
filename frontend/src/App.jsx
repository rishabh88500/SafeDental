import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DemoSelector from './components/DemoSelector';
import ResultCard from './components/ResultCard';
import ComparisonView from './components/ComparisonView';
import MetricsModal from './components/MetricsModal';
import { DEMO_SCENARIOS } from './data/demoData';
import { Play, Sparkles, Sliders, RefreshCw } from 'lucide-react';

export default function App() {
  const [isApiConnected, setIsApiConnected] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState(DEMO_SCENARIOS[0]);
  const [narrativeInput, setNarrativeInput] = useState(DEMO_SCENARIOS[0].narrative);
  const [armMode, setArmMode] = useState('ARM_C'); // ARM_C, ARM_B, ARM_A, COMPARE
  const [isMetricsOpen, setIsMetricsOpen] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [singleResult, setSingleResult] = useState(null);

  const [compResults, setCompResults] = useState({
    armA: null,
    armB: null,
    armC: null
  });

  // Check API Connection on mount
  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 'ok') {
          setIsApiConnected(true);
        }
      })
      .catch(() => setIsApiConnected(false));
  }, []);

  // Update narrative input when scenario changes
  const handleSelectScenario = (sc) => {
    setSelectedScenario(sc);
    setNarrativeInput(sc.narrative);
    setSingleResult(null);
    setCompResults({ armA: null, armB: null, armC: null });
  };

  // Run Decision Support Analysis
  const handleRunAnalysis = async () => {
    setIsLoading(true);

    if (isApiConnected) {
      try {
        if (armMode === 'COMPARE') {
          const [resA, resB, resC] = await Promise.all([
            fetch('http://localhost:8000/api/analyze', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ narrative: narrativeInput, arm: 'ARM_A' })
            }).then(r => r.json()),
            fetch('http://localhost:8000/api/analyze', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ narrative: narrativeInput, arm: 'ARM_B' })
            }).then(r => r.json()),
            fetch('http://localhost:8000/api/analyze', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ narrative: narrativeInput, arm: 'ARM_C' })
            }).then(r => r.json())
          ]);

          setCompResults({ armA: resA, armB: resB, armC: resC });
        } else {
          const res = await fetch('http://localhost:8000/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ narrative: narrativeInput, arm: armMode })
          }).then(r => r.json());

          setSingleResult(res);
        }
      } catch (err) {
        console.error('API call failed, using client fallback demo data:', err);
        fallbackClientExecution();
      }
    } else {
      // Client Demo Fallback Simulation
      setTimeout(() => {
        fallbackClientExecution();
      }, 400);
    }

    setIsLoading(false);
  };

  const fallbackClientExecution = () => {
    if (armMode === 'COMPARE') {
      setCompResults({
        armA: {
          action: 'ANSWER',
          answer: selectedScenario.recommendation || `Baseline LLM output recommending treatment for: ${narrativeInput.slice(0, 100)}...`,
          citations: []
        },
        armB: {
          action: selectedScenario.expectedAction,
          answer: selectedScenario.recommendation,
          missing_information: selectedScenario.missingInfo,
          safety_message: selectedScenario.expectedAction === 'ESCALATE' ? 'Ludwig\'s angina airway threat detected.' : '',
          citations: []
        },
        armC: {
          action: selectedScenario.expectedAction,
          answer: selectedScenario.recommendation,
          missing_information: selectedScenario.missingInfo,
          safety_message: selectedScenario.expectedAction === 'ESCALATE' ? 'Ludwig\'s angina airway threat detected.' : '',
          citations: selectedScenario.citations
        }
      });
    } else {
      setSingleResult({
        action: armMode === 'ARM_A' ? 'ANSWER' : selectedScenario.expectedAction,
        answer: armMode === 'ARM_A' ? `Baseline LLM output for: ${narrativeInput.slice(0, 100)}...` : selectedScenario.recommendation,
        missing_information: armMode === 'ARM_A' ? [] : selectedScenario.missingInfo,
        safety_message: selectedScenario.expectedAction === 'ESCALATE' ? 'Ludwig\'s angina airway threat detected.' : '',
        citations: armMode === 'ARM_C' ? selectedScenario.citations : [],
        rules: selectedScenario.rules
      });
    }
  };

  return (
    <div style={{ maxWidth: '1350px', margin: '0 auto', padding: '24px 20px' }}>
      
      {/* Navbar Header */}
      <Header
        isApiConnected={isApiConnected}
        onOpenMetrics={() => setIsMetricsOpen(true)}
      />

      {/* Main Grid Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 440px) 1fr', gap: '28px', alignItems: 'start' }}>
        
        {/* Left Control Panel */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          
          {/* Scenario Selector */}
          <DemoSelector
            scenarios={DEMO_SCENARIOS}
            selectedId={selectedScenario.id}
            onSelectScenario={handleSelectScenario}
          />

          {/* Narrative Input Area */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#94a3b8', marginBottom: '8px', letterSpacing: '0.5px', textTransform: 'uppercase' }}>
              Clinical Case Narrative / Patient Complaint:
            </label>
            <textarea
              value={narrativeInput}
              onChange={(e) => setNarrativeInput(e.target.value)}
              rows={6}
              style={{
                width: '100%',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: '14px',
                color: '#f8fafc',
                fontSize: '0.9rem',
                lineHeight: 1.5,
                fontFamily: 'var(--font-sans)',
                resize: 'vertical',
                outline: 'none'
              }}
            />
          </div>

          {/* Mode Selector Radio */}
          <div style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px', color: '#94a3b8' }}>
              <Sliders size={16} />
              <span style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Pipeline Execution Mode
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button
                className={`btn-secondary ${armMode === 'ARM_C' ? 'active' : ''}`}
                onClick={() => setArmMode('ARM_C')}
                style={{ justifyContent: 'flex-start' }}
              >
                ✨ Arm C: Proposed System (RAG + Safety)
              </button>
              
              <button
                className={`btn-secondary ${armMode === 'ARM_B' ? 'active' : ''}`}
                onClick={() => setArmMode('ARM_B')}
                style={{ justifyContent: 'flex-start' }}
              >
                🛡️ Arm B: Safety Prompting Gate
              </button>

              <button
                className={`btn-secondary ${armMode === 'ARM_A' ? 'active' : ''}`}
                onClick={() => setArmMode('ARM_A')}
                style={{ justifyContent: 'flex-start' }}
              >
                ⚠️ Arm A: Base LLM (No Safety Gate)
              </button>

              <button
                className={`btn-secondary ${armMode === 'COMPARE' ? 'active' : ''}`}
                onClick={() => setArmMode('COMPARE')}
                style={{ justifyContent: 'flex-start' }}
              >
                📊 Side-by-Side Comparison (Arms A vs B vs C)
              </button>
            </div>
          </div>

          {/* Action Trigger Button */}
          <button
            onClick={handleRunAnalysis}
            className="btn-primary"
            style={{ width: '100%' }}
            disabled={isLoading}
          >
            {isLoading ? <RefreshCw size={18} className="spin" /> : <Play size={18} />}
            <span>{isLoading ? 'Analyzing Case...' : 'Run Decision Support Analysis'}</span>
          </button>

        </div>

        {/* Right Output Results Panel */}
        <div>
          {armMode === 'COMPARE' ? (
            <ComparisonView
              armAResult={compResults.armA}
              armBResult={compResults.armB}
              armCResult={compResults.armC}
              isLoading={isLoading}
            />
          ) : (
            <ResultCard
              armName={armMode === 'ARM_C' ? 'Arm C: Proposed RAG + Safety System' : (armMode === 'ARM_B' ? 'Arm B: Safety Prompting' : 'Arm A: Base LLM Baseline')}
              resultData={singleResult}
              isLoading={isLoading}
            />
          )}
        </div>

      </div>

      {/* Benchmark Metrics Modal */}
      <MetricsModal
        isOpen={isMetricsOpen}
        onClose={() => setIsMetricsOpen(false)}
      />

    </div>
  );
}
