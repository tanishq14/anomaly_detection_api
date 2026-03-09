"""
NIH Chest X-ray Anomaly Detection Pipeline
Supports: Unsupervised (Autoencoder, IsolationForest, OCSVM, EllipticEnvelope, LOF)
         Supervised (DecisionTree, KNN)

Author: Tanishq Rahul Shelke
"""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import pickle
import os

# ============================================================================
# DISEASE INFORMATION DATABASE
# ============================================================================

DISEASE_INFO = {
    'No Finding': {
        'severity': 'normal',
        'severity_level': 0,
        'icon': '✅',
        'color': '#27ae60',
        'description': 'No significant abnormalities detected in the chest X-ray',
        'common_name': 'Normal/Healthy',
        'clinical_notes': 'The lungs, heart, and chest structures appear within normal limits.',
        'prevalence': 'Baseline',
        'recommendation': 'No immediate action required. Continue routine health monitoring.'
    },
    
    'Atelectasis': {
        'severity': 'moderate',
        'severity_level': 2,
        'icon': '🫁',
        'color': '#f39c12',
        'description': 'Partial or complete collapse of a lung or lobe of a lung',
        'common_name': 'Collapsed Lung Area',
        'clinical_notes': 'Occurs when air sacs (alveoli) cannot expand properly. May be caused by blockage, pressure, or scarring.',
        'causes': ['Mucus plug', 'Foreign object', 'Tumor', 'Post-surgery'],
        'prevalence': 'Common (5-10% of hospitalized patients)',
        'recommendation': 'Clinical correlation recommended. May require breathing exercises, chest physiotherapy, or bronchoscopy.'
    },
    
    'Cardiomegaly': {
        'severity': 'moderate',
        'severity_level': 2,
        'icon': '❤️',
        'color': '#e74c3c',
        'description': 'Enlargement of the heart visible on chest X-ray',
        'common_name': 'Enlarged Heart',
        'clinical_notes': 'Heart size exceeds normal cardiothoracic ratio (>0.5). May indicate various cardiac conditions.',
        'causes': ['Hypertension', 'Heart valve disease', 'Cardiomyopathy', 'Chronic heart failure'],
        'prevalence': 'Common (2-3% of general population)',
        'recommendation': 'Cardiology evaluation recommended. Echocardiogram and ECG may be needed.'
    },
    
    'Effusion': {
        'severity': 'moderate',
        'severity_level': 2,
        'icon': '💧',
        'color': '#3498db',
        'description': 'Abnormal accumulation of fluid in the pleural space (between lung and chest wall)',
        'common_name': 'Pleural Effusion/Fluid Buildup',
        'clinical_notes': 'Can be transudate (low protein) or exudate (high protein). Blunting of costophrenic angle is typical.',
        'causes': ['Congestive heart failure', 'Pneumonia', 'Cancer', 'Kidney disease', 'Liver cirrhosis'],
        'prevalence': 'Common (1.5 million cases/year in US)',
        'recommendation': 'Further evaluation needed. May require thoracentesis (fluid sampling) to determine cause.'
    },
    
    'Infiltration': {
        'severity': 'moderate',
        'severity_level': 2,
        'icon': '🦠',
        'color': '#e67e22',
        'description': 'Presence of abnormal substances in the lung tissue (cells, fluid, or other material)',
        'common_name': 'Lung Infiltrate',
        'clinical_notes': 'Appears as increased density on X-ray. Can be focal or diffuse. Non-specific finding.',
        'causes': ['Infection', 'Inflammation', 'Aspiration', 'Pulmonary edema', 'Cancer'],
        'prevalence': 'Common finding (varies by cause)',
        'recommendation': 'Clinical correlation required. CT scan and laboratory tests may be needed to identify cause.'
    },
    
    'Mass': {
        'severity': 'high',
        'severity_level': 3,
        'icon': '🔴',
        'color': '#c0392b',
        'description': 'Abnormal growth or lesion in the lung tissue larger than 3cm',
        'common_name': 'Lung Mass/Tumor',
        'clinical_notes': 'Defined as opacity >3cm. Requires differentiation between benign and malignant causes.',
        'causes': ['Lung cancer', 'Metastatic cancer', 'Abscess', 'Granuloma', 'Hamartoma'],
        'prevalence': 'Less common but serious (depends on cause)',
        'recommendation': 'Urgent evaluation required. CT scan, PET scan, and possible biopsy needed.'
    },
    
    'Nodule': {
        'severity': 'moderate',
        'severity_level': 2,
        'icon': '⚪',
        'color': '#95a5a6',
        'description': 'Small, round or oval-shaped growth in the lung, less than 3cm in diameter',
        'common_name': 'Lung Nodule',
        'clinical_notes': 'Most are benign, but require monitoring. Size, shape, and growth rate are important factors.',
        'causes': ['Granuloma', 'Infection scar', 'Benign tumor', 'Early cancer', 'Metastasis'],
        'prevalence': 'Common (found in 50% of CT scans of smokers over 50)',
        'recommendation': 'Follow-up imaging recommended. Management depends on size, characteristics, and risk factors.'
    },
    
    'Pneumonia': {
        'severity': 'high',
        'severity_level': 3,
        'icon': '🚨',
        'color': '#e74c3c',
        'description': 'Infection of the lung tissue causing inflammation and fluid accumulation in air sacs',
        'common_name': 'Lung Infection/Pneumonia',
        'clinical_notes': 'Appears as consolidation, often with air bronchograms. Can be lobar, bronchial, or interstitial.',
        'causes': ['Bacteria (Streptococcus pneumoniae)', 'Viruses (Influenza, COVID-19)', 'Fungi', 'Aspiration'],
        'prevalence': 'Very common (450 million cases/year worldwide)',
        'recommendation': 'Immediate treatment needed. Antibiotics (if bacterial), supportive care, hospitalization if severe.'
    },
    
    'Pneumothorax': {
        'severity': 'high',
        'severity_level': 3,
        'icon': '💨',
        'color': '#e74c3c',
        'description': 'Presence of air in the pleural space causing partial or complete lung collapse',
        'common_name': 'Collapsed Lung',
        'clinical_notes': 'Visible as lucency (dark area) with absent lung markings. White visceral pleural line may be seen.',
        'causes': ['Trauma', 'Spontaneous (tall, thin males)', 'COPD', 'Medical procedures', 'Ruptured bleb'],
        'prevalence': 'Uncommon (20-30 per 100,000 per year)',
        'recommendation': 'Medical emergency if large. May require chest tube insertion, oxygen therapy, or surgery.'
    },
    
    'Consolidation': {
        'severity': 'moderate',
        'severity_level': 2,
        'icon': '🌫️',
        'color': '#7f8c8d',
        'description': 'Air spaces in the lung are filled with fluid, pus, blood, or cells instead of air',
        'common_name': 'Lung Consolidation',
        'clinical_notes': 'Appears as homogeneous increased density. Air bronchograms often visible.',
        'causes': ['Pneumonia', 'Pulmonary edema', 'Hemorrhage', 'Aspiration', 'Lung cancer'],
        'prevalence': 'Common (primary feature of pneumonia)',
        'recommendation': 'Identify underlying cause. Treatment depends on etiology (infection, fluid overload, etc.).'
    },
    
    'Edema': {
        'severity': 'moderate',
        'severity_level': 2,
        'icon': '💧',
        'color': '#3498db',
        'description': 'Accumulation of fluid in the lung tissue (pulmonary edema)',
        'common_name': 'Fluid in Lungs/Pulmonary Edema',
        'clinical_notes': 'Bilateral, symmetric hazy opacities. Kerley B lines, peribronchial cuffing, and bat-wing pattern may be seen.',
        'causes': ['Congestive heart failure (cardiogenic)', 'ARDS (non-cardiogenic)', 'Kidney failure', 'Altitude sickness'],
        'prevalence': 'Common in heart failure patients',
        'recommendation': 'Urgent treatment needed. Diuretics, oxygen therapy, treat underlying cause (heart failure, etc.).'
    },
    
    'Emphysema': {
        'severity': 'moderate',
        'severity_level': 2,
        'icon': '🫁',
        'color': '#f39c12',
        'description': 'Chronic lung condition where air sacs are damaged, causing breathing difficulty',
        'common_name': 'Emphysema (COPD)',
        'clinical_notes': 'Hyperinflation, flattened diaphragm, increased lucency, reduced vascular markings. Part of COPD.',
        'causes': ['Smoking (90%)', 'Alpha-1 antitrypsin deficiency', 'Air pollution', 'Occupational exposure'],
        'prevalence': 'Common (3.5% of global population has COPD)',
        'recommendation': 'Smoking cessation essential. Bronchodilators, pulmonary rehabilitation, oxygen therapy if needed.'
    },
    
    'Fibrosis': {
        'severity': 'moderate',
        'severity_level': 2,
        'icon': '🧬',
        'color': '#9b59b6',
        'description': 'Scarring and thickening of lung tissue, making breathing difficult',
        'common_name': 'Pulmonary Fibrosis/Lung Scarring',
        'clinical_notes': 'Reticular pattern, honeycombing, decreased lung volumes. Progressive and often irreversible.',
        'causes': ['Idiopathic (unknown)', 'Environmental exposures (asbestos)', 'Autoimmune diseases', 'Medications', 'Radiation'],
        'prevalence': 'Uncommon (5 million people worldwide)',
        'recommendation': 'Pulmonary function tests needed. Antifibrotic medications, oxygen therapy, lung transplant in severe cases.'
    },
    
    'Pleural_Thickening': {
        'severity': 'low',
        'severity_level': 1,
        'icon': '📏',
        'color': '#95a5a6',
        'description': 'Thickening of the pleural membrane (lining around the lungs)',
        'common_name': 'Thickened Pleura',
        'clinical_notes': 'Dense line along chest wall or diaphragm. Can be focal or diffuse, unilateral or bilateral.',
        'causes': ['Previous infection (TB, pneumonia)', 'Asbestos exposure', 'Trauma', 'Hemothorax', 'Empyema'],
        'prevalence': 'Common after pleural inflammation',
        'recommendation': 'Usually benign finding. Monitor if asbestos exposure. No treatment unless symptomatic.'
    },
    
    'Hernia': {
        'severity': 'low',
        'severity_level': 1,
        'icon': '🔺',
        'color': '#e67e22',
        'description': 'Protrusion of abdominal contents through the diaphragm into the chest cavity',
        'common_name': 'Hiatal/Diaphragmatic Hernia',
        'clinical_notes': 'Most commonly hiatal hernia (stomach through esophageal hiatus). May see air-fluid level or soft tissue mass.',
        'causes': ['Congenital weakness', 'Increased abdominal pressure', 'Trauma', 'Age-related muscle weakness'],
        'prevalence': 'Common (60% of people >50 have hiatal hernia)',
        'recommendation': 'Usually asymptomatic. Surgery only if symptomatic (GERD, obstruction, strangulation).'
    }
}

