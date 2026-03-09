import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import mode
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, confusion_matrix, ConfusionMatrixDisplay, RocCurveDisplay, precision_recall_curve, PrecisionRecallDisplay
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
from sklearn.decomposition import PCA
from sklearn.covariance import EllipticEnvelope
from sklearn.neighbors import LocalOutlierFactor
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
import torchvision.models as models
import torch
from PIL import Image
import pickle

# Load models once at module import
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using Device: {device}")

# Product category information for users
CATEGORY_INFO = {
    'bottle': {'icon': '🍾', 'description': 'Glass bottles - detects cracks, contamination'},
    'cable': {'icon': '🔌', 'description': 'Electrical cables - detects cuts, bent cables'},
    'capsule': {'icon': '💊', 'description': 'Pharmaceutical capsules - detects cracks, pokes'},
    'carpet': {'icon': '🧱', 'description': 'Carpets/Fabrics - detects color defects, cuts'},
    'grid': {'icon': '⚡', 'description': 'Metal grids - detects bent, broken parts'},
    'hazelnut': {'icon': '🥜', 'description': 'Hazelnuts - detects cracks, holes'},
    'leather': {'icon': '🧵', 'description': 'Leather surfaces - detects cuts, folds'},
    'metal_nut': {'icon': '🔩', 'description': 'Metal nuts - detects bent, scratched parts'},
    'pill': {'icon': '💊', 'description': 'Pills/Tablets - detects cracks, contamination'},
    'screw': {'icon': '🧪', 'description': 'Screws - detects thread damage, scratches'},
    'tile': {'icon': '🟫', 'description': 'Floor tiles - detects cracks, glue strips'},
    'toothbrush': {'icon': '🪥', 'description': 'Toothbrushes - detects defective bristles'},
    'transistor': {'icon': '📱', 'description': 'Electronic components - detects damaged cases'},
    'wood': {'icon': '🪵', 'description': 'Wood surfaces - detects scratches, color defects'},
    'zipper': {'icon': '🤐', 'description': 'Zippers - detects broken teeth, fabric defects'}
}

def get_category_from_filename(filename):
    """Extract category from filename or return 'unknown'"""
    filename_lower = filename.lower()
    for category in DATASET_CONFIG['categories']:
        if category in filename_lower:
            return category
    return 'unknown'


"""
MVTec Anomaly Detection Pipeline
Supports: OneClassSVM, IsolationForest, EllipticEnvelope, LOF, Ensemble
"""

# Dataset configuration
DATASET_CONFIG = {
    'data_dir': '.datasets/mvtec/mvtec_anomaly_detection',
    'categories': ['bottle', 'cable', 'capsule', 'carpet', 'grid', 
                  'hazelnut', 'leather', 'metal_nut', 'pill', 'screw',
                  'tile', 'toothbrush', 'transistor', 'wood', 'zipper'],
    'image_size': 224
}

# Model paths
MODEL_PATHS = {
    'resnet_feature_extractor': 'models/mvtec/resnet34_feature_extractor.pt',
    'scaler': 'models/mvtec/scaler.pkl',
    'pca': 'models/mvtec/pca.pkl',  # General PCA for dimensionality reduction
    'ocsvm': 'models/mvtec/ocsvm.pkl',
    'isolation_forest': 'models/mvtec/isolation_forest.pkl',
    'isolation_pca': 'models/mvtec/isolation_pca.pkl',  # PCA for IsolationForest
    'elliptic_envelope': 'models/mvtec/elliptic_envelope.pkl',
    'elliptic_pca': 'models/mvtec/elliptic_pca.pkl',  # PCA for EllipticEnvelope
    'lof': 'models/mvtec/lof.pkl'
    # 'ensemble': 'models/mvtec/ensemble.pkl' 
}

