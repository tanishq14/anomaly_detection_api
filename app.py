"""
============================================================================
FLASK API FOR MULTI-DOMAIN ANOMALY DETECTION
============================================================================
Supports: Network Intrusion, MVTec Quality Inspection, X-ray Analysis
Author: Tanishq Rahul Shelke
Version: 1.0
============================================================================
""" 
from flask import Flask, request, render_template, jsonify
import os
import logging
from datetime import datetime

# Import configuration
from config import config

# Import utility functions
from utils import validate_image, validate_network_data, format_response, save_upload

# Import pipeline modules
from modules import network_pipeline, mvtec_pipeline, xray_pipeline

# ============================================================================
# INITIALIZE FLASK APP
# ============================================================================

app = Flask(__name__)
app.config.from_object(config['development'])  # Change to 'production' for deployment

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# ROUTES - Web Pages
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    logger.info("Home page accessed")
    return render_template('index.html')


@app.route('/network')
def network_page():
    """Network intrusion detection page"""
    logger.info("Network page accessed")
    return render_template('network.html')


@app.route('/mvtec')
def mvtec_page():
    """MVTec anomaly detection page"""
    logger.info("MVTec page accessed")
    return render_template('mvtec.html')


@app.route('/xray')
def xray_page():
    """Chest X-ray analysis page"""
    logger.info("X-ray page accessed")
    return render_template('xray.html')

# ============================================================================
# API ENDPOINTS - Predictions
# ============================================================================

@app.route('/api/predict/network', methods=['POST'])
def predict_network():
    """
    Network intrusion detection endpoint
    
    Request: JSON with network traffic features
    Response: Predictions from all models + ensemble result
    """
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            logger.warning("Network prediction: No data provided")
            return format_response(False, error="No data provided", code=400)
        
        # Validate data
        is_valid, error_msg, cleaned_data = validate_network_data(data)
        if not is_valid:
            logger.warning(f"Network prediction: Validation failed - {error_msg}")
            return format_response(False, error=error_msg, code=400)
        
        # Run prediction
        logger.info(f"Network prediction: {cleaned_data.get('proto', 'unknown')} - {cleaned_data.get('service', 'unknown')}")
        result = network_pipeline.predict_network(cleaned_data)
        
        logger.info(f"Network prediction successful: {result['ensemble']['prediction']}")
        return format_response(True, data=result)
        
    except Exception as e:
        logger.error(f"Network prediction error: {str(e)}", exc_info=True)
        return format_response(False, error=f"Prediction failed: {str(e)}", code=500)


@app.route('/api/predict/mvtec', methods=['POST'])
def predict_mvtec():
    """
    MVTec image anomaly detection endpoint
    
    Request: multipart/form-data with 'file' field
    Response: Predictions from all models + ensemble result
    """
    filepath = None
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            logger.warning("MVTec prediction: No file uploaded")
            return format_response(False, error="No file uploaded", code=400)
        
        file = request.files['file']
        
        # Validate image
        is_valid, error_msg = validate_image(file)
        if not is_valid:
            logger.warning(f"MVTec prediction: Validation failed - {error_msg}")
            return format_response(False, error=error_msg, code=400)
        
        # Save uploaded file
        filepath = save_upload(file, app.config['UPLOAD_FOLDER'])
        
        # Run prediction
        logger.info(f"MVTec prediction: {file.filename}")
        result = mvtec_pipeline.predict_mvtec(filepath)
        
        logger.info(f"MVTec prediction successful: {result['ensemble']['prediction']}")
        return format_response(True, data=result)
        
    except Exception as e:
        logger.error(f"MVTec prediction error: {str(e)}", exc_info=True)
        return format_response(False, error=f"Prediction failed: {str(e)}", code=500)
        
    finally:
        # Clean up uploaded file
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.debug(f"Cleaned up temp file: {filepath}")
            except Exception as e:
                logger.warning(f"Failed to remove temp file: {e}")