# ============================================================================
# HELPER FUNCTIONS FOR DISEASE INFORMATION
# ============================================================================

def get_disease_info(disease_name):
    """Get complete information about a disease"""
    return DISEASE_INFO.get(disease_name, {
        'severity': 'unknown',
        'severity_level': 0,
        'icon': '❓',
        'color': '#95a5a6',
        'description': 'Disease information not available',
        'common_name': disease_name,
        'clinical_notes': 'Please consult a medical professional.',
        'recommendation': 'Professional medical evaluation recommended.'
    })

def get_disease_severity_color(disease_name):
    """Return color code based on disease severity"""
    info = get_disease_info(disease_name)
    return info.get('color', '#95a5a6')

def format_disease_report(disease_name, confidence=None):
    """Format a comprehensive disease report for display"""
    info = get_disease_info(disease_name)
    
    report = {
        'disease': disease_name,
        'common_name': info.get('common_name', disease_name),
        'icon': info.get('icon', '❓'),
        'color': info.get('color', '#95a5a6'),
        'severity': info.get('severity', 'unknown'),
        'severity_level': info.get('severity_level', 0),
        'description': info.get('description', 'No description available'),
        'clinical_notes': info.get('clinical_notes', ''),
        'recommendation': info.get('recommendation', 'Consult a healthcare professional')
    }
    
    if confidence is not None:
        report['confidence'] = round(confidence, 2)
    
    if 'causes' in info:
        report['common_causes'] = info['causes']
    
    if 'prevalence' in info:
        report['prevalence'] = info['prevalence']
    
    return report