class MVTecAnomalyDetector:
    def __init__(self):
        """Initialize models and feature extractor"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models = {}
        self.scaler = None
        self.resnet = None
        self.pca = None  # General PCA for feature reduction
        self.pca_models = {}
        
        # Load ResNet feature extractor
        if os.path.exists(MODEL_PATHS['resnet_feature_extractor']):
            self.resnet = models.resnet34(weights=None)
            self.resnet.fc = torch.nn.Identity()
            self.resnet.load_state_dict(
                torch.load(MODEL_PATHS['resnet_feature_extractor'], map_location=self.device)
            )
            self.resnet.eval().to(self.device)
            print("Loaded ResNet34 feature extractor")
        
        # Load scaler
        if os.path.exists(MODEL_PATHS['scaler']):
            with open(MODEL_PATHS['scaler'], 'rb') as f:
                self.scaler = pickle.load(f)
            print("Loaded StandardScaler")
            # Debug: show fitted input dim
            print("Scaler fitted n_features_in_:", getattr(self.scaler, 'n_features_in_', None))
        
        # Load PCA for dimensionality reduction
        if os.path.exists(MODEL_PATHS['pca']):
            with open(MODEL_PATHS['pca'], 'rb') as f:
                self.pca = pickle.load(f)
            print("Loaded PCA")
            # Debug: show PCA fitted/input/output dims
            print("PCA fitted n_features_in_:", getattr(self.pca, 'n_features_in_', None),
                  "n_components_:", getattr(self.pca, 'n_components_', None))
        
        # Load all anomaly detection models
        for model_name, path in MODEL_PATHS.items():
            if model_name not in ['resnet_feature_extractor', 'scaler', 'pca'] and os.path.exists(path):
                with open(path, 'rb') as f:
                    loaded_obj = pickle.load(f)
                    if 'pca' in model_name:
                        # store PCA models in dict and also as well-known attributes
                        self.pca_models[model_name] = loaded_obj
                        # set attribute names used elsewhere in the code
                        if model_name == 'isolation_pca':
                            self.isolation_pca = loaded_obj
                        if model_name == 'elliptic_pca':
                            self.pca_elliptic = loaded_obj
                    else:
                        self.models[model_name] = loaded_obj
                print(f"✓ Loaded {model_name}")

        # Ensure per-model PCA attributes exist even if not present in files
        if not hasattr(self, 'isolation_pca'):
            self.isolation_pca = self.pca_models.get('isolation_pca')
        if not hasattr(self, 'pca_elliptic'):
            self.pca_elliptic = self.pca_models.get('elliptic_pca')

        # Debug: print per-model PCA info
        for name, p in self.pca_models.items():
            try:
                print(f"Loaded PCA model {name}: n_features_in_={getattr(p, 'n_features_in_', None)}, n_components_={getattr(p, 'n_components_', None)}")
            except Exception:
                print(f"Loaded PCA model {name}: (no shape info)")
        
        # Preprocessing transform
        self.transform = transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((DATASET_CONFIG['image_size'], DATASET_CONFIG['image_size'])),
            transforms.ToTensor(),
            transforms.Lambda(lambda x: x.repeat(3, 1, 1)),  # Convert to 3-channel
            transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
        ])
    
    def extract_features(self, image_path):
        """Extract ResNet features from image"""
        if self.resnet is None:
            raise RuntimeError("ResNet feature extractor not loaded")
        
        img = Image.open(image_path).convert('L')
        img_tensor = self.transform(img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            features = self.resnet(img_tensor).cpu().numpy().squeeze()
        # features should be shape (1, D)
        if features.ndim == 1:
            features = features.reshape(1, -1)

        raw_dim = features.shape[1]

        if self.scaler is not None:
            if hasattr(self.scaler, 'n_features_in_') and self.scaler.n_features_in_== raw_dim:
                features = self.scaler.transform(features)
            else:
                raise RuntimeError(
                    f"Scaler input dimension mismatch: expected {self.scaler.n_features_in_}, got {raw_dim}"
                )
            
        return features
    
    def predict(self, image_path, model_name='isolation_forest'):
        """
        Predict anomaly for image using specified model
        
        Args:
            image_path: Path to image file
            model_name: One of ['ocsvm', 'isolation_forest', 'elliptic_envelope', 'lof', 'all']
        
        Returns:
            dict: {'prediction': 'Normal'/'Anomaly', 'score': float, 'model': str, 'confidence': float, ...}
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Available: {list(self.models.keys())}")
        
        features = self.extract_features(image_path)
        model = self.models[model_name]
        
        # Apply PCA if needed
        if model_name in ['isolation_forest', 'elliptic_envelope']:
            pca_key = f"{model_name.split('_')[0]}_pca"
            if pca_key in self.pca_models:
                features = self.pca_models[pca_key].transform(features)
        
        # Predict
        prediction = model.predict(features)[0]
        
        # Get score
        if hasattr(model, 'score_samples'):
            score = float(model.score_samples(features)[0])
        elif hasattr(model, 'decision_function'):
            score = float(model.decision_function(features)[0])
        else:
            score = None
        
        label = 'Normal' if prediction == 1 else 'Anomaly'
        
        return {
            'prediction': label,
            'score': score,
            'model': model_name,
            'confidence': self._calculate_confidence(score)
        }
    
    def predict_all(self, image_path):
        """
        Run ALL models and return comprehensive results + ensemble prediction
        
        Args:
            image_path: Path to image file
        
        Returns:
            dict: {
                'ensemble': {'prediction': 'Normal/Anomaly', 'confidence': float, 'votes': dict, 'total_models': int},
                'models': {
                    'isolation_forest': {...},
                    'ocsvm': {...},
                    'elliptic_envelope': {...},
                    'lof': {...}
                }
            }
        
        Enhanced prediction with category detection
        
        """
        features = self.extract_features(image_path)

        results = {}
        predictions = []
        
        # 1. IsolationForest (with PCA)
        if 'isolation_forest' in self.models:
            model = self.models['isolation_forest']
            
            try:
                if hasattr(self, 'isolation_pca') and self.isolation_pca is not None:
                    feat = self.isolation_pca.transform(features)
                elif self.pca is not None:
                    feat = self.pca.transform(features)
                else:
                    feat = features
        
                pred = model.predict(feat)[0]
                score = float(model.score_samples(feat)[0]) if hasattr(model, 'score_samples') else None
                
                results['isolation_forest'] = {
                        'prediction': 'Normal' if pred == 1 else 'Anomaly',
                        'score': score,
                        'confidence': self._calculate_confidence(score),
                        'raw_prediction': int(pred)
                }
                predictions.append(pred)
    
            except Exception as e:
                print(f"Error in IsolationForest prediction: {e}")
        
        # 2. OneClassSVM
        if 'ocsvm' in self.models:
            model = self.models['ocsvm']

            try:
                pred = model.predict(features)[0]
                score = float(model.decision_function(features)[0]) if hasattr(model, 'decision_function') else None
            except ValueError:

                if self.pca is not None:
                    feat_reduced = self.pca.transform(features)
                    pred = model.predict(feat_reduced)[0]
                    score = float(model.decision_function(feat_reduced)[0]) 
                else:
                    raise

            results['ocsvm'] = {
                'prediction': 'Normal' if pred == 1 else 'Anomaly',
                'score': score,
                'confidence': self._calculate_confidence(score),
                'raw_prediction': int(pred)
            }
            predictions.append(pred)
        
        # 3. EllipticEnvelope (with PCA)
        if 'elliptic_envelope' in self.models:
            model = self.models['elliptic_envelope']

            try:
                if hasattr(self, 'pca_elliptic') and self.pca_elliptic is not None:
                    feat = self.pca_elliptic.transform(features)
                elif self.pca is not None:
                    feat = self.pca.transform(features)
                else:
                    feat = features

                pred = model.predict(feat)[0]
                score = float(model.decision_function(feat)[0]) if hasattr(model, 'decision_function') else None
                
                results['elliptic_envelope'] = {
                    'prediction': 'Normal' if pred == 1 else 'Anomaly',
                    'score': score,
                    'confidence': self._calculate_confidence(score),
                    'raw_prediction': int(pred)
                }
                predictions.append(pred)
            except Exception as e:
                print(f"Error in EllipticEnvelope prediction: {e}")
            
        # 4. LocalOutlierFactor
        if 'lof' in self.models:
            model = self.models['lof']
            # LOF predict is only available in 'novelty' mode
            pred = model.predict(features)[0]
            score = float(model.decision_function(features)[0]) if hasattr(model, 'decision_function') else None
            
            results['lof'] = {
                'prediction': 'Normal' if pred == 1 else 'Anomaly',
                'score': score,
                'confidence': self._calculate_confidence(score),
                'raw_prediction': int(pred)
            }
            predictions.append(pred)
        
        # Ensemble: Majority Voting

        if not predictions:
            return {'error':'No models available for prediction.'}
        
        normal_votes = predictions.count(1)
        anomaly_votes = predictions.count(-1)
        ensemble_pred = 'Normal' if normal_votes > anomaly_votes else 'Anomaly'
        ensemble_confidence = max(normal_votes, anomaly_votes) / len(predictions) * 100 if predictions else 0

        # Detect category from filename
        category = get_category_from_filename(os.path.basename(image_path))
        category_info = CATEGORY_INFO.get(category, {'icon': '📦', 'description': 'Product quality inspection'})
        
        return {
            'ensemble': {
            'prediction': ensemble_pred,
            'confidence': round(ensemble_confidence, 2),
            'votes': {'Normal': normal_votes, 'Anomaly': anomaly_votes},
            'total_models': len(predictions)
        },
        'models': results,
        'image_info': {
            'category': category,
            'category_icon': category_info['icon'],
            'category_description': category_info['description']
        }
    }
    
    def _calculate_confidence(self, score):
        """Convert score to confidence"""
        if score is None:
            return None
        confidence = 1 / (1 + np.exp(-abs(score)))
        return round(confidence * 100, 2)

# Singleton
_detector = None

def get_detector():
    global _detector
    if _detector is None:
        _detector = MVTecAnomalyDetector()
    return _detector

def predict_mvtec(image_path):
    """
    Main prediction function - runs ALL models and returns comprehensive results
    """
    detector = get_detector()
    return detector.predict_all(image_path)