@app.route('/api/predict/xray', methods=['POST'])
def predict_xray():
    """
    Chest X-ray anomaly detection endpoint
    
    Request: multipart/form-data with 'file' field
    Response: Predictions from all models (unsupervised + supervised) + ensemble
    """
    filepath = None
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            logger.warning("X-ray prediction: No file uploaded")
            return format_response(False, error="No file uploaded", code=400)
        
        file = request.files['file']
        
        # Validate image
        is_valid, error_msg = validate_image(file)
        if not is_valid:
            logger.warning(f"X-ray prediction: Validation failed - {error_msg}")
            return format_response(False, error=error_msg, code=400)
        
        # Save uploaded file
        filepath = save_upload(file, app.config['UPLOAD_FOLDER'])
        
        # Run prediction
        logger.info(f"X-ray prediction: {file.filename}")
        result = xray_pipeline.predict_xray(filepath)
        
        logger.info(f"X-ray prediction successful: {result['ensemble']['prediction']}")
        return format_response(True, data=result)
        
    except Exception as e:
        logger.error(f"X-ray prediction error: {str(e)}", exc_info=True)
        return format_response(False, error=f"Prediction failed: {str(e)}", code=500)
        
    finally:
        # Clean up uploaded file
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.debug(f"Cleaned up temp file: {filepath}")
            except Exception as e:
                logger.warning(f"Failed to remove temp file: {e}")

# ============================================================================
# API ENDPOINTS - Health & Info
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'endpoints': {
            'network': '/api/predict/network',
            'mvtec': '/api/predict/mvtec',
            'xray': '/api/predict/xray'
        }
    })


@app.route('/api/models/info', methods=['GET'])
def models_info():
    """Get information about loaded models"""
    try:
        info = {
            'network': {
                'dataset': 'UNSW-NB15',
                'models': ['IsolationForest', 'OneClassSVM', 'EllipticEnvelope', 'LocalOutlierFactor'],
                'ensemble': 'Majority Voting',
                'total_models': 4
            },
            'mvtec': {
                'dataset': 'MVTec AD',
                'models': ['IsolationForest', 'OneClassSVM', 'EllipticEnvelope', 'LocalOutlierFactor'],
                'feature_extractor': 'ResNet34',
                'ensemble': 'Majority Voting',
                'total_models': 4
            },
            'xray': {
                'dataset': 'NIH Chest X-ray14',
                'unsupervised_models': ['Autoencoder', 'IsolationForest', 'OneClassSVM', 'EllipticEnvelope', 'LocalOutlierFactor'],
                'supervised_models': ['DecisionTree', 'KNN'],
                'ensemble': 'Majority Voting (Unsupervised)',
                'total_models': 7
            }
        }
        return jsonify(info)
    except Exception as e:
        logger.error(f"Models info error: {str(e)}")
        return format_response(False, error=str(e), code=500)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.url}")
    return format_response(False, error="Endpoint not found", code=404)


@app.errorhandler(413)
def too_large(error):
    """Handle file too large errors"""
    logger.warning("413 error: File too large")
    return format_response(False, error="File too large. Max size: 16MB", code=413)


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 internal error: {str(error)}", exc_info=True)
    return format_response(False, error="Internal server error", code=500)

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 ANOMALY DETECTION API v2.0")
    print("=" * 80)
    
    logger.info("Starting Anomaly Detection API...")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"Debug mode: {app.config['DEBUG']}")
    
    print("\n📊 Available Endpoints:")
    print("   - Homepage:        http://localhost:5000/")
    print("   - Network:         http://localhost:5000/network")
    print("   - MVTec:           http://localhost:5000/mvtec")
    print("   - X-ray:           http://localhost:5000/xray")
    print("\n🔌 API Endpoints:")
    print("   - POST /api/predict/network")
    print("   - POST /api/predict/mvtec")
    print("   - POST /api/predict/xray")
    print("   - GET  /api/health")
    print("   - GET  /api/models/info")
    print("\n" + "=" * 80 + "\n")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