# ============================================================================
# Dataset configuration
# ============================================================================
DATASET_CONFIG = {
    'data_dir': 'datasets/xray/archive/images_008/images/',
    'metadata_path': 'archive/Data_Entry_2017.csv',
    'image_size': 224,
    'classes': ['No Finding', 'Atelectasis', 'Cardiomegaly', 'Effusion', 'Infiltration',
                'Mass', 'Nodule', 'Pneumonia', 'Pneumothorax', 'Consolidation', 
                'Edema', 'Emphysema', 'Fibrosis', 'Pleural_Thickening', 'Hernia']
}

# Model paths
MODEL_PATHS = {
    # Unsupervised
    'autoencoder': 'models/xray/autoencoder.pt',
    'isolation_forest': 'models/xray/isolation_forest.pkl',
    'ocsvm': 'models/xray/ocsvm.pkl',
    'elliptic_envelope': 'models/xray/elliptic_envelope.pkl',
    'elliptic_pca': 'models/xray/elliptic_pca.pkl',
    'lof': 'models/xray/lof.pkl',
    
    # Supervised
    # 'linear_regression': 'models/xray/linear_regression.pt',
    # 'logistic_regression': 'models/xray/logistic_regression.pt',
    # 'svm': 'models/xray/svm.pt',
    'decision_tree': 'models/xray/dt_model.pkl',
    'knn': 'models/xray/knn_model.pkl'
}


