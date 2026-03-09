import { useState } from 'react';

export default function NetworkPage() {
  // 1. STATE: Holds all form data
  const [formData, setFormData] = useState({
    dur: 0.5, proto: 'tcp', service: 'http', state: 'FIN',
    spkts: 12, dpkts: 10, sbytes: 800, dbytes: 15000, rate: 40.0
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // 2. PRESETS
  const loadPreset = (type) => {
    const presets = {
      "normal_web_browsing": { 
        dur: 0.5, proto: "tcp", service: "http", state: "FIN", spkts: 12, dpkts: 10,
        sbytes: 800, dbytes: 15000, rate: 40.0 
      },
      "file_transfer_ftp": {
        dur: 2.5, proto: "tcp", service: "ftp", state: "FIN", spkts: 30, dpkts: 25,
        sbytes: 2000, dbytes: 50000, rate: 20.0
      },
      "dns_query": { 
        dur: 0.001, proto: "udp", service: "dns", state: "CON", spkts: 2, dpkts: 2,
        sbytes: 146, dbytes: 178, rate: 2000.0 
      },
      "suspicious_scan": { 
        dur: 0.01, proto: "tcp", service: "-", state: "INT", spkts: 5, dpkts: 0, 
        sbytes: 200, dbytes: 0, rate: 500.0 
      }
    };
    if (presets[type]) setFormData(presets[type]);
  };

  // 3. HANDLER: Updates state when user types
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // 4. SUBMIT: Calls the Python API
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/predict/network', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      
      if (data.success) {
        setResult(data.data);
      } else {
        setError(data.error || 'Prediction failed');
      }
    } catch (err) {
      setError('Connection Error: Is the Flask server running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>🌐 Network Intrusion Detection</h2>
      <p>UNSW-NB15 Dataset Analysis</p>
      
      {/* Buttons to load presets */}
      <div className="preset-selector" style={{marginBottom: '20px'}}>
        <label style={{display: 'block', marginBottom: '10px', color: 'white', fontWeight: 'bold'}}>Quick Start - Choose Traffic Type:</label>
        <div style={{display: 'flex', gap: '10px', flexWrap: 'wrap'}}>
          <button type="button" onClick={() => loadPreset('normal_web_browsing')} className="btn-secondary">🌐 Normal Web</button>
          <button type="button" onClick={() => loadPreset('file_transfer_ftp')} className="btn-secondary">📁 FTP Transfer</button>
          <button type="button" onClick={() => loadPreset('dns_query')} className="btn-secondary">🔍 DNS Query</button>
          <button type="button" onClick={() => loadPreset('suspicious_scan')} className="btn-secondary">⚠️ Port Scan</button>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <h3>📊 Traffic Information</h3>
          <div className="form-row">
            <div className="form-group tooltip-container">
              <label>Duration (seconds) <span className="info-icon" title="How long the connection lasted">ⓘ</span></label>
            {/* Value comes from State, Change updates State */}
              <input type="number" name="dur" value={formData.dur} onChange={handleChange} step="0.001" />
            </div>
            <div className="form-group tooltip-container">
              <label>Protocol<span className="info-icon" title="Network communication protocol">ⓘ</span></label>
              <select name="proto" value={formData.proto} onChange={handleChange}>
                <option value="tcp">TCP</option>
                <option value="udp">UDP</option>
                <option value="arp">ARP</option>
                <option value="other">Other</option>
            </select>
          </div>
        </div>
        <div className="form row">
          <div className="form-group tooltip-container">
            <label>Service <span className="info-icon" title="What application is using the connection">ⓘ</span></label>
            <select name="service" value={formData.service} onChange={handleChange}>
              <option value="http">HTTP</option>
              <option value="https">HTTPS</option>
              <option value="ftp">FTP</option>
              <option value="dns">DNS</option>
            </select>
          </div>
        <div className="form-group tooltip-container">
          <label>State <span className="info-icon" title="current status of the connection">ⓘ</span></label>
          <select name="state" value={formData.state} onChange={handleChange}>
            <option value="FIN">FIN</option>
            <option value="CON">CON</option>
            <option value="INT">INT</option>
            <option value="REQ">REQ</option>
          </select>
        </div>
      </div>
    </div>

    <div className="form-section">
      <h3>📦 Packet & Data Information</h3>
      <div className="form-row">
        <div className="form-group tooltip-container">
          <label>Source Packets <span className="info-icon" title="Packets sent from source">ⓘ</span></label>
          <input type="number" name="spkts" value={formData.spkts} onChange={handleChange} />
        </div>
        <div className="form-group tooltip-container">
          <label>Destination Packets <span classname="info-icon" title="Packets received at destination">ⓘ</span></label>
          <input type="number" name="dpkts" value={formData.dpkts} onChange={handleChange} />
        </div>
      </div>
      <div className="form-row">
        <div className="form-group tooltip-container">
          <label>Source Bytes <span classname="info-icon" title="Bytes sent from source">ⓘ</span></label>
          <input type="number" name="sbytes" value={formData.sbytes} onChange={handleChange} />
        </div>
        <div className="form-group tooltip-container">
          <label>Destination Bytes <span classname="info-icon" title="Bytes received at destination">ⓘ</span></label>
          <input type="number" name="dbytes" value={formData.dbytes} onChange={handleChange} />
        </div>
      </div>
      <div className="form-group tooltip-container">
          <label>Transmisssion Rate (pkts/sec) <span classname="info-icon" title="Data transfer rate">ⓘ</span></label>
          <input type="number" name="rate" value={formData.rate} onChange={handleChange} step="0.01" />
      </div>
    </div>
        
    <button type="submit" className="btn btn-large" disabled={loading}>
      {loading ? 'Analyzing...' : '🔍 Analyze Traffic'}
     </button>
  </form>

  {/* ERROR MESSAGE */}
  {error && <div className="alert alert-error mt-3">{error}</div>}

  {/* RESULT DISPLAY */}
  {result && (
    <div className="results-container mt-4">
      <div className="result-card ensemble-result" style={{borderLeft: `5px solid ${result.ensemble.prediction === 'Normal' ? '#27ae60' : '#e74c3c'}`}}>
        <h3 style={{color: result.ensemble.prediction === 'Normal' ? '#27ae60' : '#e74c3c'}}>
          {result.ensemble.prediction === 'Normal' ? '✅ Normal Traffic' : '⚠️ Potential Threat Detected'}
        </h3>
        <div className="confidence-display">
            <div className="confidence-label">Confidence Level</div>
            <div className="confidence-bar-container">
                <div className="confidence-bar" style={{width: `${result.ensemble.confidence}%`, background: result.ensemble.prediction === 'Normal' ? '#27ae60' : '#e74c3c'}}></div>
            </div>
            <div className="confidence-value">{result.ensemble.confidence}%</div>
        </div>
        <div className="voting-summary">
          <p><strong>Model Agreement:</strong> {result.ensemble.votes.Normal} Normal vs {result.ensemble.votes.Attack} Attack</p>
        </div>
      </div>
            
      {/* Render model details loop */}
      <div className="models-breakdown mt-4">
          <h4>Individual Models Results</h4>
          <div className="model-cards mt-3">
              {Object.entries(result.models).map(([name, data]) => {
                const color = data.prediction === 'Normal' ? '#27ae60' : '#e74c3c';
                return (
                  <div key={name} className="model-card">
                    <div className="model-header">
                    <span className="model-name" style={{textTransform: 'captalize'}}>{name.replace('_', ' ')}</span>
                    <span className="model- badge" style={{background: color}}>{data.prediction}</span>
                    </div>
                    <div className="model-confidence">
                      <small>Condidence: {data.confidence}%</small>
                      <div className="mini-confidence-bar"><div style={{width: `${data.confidence}%`, backgroung: color}}></div></div>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      </div>
      )}
    </div>
  );
}