import { useState } from 'react';

export default function XrayPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analysisType, setAnalysisType] = useState('all');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (selectedFile) => {
    if (selectedFile && selectedFile.type.startsWith('image/')) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setError(null);
    } else {
      setError('Please select a valid image file.');
    }
  };

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = () => { setIsDragging(false); };
  const handleDrop = (e) => {
    e.preventDefault(); setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return setError('Please select an X-ray image first.');
    
    setLoading(true); setError(null); setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('analysis_type', analysisType);

    try {
      const apiUrl= import.meta.env.VITE_API_URL || '';
      
      const response = await fetch(`${apiUrl}/api/predict/xray`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (data.success) setResult(data.data);
      else setError(data.error || 'Prediction failed');
    } catch (err) {
      setError('Connection Error: Is the Flask server running?');
    } finally {
      setLoading(false);
    }
  };

  return (
      <div className="form-container">
        <header style={{textAlign: 'center', marginBottom: '20px'}}>
          <h2 style={{fontSize: '2rem'}}>🏥 Medical Chest X-ray Analysis</h2>
          <p className="subtitle">AI-Powered Diagnostic Assistance using NIH Chest X-ray14 Dataset</p>
        </header>

        <div className="medical-disclaimer mt-4">
            <strong>⚕️ This is a research tool for educational purposes only. Not for clinical diagnosis.</strong>
            <ul style={{marginLeft: '20px'}}>
              <li>❌ Not approved for clinical diagnosis</li>
              <li>❌ Not a substitute for professional medical advice</li>
              <li>✅ For research and demonstration purposes only</li>
              <li>✅ Always consult qualified healthcare professionals</li>
            </ul>
        </div>

        <div className="info-panel mb-4">
          <h3>📊 What This System Detects</h3>
          <p>Upload a chest X-ray image and our AI models will analyze for 14 common thoracic conditions:</p>
          <div className="conditions-grid mt-2">
              <div className="condition-item"><span className="condition-icon">🫁</span><span>Atelectasis</span></div>
              <div className="condition-item"><span className="condition-icon">❤️</span><span>Cardiomegaly</span></div>
              <div className="condition-item"><span className="condition-icon">💧</span><span>Effusion</span></div>
              <div className="condition-item"><span className="condition-icon">🦠</span><span>Infiltration</span></div>
              <div className="condition-item"><span className="condition-icon">🔴</span><span>Mass</span></div>
              <div className="condition-item"><span className="condition-icon">⚪</span><span>Nodule</span></div>
              <div className="condition-item"><span className="condition-icon">🫁</span><span>Pneumonia</span></div>
              <div className="condition-item"><span className="condition-icon">💨</span><span>Pneumothorax</span></div>
              <div className="condition-item"><span className="condition-icon">🌫️</span><span>Consolidation</span></div>
              <div className="condition-item"><span className="condition-icon">💧</span><span>Edema</span></div>
              <div className="condition-item"><span className="condition-icon">🫁</span><span>Emphysema</span></div>
              <div className="condition-item"><span className="condition-icon">🧬</span><span>Fibrosis</span></div>
              <div className="condition-item"><span className="condition-icon">📏</span><span>Pleural Thickening</span></div>
              <div className="condition-item"><span className="condition-icon">🔺</span><span>Hernia</span></div>
          </div>
      </div>
      
      {/* Upload Section */}
      <div classname="form-container">
        <h2>📸 Upload Chest X-ray Image</h2>
        <p className="subtitle mb-3">Upload a frontal chest X-ray for AI analysis</p>

        {/* Technical Specs */}
        <div className="tech-specs mb-4">
            <h4 style={{marginTop: 0, marginBottom:'10px'}}>📋 Image Requirements:</h4>
            <ul>
                <li>✅ Frontal (PA or AP) chest X-ray</li>
                <li>✅ Grayscale or color image</li>
                <li>✅ Common formats: JPG, PNG, DICOM</li>
                <li>✅ Maximum file size: 10MB</li>
            </ul>
        </div>
        
        {/* Upload Form */}
        <form onSubmit={handleSubmit}>
          <div 
            className={`file-upload-zone ${isDragging ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('xrayFileInput').click()}
          >
            <input 
              type="file" 
              id="xrayFileInput" 
              className="file-upload-input" 
              accept="image/*" 
              onChange={(e) => handleFileChange(e.target.files[0])}
            />
            <div className="upload-icon">🏥</div>
            <span className="upload-text">Click to upload or drag X-ray here</span>
            <span className="upload-hint">Supported: JPG, PNG (Max 10MB)</span>

            {preview && (
              <div className="image-preview mt-3" onClick={(e) => e.stopPropagation()}>
                <img src={preview} alt="Preview" style={{maxHeight: '250px', borderRadius: '8px'}} />
                <button type="button" className="remove-image" onClick={(e) => {e.stopPropagation(); setFile(null); setPreview(null);}}>✕</button>
              </div>
            )}
          </div>

          <div className="analysis-options mt-4">
              <h4>🔬 Select Analysis Type:</h4>
              <div className="radio-group mt-2">
                  <label className="radio-option">
                      <input type="radio" value="all" checked={analysisType === 'all'} onChange={(e) => setAnalysisType(e.target.value)} />
                      <span className="radio-label">
                        <strong>Complete Analysis</strong>
                        <small>Both unsupervised (anomaly detection) + supervised (disease classification) models</small>
                      </span>
                  </label>
                  <label className="radio-option">
                    <input type="radio" value="unsupervised" checked={analysisType === 'unsupervised'} onChange={(e) => setAnalysisType(e.target.value)} />
                    <span className="radio-label">
                      <strong> Anomaly Detection Only</strong>
                      <small>Detect unusual patterns (Autoencoder, IsolationForest, etc.)</small>
                    </span>
                  </label>
                  <label className="radio-option">
                    <input type="radio" value="supervised" checked={analysisType === 'supervised'} onChange={(e) => setAnalysisType(e.target.value)} />
                    <span className="radio-label">
                      <strong> Disease Classification Only</strong>
                      <small>Identity specific conditions (Decision Tree, KNN)</small>
                    </span>
                  </label>
                </div>
            </div>

          <button type="submit" className="btn btn-large medical-btn mt-4" disabled={loading || !file}>
            {loading ? 'Analyzing...' : '🔬 Analyze X-ray'}
          </button>
        </form>
      </div>

      {loading && (
        <div className="loading mt-4">
          <div className="spinner"></div>
          <p className="loading-main">🏥 Analyzing Chest X-ray...</p>
          <div className="loading-steps" style={{textAlign: 'left', display: 'inline-block', color: '#7f8c8d'}}>
              <p>📸 Step 1: Preprocessing image (224x224 normalization)</p>
              <p>🤖 Step 2: Running unsupervised anomaly detection</p>
              <p>🏥 Step 3: Running supervised disease classifiers</p>
              <p>📊 Step 4: Computing ensemble predictions</p>
          </div>
        </div>
      )}
        
      {/* Error State */}
      {error && <div className="alert alert-error mt-3">{error}</div>}
      
      {/* Results State */}
      {result && (
        <div className="results-container mt-4">
            <div className="medical-warning mb-3">
                ⚕️ <strong>Medical Disclaimer:</strong> {result.medical_disclaimer || 'This is for research purposes only. Always consult qualified healthcare professionals.'}
            </div>

            {/* Overall Ensemble Result */}
            <div className="result-card ensemble-result" style={{borderLeft: `5px solid ${result.ensemble.prediction === 'Normal' ? '#27ae60' : '#e74c3c'}`}}>
                <h3 style={{color: result.ensemble.prediction === 'Normal' ? '#27ae60' : '#e74c3c'}}>
                    {result.ensemble.prediction === 'Normal' ? '✅ Analysis Result: Normal' : '⚠️ Analysis Result: Anomaly Detected'}
                </h3>
                <div className="confidence-display">
                    <div className="confidence-label">Overall Confidence</div>
                    <div className="confidence-bar-container">
                        <div className="confidence-bar" style={{width: `${result.ensemble.confidence}%`, background: result.ensemble.prediction === 'Normal' ? '#27ae60' : '#e74c3c'}}></div>
                    </div>
                    <div className="confidence-value">{result.ensemble.confidence}%</div>
                </div>
                <div className="voting-summary mt-3">
                    <p><strong>Consensus:</strong> {result.ensemble.votes.Normal} models indicate Normal, {result.ensemble.votes.Anomaly} detect Anomaly.</p>
                    {result.ensemble.interpretation && <p className="explanation-text">{result.ensemble.interpretation}</p>}
                </div>
            </div>
            
            {/* Unsupervised Models Breakdown */}
            {Object.keys(result.unsupervised_models || {}).length > 0 && (
              <div className="models-breakdown mt-4">
                  <h4 style={{borderBottom: '2px solid #e0e0e0', paddingBottom: '10px'}}>🔬 Unsupervised Anomaly Detection</h4>
                  <p className="section-description">These models detect unusual patterns without knowing specific diseases</p>
                  <div className="model-cards mt-2">
                      {Object.entries(result.unsupervised_models).map(([name, data]) => {
                          const modelColor = data.prediction === 'Normal' ? '#27ae60' : '#e74c3c';
                          return (
                            <div key={name} className="model-card">
                                <div className="model-header">
                                    <span className="model-name" style={{textTransform: 'capitalize'}}>{name.replace('_', ' ')}</span>
                                    <span className="model-badge" style={{background: modelColor}}>{data.prediction}</span>
                                </div>
                                <div className="model-confidence mt-2">
                                    {data.method && <small className="model-method d-block mb-1 text-muted">{data.method}</small>}
                                    {data.reconstruction_error !== undefined && (
                                        <small className="d-block mb-1">Error: {Number(data.reconstruction_error).toFixed(4)}</small>
                                    )}
                                    {data.confidence && (
                                        <>
                                            <small>Confidence: {data.confidence}%</small>
                                            <div className="mini-confidence-bar">
                                                <div style={{width: `${data.confidence}%`, background: modelColor}}></div>
                                            </div>
                                        </>
                                    )}
                                </div>
                            </div>
                          );
                      })}
                  </div>
              </div>
            )}

            {/* Supervised Models Breakdown (Disease Classification) */}
            {Object.keys(result.supervised_models || {}).length > 0 && (
              <div className="models-breakdown mt-4">
                  <h4 style={{borderBottom: '2px solid #e0e0e0', paddingBottom: '10px'}}>🏥 Disease Classification (Supervised)</h4>
                  <p className="section-description">These models identify specific thoracic conditions</p>
                  <div className="model-cards mt-2">
                      {Object.entries(result.supervised_models).map(([name, data]) => {
                          // The Python backend returns disease_info containing color, icon, common_name etc.
                          const diseaseInfo = data.disease_info || {};
                          const color = diseaseInfo.color || '#95a5a6';
                          
                          return (
                            <div key={name} className="model-card disease-card" style={{borderLeft: `5px solid ${color}`}}>
                                <div className="model-header">
                                    <span className="model-name" style={{textTransform: 'capitalize'}}>{name.replace('_', ' ')}</span>
                                    <span className="model-badge" style={{background: color}}>
                                        {diseaseInfo.icon || ''} {data.prediction}
                                    </span>
                                </div>
                                
                                {diseaseInfo.common_name && (
                                    <p className="disease-common-name mt-2" style={{fontWeight: '600', color: color, fontSize: '0.95rem'}}>
                                        {diseaseInfo.common_name}
                                    </p>
                                )}
                                
                                {diseaseInfo.description && (
                                    <p className="disease-description mt-1" style={{fontSize: '0.85rem', color: '#7f8c8d'}}>
                                        {diseaseInfo.description}
                                    </p>
                                )}
                                
                                {data.confidence && (
                                    <div className="model-confidence mt-2">
                                        <small>Confidence: {data.confidence.toFixed(1)}%</small>
                                        <div className="mini-confidence-bar">
                                            <div style={{width: `${data.confidence}%`, background: color}}></div>
                                        </div>
                                    </div>
                                )}
                                
                                {diseaseInfo.recommendation && (
                                    <div className="disease-recommendation mt-3" style={{background: '#fff3cd', padding: '8px', borderRadius: '4px', fontSize: '0.85rem', color: '#856404', borderLeft: '3px solid #f39c12'}}>
                                        <strong>Recommendation:</strong> {diseaseInfo.recommendation}
                                    </div>
                                )}
                            </div>
                          );
                      })}
                  </div>
              </div>
            )}
        </div>
      )}
    </div>
  );
}