# ============================================================================
# AUTOENCODER MODEL
# ============================================================================

class Autoencoder(nn.Module):
    """PyTorch Autoencoder for anomaly detection"""
    def __init__(self, input_dim=224*224):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 256), 
            nn.ReLU(),
            nn.Linear(256, 64), 
            nn.ReLU(),
            nn.Linear(64, 16)
        )
        self.decoder = nn.Sequential(
            nn.Linear(16, 64), 
            nn.ReLU(),
            nn.Linear(64, 256), 
            nn.ReLU(),
            nn.Linear(256, input_dim)
        )
    
    def forward(self, x):
        return self.decoder(self.encoder(x))

# ============================================================================
# MAIN DETECTOR CLASS
# ============================================================================

class ChestXrayAnomalyDetector:
    def __init__(self):
        """Initialize all models and preprocessing"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models = {}
        self.torch_models = {}
        self.pca = None
        self.autoencoder_threshold = 0.05

        print(f"🔧 Initializing Chest X-ray Anomaly Detector on {self.device}")
        
        # Load Autoencoder
        if os.path.exists(MODEL_PATHS['autoencoder']):
            try:
                self.torch_models['autoencoder'] = Autoencoder()
                self.torch_models['autoencoder'].load_state_dict(
                    torch.load(MODEL_PATHS['autoencoder'], map_location=self.device)
                )
                self.torch_models['autoencoder'].eval().to(self.device)
                print("Loaded Autoencoder")
            except Exception as e:
                print(f"✗ Failed to load Autoencoder: {e}")
        
        # Load sklearn models
        for model_name, path in MODEL_PATHS.items():
            if model_name in ['autoencoder']: 
                continue
            
            if os.path.exists(path):
                try:
                    with open(path, 'rb') as f:
                        if model_name == 'elliptic_pca':
                            self.pca = pickle.load(f)
                            print(f"Loaded PCA for EllipticEnvelope")
                        else:
                            self.models[model_name] = pickle.load(f)
                            print(f"✓ Loaded {model_name}")
                except Exception as e:
                    print(f"✗ Failed to load {model_name}: {e}")

        # Preprocessing transform
        self.transform = transforms.Compose([
            transforms.Resize((DATASET_CONFIG['image_size'], DATASET_CONFIG['image_size'])),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])
        ])

        print(f"🎯 Loaded {len(self.models)} sklearn models + {len(self.torch_models)} torch models")
    
    def preprocess_image(self, image_path):
        """Load and preprocess X-ray image"""
        try:
            img = Image.open(image_path).convert('L')  # Convert to grayscale
            img_tensor = self.transform(img)
            img_flat = img_tensor.flatten().unsqueeze(0).to(self.device)
            return img_flat
        except Exception as e:
            raise RuntimeError(f"Error preprocessing image: {e}")
    
    def predict_all(self, image_path):
        """
        Run ALL models and return comprehensive results + ensemble prediction
        
        Args:
            image_path: Path to chest X-ray image
        
        Returns:
            dict: {
                'ensemble': {'prediction': 'Normal/Anomaly', 'confidence': float, 'votes': dict},
                'unsupervised_models': {...},
                'supervised_models': {...}
            }
        """
        img_tensor = self.preprocess_image(image_path)
        features_numpy = img_tensor.cpu().numpy()
        
        unsupervised_results = {}
        supervised_results = {}
        predictions = []
        
        # =============================================================
        # UNSUPERVISED MODELS
        # =============================================================
        
        # 1. Autoencoder
        if 'autoencoder' in self.torch_models:
            try:
                with torch.no_grad():
                    recon = self.torch_models['autoencoder'](img_tensor)
                    mse = torch.mean((img_tensor - recon)**2).item()
                
                pred = -1 if mse > self.autoencoder_threshold else 1
                unsupervised_results['autoencoder'] = {
                    'prediction': 'Anomaly' if pred == -1 else 'Normal',
                    'reconstruction_error': float(mse),
                    'threshold': self.autoencoder_threshold,
                    'confidence': self._calculate_ae_confidence(mse),
                    'raw_prediction': int(pred),
                    'method': 'Deep Learning (Autoencoder)'
                }
                predictions.append(pred)
            except Exception as e:
                print( f"Autoencoder prediction failed: {e}")

        # 2. IsolationForest
        if 'isolation_forest' in self.models:
            try:
                model = self.models['isolation_forest']
                pred = model.predict(features_numpy)[0]
                score = float(model.score_samples(features_numpy)[0]) if hasattr(model, 'score_samples') else None
                
                unsupervised_results['isolation_forest'] = {
                    'prediction': 'Normal' if pred == 1 else 'Anomaly',
                    'score': score,
                    'confidence': self._calculate_confidence(score),
                    'raw_prediction': int(pred),
                    'method': 'Isolation Forest'
                }
                predictions.append(pred)
            except Exception as e:
                print( f"IsolationForest prediction failed: {e}")
        
        # 3. OneClassSVM
        if 'ocsvm' in self.models:
            try:
                model = self.models['ocsvm']
                pred = model.predict(features_numpy)[0]
                score = float(model.decision_function(features_numpy)[0]) if hasattr(model, 'decision_function') else None
                
                unsupervised_results['ocsvm'] = {
                    'prediction': 'Normal' if pred == 1 else 'Anomaly',
                    'score': score,
                    'confidence': self._calculate_confidence(score),
                    'raw_prediction': int(pred),
                    'method': 'One-Class SVM'
                }
                predictions.append(pred)
            except Exception as e:
                print( f"OneClassSVM prediction failed: {e}")
        
        # 4. EllipticEnvelope (with PCA)
        if 'elliptic_envelope' in self.models:
            try:
                model = self.models['elliptic_envelope']
                feat = self.pca.transform(features_numpy) if self.pca else features_numpy
                pred = model.predict(feat)[0]
                score = float(model.decision_function(feat)[0]) if hasattr(model, 'decision_function') else None
                
                unsupervised_results['elliptic_envelope'] = {
                    'prediction': 'Normal' if pred == 1 else 'Anomaly',
                    'score': score,
                    'confidence': self._calculate_confidence(score),
                    'raw_prediction': int(pred),
                    'method': 'Gaussian Distribution (Elliptic Envelope)'
                }
                predictions.append(pred)
            except Exception as e:
                print( f"EllipticEnvelope prediction failed: {e}")
        
        # 5. LocalOutlierFactor
        if 'lof' in self.models:
            try:
                model = self.models['lof']

                if not getattr(model, 'novelty', False):
                    raise ValueError("Model was trained with noelty=False. Must be retrained with novelty=True to predict on new X-ray images.")
                
                pred = model.predict(features_numpy)[0]
                score = float(model.decision_function(features_numpy)[0]) if hasattr(model, 'decision_function') else None
                
                unsupervised_results['lof'] = {
                    'prediction': 'Normal' if pred == 1 else 'Anomaly',
                    'score': score,
                    'confidence': self._calculate_confidence(score),
                    'raw_prediction': int(pred),
                    'method': 'Density-Based (Local Outlier Factor)'
                }
                predictions.append(pred)
            except Exception as e:
                print( f"LOF prediction failed: {e}")
        
        # =============================================================
        # SUPERVISED MODELS
        # =============================================================

        # 6. DecisionTree
        if 'decision_tree' in self.models:
            try:
                model = self.models['decision_tree']
                pred = model.predict(features_numpy)[0]
                proba = model.predict_proba(features_numpy)[0] if hasattr(model, 'predict_proba') else None
                
                disease_name = DATASET_CONFIG['classes'][pred] if pred < len(DATASET_CONFIG['classes']) else 'Unknown'
                confidence = max(proba) * 100 if proba is not None else None

                supervised_results['decision_tree'] = {
                    'prediction': 'Normal' if pred == 0 else 'Anomaly',
                    'class_index': int(pred),
                    'probability': proba.tolist() if proba is not None else None,
                    'confidence': confidence,
                    'method': 'Tree-Based Classification',
                    'disease_info': format_disease_report(disease_name, confidence)
            }
            except Exception as e:
                print( f"DecisionTree prediction failed: {e}")
        
        # 7. KNN
        if 'knn' in self.models:
            try:
                model = self.models['knn']
                pred = model.predict(features_numpy)[0]
                proba = model.predict_proba(features_numpy)[0] if hasattr(model, 'predict_proba') else None
                
                disease_name = DATASET_CONFIG['classes'][pred] if pred < len(DATASET_CONFIG['classes']) else 'Unknown'
                confidence = max(proba) * 100 if proba is not None else None

                supervised_results['knn'] = {
                    'prediction': 'Normal' if pred == 0 else 'Anomaly',
                    'class': int(pred),
                    'probability': proba.tolist() if proba is not None else None,
                    'confidence': confidence,
                    'method': 'K-Nearest Neighbors Classification',
                    'disease_info': format_disease_report(disease_name, confidence)
            }
            except Exception as e:
                print( f"KNN prediction failed: {e}")
        
        # =============================================================
        # Ensemble: Majority Voting (unsupervised only)
        # =============================================================
        normal_votes = predictions.count(1)
        anomaly_votes = predictions.count(-1)
        ensemble_pred = 'Normal' if normal_votes > anomaly_votes else 'Anomaly'
        ensemble_confidence = max(normal_votes, anomaly_votes) / len(predictions) * 100 if predictions else 0
        
        # Image metadata
        image_info = {
            'filename': os.path.basename(image_path),
            'image_size': f"{DATASET_CONFIG['image_size']}x{DATASET_CONFIG['image_size']}",
            'preprocessing': 'Grayscale, Normalized [-1, 1]',
            'total_models_run': len(unsupervised_results) + len(supervised_results)
        }

        return {
            'ensemble': {
                'prediction': ensemble_pred,
                'confidence': round(ensemble_confidence, 2),
                'votes': {
                    'Normal': normal_votes,
                    'Anomaly': anomaly_votes
                },
                'total_models': len(predictions),
                'interpretation': self._get_ensemble_interpretation(ensemble_pred, ensemble_confidence)
            },
            'unsupervised_models': unsupervised_results,
            'supervised_models': supervised_results,
            'image_info': image_info,
            'medical_disclaimer': 'This is a research tool. Not approved for clinical diagnosis. Always consult qualified healthcare professionals.'
        }
    
    def _calculate_confidence(self, score):
        """Convert anomaly score to confidence percentage"""
        if score is None:
            return None
        confidence = 1 / (1 + np.exp(-abs(score)))
        return round(confidence * 100, 2)
    
    def _calculate_ae_confidence(self, mse):
        """Calculate confidence based on reconstruction error"""
        if mse < self.autoencoder_threshold * 0.5:
            return 95.0
        elif mse > self.autoencoder_threshold * 2:
            return 95.0
        else:
            # Linear interpolation around threshold
            distance_from_threshold = abs(mse - self.autoencoder_threshold)
            max_distance = self.autoencoder_threshold
            confidence = 50 + (distance_from_threshold / max_distance) * 45
            return round(min(confidence, 95.0), 2)
    
    def _get_ensemble_interpretation(self, prediction, confidence):
        """Provide human-readable interpretation"""
        if prediction == 'Normal':
            if confidence >= 80:
                return "Strong consensus: X-ray appears normal across multiple detection methods."
            elif confidence >= 60:
                return "Moderate consensus: Most models indicate normal findings."
            else:
                return "Weak consensus: Results are mixed. Professional review recommended."
        else:
            if confidence >= 80:
                return "Strong consensus: Potential abnormality detected by multiple models. Further evaluation strongly recommended."
            elif confidence >= 60:
                return "Moderate consensus: Some models detected potential abnormalities. Clinical correlation advised."
            else:
                return "Weak consensus: Results are inconclusive. Professional medical review necessary."

# ============================================================================
# SINGLETON PATTERN
# ============================================================================

_detector = None

def get_detector():
    """Get or create detector instance (singleton)"""
    global _detector
    if _detector is None:
        _detector = ChestXrayAnomalyDetector()
    return _detector

def predict_xray(image_path):
    """
    Main prediction function - runs ALL models and returns comprehensive results
    
    Args:
        image_path: Path to chest X-ray image file
        
    Returns:
        dict: Complete analysis results with ensemble, unsupervised, and supervised predictions
    """
    detector = get_detector()
    return detector.predict_all(image_path)
# ============================================================================
# UTILITY FUNCTIONS FOR API
# ============================================================================

def get_available_models():
    """Return list of available models"""
    detector = get_detector()
    return {
        'unsupervised': list(detector.models.keys()) + list(detector.torch_models.keys()),
        'supervised': [k for k in detector.models.keys() if k in ['decision_tree', 'knn']],
        'total': len(detector.models) + len(detector.torch_models)
    }

def get_supported_diseases():
    """Return list of detectable diseases with info"""
    return {disease: get_disease_info(disease) for disease in DATASET_CONFIG['classes']}

def validate_image(image_path):
    """Validate if image can be processed"""
    if not os.path.exists(image_path):
        return False, "Image file not found"
    
    try:
        img = Image.open(image_path)
        img.verify()
        return True, "Valid image"
    except Exception as e:
        return False, f"Invalid image: {str(e)}"

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("NIH CHEST X-RAY ANOMALY DETECTION PIPELINE")
    print("="*80)
    
    # Get available models
    available = get_available_models()
    print(f"\n📊 Available Models: {available['total']}")
    print(f"   - Unsupervised: {', '.join(available['unsupervised'])}")
    print(f"   - Supervised: {', '.join(available['supervised'])}")
    
    # Get supported diseases
    print(f"\n🏥 Detectable Conditions: {len(DATASET_CONFIG['classes'])}")
    for disease in DATASET_CONFIG['classes'][:5]:  # Show first 5
        info = get_disease_info(disease)
        print(f"   {info['icon']} {disease}: {info['description'][:50]}...")
    
    print("\n" + "="*80)
    print("Pipeline ready for predictions!")
    print("="*80)