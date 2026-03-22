import { useState } from 'react';

export default function MVTecPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

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
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const loadSampleImage = async (imagePath, fileName) => {
    try {
      setIsModalOpen(false); 
      setError(null);

      const response = await fetch(imagePath);
      const blob = await response.blob();
      
      const sampleFile = new File([blob], fileName, { type: blob.type });
      handleFileChange(sampleFile);
    } catch (err) {
      setError(`Failed to load sample image from ${imagePath}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return setError('Please select an image first.');
    
    setLoading(true); setError(null); setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const apiUrl= import.meta.env.VITE_API_URL || '';
      
        const response = await fetch(`${apiUrl}/api/predict/mvtec`, {
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

  const getMVTecExplanation = (isNormal, confidence) => {
    if (isNormal) {
        return "✓ This product passes quality inspection. No manufacturing defects or anomalies detected by our AI models.";
    } else {
        if (confidence >= 75) {
            return "⚠ Potential defect detected with high confidence. Manual inspection strongly recommended before shipping.";
        } else {
            return "⚠ Possible quality issue detected. Additional verification recommended to confirm defect status.";
        }
    }
  };

  return (
    <div className="form-container">
      <header style={{textAlign: 'center', marginBottom: '20px'}}>
        <h2 style={{fontSize: '2rem'}}>🏭 Product Quality Inspection</h2>
        <p className="subtitle">AI-Powered Visual Defect Detection using MVTec Dataset</p>
      </header>

      {/* Info Section with all tags */}
      <div className="info-panel mb-4">
          <h3>📊 What is MVTec Anomaly Detection?</h3>
          <p>Upload an image of a product (bottle, cable, circuit board, etc.) and our AI will detect manufacturing defects or anomalies.</p>
          <div className="supported-categories mt-3">
              <h4 style={{color: 'white', marginBottom: '10px'}}>✅ Supported Product Categories:</h4>
              <div className="category-tags">
                  <span className="tag">🍾 Bottle</span>
                  <span className="tag">🔌 Cable</span>
                  <span className="tag">💊 Capsule/Pill</span>
                  <span className="tag">🧱 Carpet/Fabric</span>
                  <span className="tag">⚡ Grid/Circuit</span>
                  <span className="tag">🥜 Hazelnut</span>
                  <span className="tag">🧵 Leather</span>
                  <span className="tag">🔩 Metal Nut</span>
                  <span className="tag">🧪 Screw</span>
                  <span className="tag">🟫 Tile</span>
                  <span className="tag">🪥 Toothbrush</span>
                  <span className="tag">📱 Transistor</span>
                  <span className="tag">🪵 Wood</span>
                  <span className="tag">🤐 Zipper</span>
              </div>
          </div>
      </div>

      <h2>📸 Upload Product Image</h2>
      <p className="subtitle mb-3">Drag & drop or click to select an image for quality inspection</p>

      {/* Sample Images Modal Setup */}
      <div className="sample-images-section mb-4">
          <button type="button" className="btn-secondary" onClick={() => setIsModalOpen(true)}>
              📁 View Sample Images
          </button>
          
          {isModalOpen && (
            <div className="modal show" onClick={() => setIsModalOpen(false)}>
                <div className="modal-content" onClick={e => e.stopPropagation()}>
                    <span className="close-modal" onClick={() => setIsModalOpen(false)}>&times;</span>
                    <h3>Sample Images for Testing</h3>
                    <p>Download these examples to test the system:</p>
                    <div className="sample-grid">
                        <div className="sample-item">
                            <div className="sample-preview normal-sample">✅ Normal Grid</div>
                            <button 
                                className="download-sample"
                                onClick={() => loadSampleImage('/mvtec/normal-grid.png', 'normal-grid.png')}
                                >
                                Download
                                </button>
                        </div>
                        <div className="sample-item">
                            <div className="sample-preview defect-sample">❌ Defective Grid</div>
                            <button 
                                className="download-sample"
                                onClick={() => loadSampleImage('/mvtec/defective-grid.png', 'defective-grid.png')}
                                >
                                Download
                                </button>
                        </div>
                        <div className="sample-item">
                            <div className="sample-preview normal-sample">✅ Normal Wood</div>
                            <button 
                                className="download-sample"
                                onClick={() => loadSampleImage('/mvtec/normal-wood.png', 'normal-wood.png')}
                                >
                                Download
                                </button>
                        </div>
                        <div className="sample-item">
                            <div className="sample-preview defect-sample">❌ Defective Wood</div>
                            <button 
                                className="download-sample"
                                onClick={() => loadSampleImage('/mvtec/defective-wood.png', 'defective-wood.png')}
                                >
                                Download
                                </button>
                        </div>
                    </div>
                </div>
            </div>
          )}
      </div>

      {/* Upload Form */}
      <form onSubmit={handleSubmit}>
        <div className="form-group mb-4">
            <div 
              className={`file-upload-zone ${isDragging ? 'drag-over' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById('imageFile').click()}
            >
                <input 
                  type="file" 
                  id="imageFile" 
                  className="file-upload-input" 
                  accept="image/*" 
                  onChange={(e) => handleFileChange(e.target.files[0])}
                />
                <div className="upload-icon">📁</div>
                <span className="upload-text">Click to upload or drag image here</span>
                <span className="upload-hint">Supported: JPG, PNG (Max 5MB)</span>
                
                {preview && (
                    <div className="image-preview mt-3" onClick={(e) => e.stopPropagation()}>
                        <img src={preview} alt="Preview" style={{maxHeight: '250px', borderRadius: '8px'}} />
                        <button type="button" className="remove-image" onClick={(e) => {e.stopPropagation(); setFile(null); setPreview(null);}}>✕</button>
                    </div>
                )}
            </div>
            {file && <div className="file-name mt-2 text-muted">Selected: {file.name}</div>}
        </div>

        <button type="submit" className="btn btn-large" disabled={loading || !file}>
            {loading ? 'Inspecting...' : '🔍 Inspect for Defects'}
        </button>
      </form>

      {/* Loading State */}
      {loading && (
        <div className="loading mt-4">
            <div className="spinner"></div>
            <p className="loading-main">🔬 Analyzing Image Quality...</p>
            <div className="loading-steps" style={{textAlign: 'left', display: 'inline-block', color: '#7f8c8d'}}>
                <p>⚙️ Step 1: Extracting visual features with ResNet34</p>
                <p>🤖 Step 2: Running 4 anomaly detection models</p>
                <p>📊 Step 3: Computing ensemble prediction</p>
            </div>
        </div>
      )}

      {/* Error State */}
      {error && <div className="alert alert-error mt-4">{error}</div>}

      {/* Results Rendering */}
      {result && (
        <div className="results-container mt-4">
            <div className="result-card ensemble-result" style={{borderLeft: `5px solid ${result.ensemble.prediction === 'Normal' ? '#27ae60' : '#e74c3c'}`}}>
                
                {result.image_info?.category && (
                    <div className="product-category" style={{textTransform: 'uppercase', fontSize: '1.3rem', fontWeight: 'bold', marginBottom: '10px'}}>
                        {result.image_info.category_icon} {result.image_info.category}
                    </div>
                )}
                
                <h3 style={{color: result.ensemble.prediction === 'Normal' ? '#27ae60' : '#e74c3c'}}>
                    {result.ensemble.prediction === 'Normal' ? '✅' : '⚠️'} Quality Inspection: {result.ensemble.prediction}
                </h3>
                
                {result.image_info?.category_description && (
                    <p className="category-description" style={{fontStyle: 'italic', color: '#7f8c8d'}}>
                        {result.image_info.category_description}
                    </p>
                )}
                
                <div className="confidence-display mt-3">
                    <div className="confidence-label">Quality Inspection Confidence</div>
                    <div className="confidence-bar-container">
                        <div className="confidence-bar" style={{width: `${result.ensemble.confidence}%`, background: result.ensemble.prediction === 'Normal' ? '#27ae60' : '#e74c3c'}}></div>
                    </div>
                    <div className="confidence-value">{result.ensemble.confidence}%</div>
                </div>
                
                <div className="voting-summary mt-3">
                    <p><strong>Model Agreement:</strong> {result.ensemble.votes.Normal} models say Normal, {result.ensemble.votes.Anomaly} detect Anomaly (out of {result.ensemble.total_models} total)</p>
                    <p className="explanation-text">
                        {getMVTecExplanation(result.ensemble.prediction === 'Normal', result.ensemble.confidence)}
                    </p>
                </div>
            </div>
            
            {/* Individual Models */}
            <div className="models-breakdown mt-4">
                <h4 style={{borderBottom: '2px solid #e0e0e0', paddingBottom: '10px'}}>🤖 Individual Model Results</h4>
                <div className="model-cards mt-3">
                    {Object.entries(result.models).map(([name, data]) => {
                        const color = data.prediction === 'Normal' ? '#27ae60' : '#e74c3c';
                        return (
                            <div key={name} className="model-card">
                                <div className="model-header">
                                    <span className="model-name" style={{textTransform: 'capitalize'}}>{name.replace('_', ' ')}</span>
                                    <span className="model-badge" style={{background: color}}>{data.prediction}</span>
                                </div>
                                <div className="model-confidence mt-2">
                                    {data.confidence && (
                                        <>
                                            <small>Confidence: {data.confidence}%</small>
                                            <div className="mini-confidence-bar">
                                                <div style={{width: `${data.confidence}%`, background: color}}></div>
                                            </div>
                                        </>
                                    )}
                                    {data.score !== undefined && data.score !== null && (
                                        <small className="model-score mt-2 d-block text-muted">
                                            Anomaly Score: {Number(data.score).toFixed(4)}
                                        </small>
                                    )}
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