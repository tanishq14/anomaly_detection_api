"""
Network Intrusion Detection Pipeline (UNSW-NB15)
Supports: IsolationForest, OneClassSVM, EllipticEnvelope, LocalOutlierFactor
"""

import pandas as pd
import pickle
import numpy as np
from sklearn.decomposition import PCA
import os

# Dataset configuration
DATASET_CONFIG = {
    'train_path': 'datasets/network/UNSW-NB15 dataset/CSV Files/Training and Testing Sets/UNSW_NB15_training-set.csv',
    'test_path': 'datasets/network/UNSW-NB15 dataset/CSV Files/Training and Testing Sets/UNSW_NB15_testing-set.csv',
    'features_path': 'datasets/network/UNSW-NB15 dataset/CSV Files/NUSW-NB15_features.csv',
    'expected_features': ['dur', 'proto', 'service', 'state', 'spkts', 'dpkts', 'sbytes', 
                         'dbytes', 'rate', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss',
                         'sinpkt', 'dinpkt', 'sjit', 'djit', 'swin', 'stcpb', 'dtcpb', 'dwin',
                         'tcprtt', 'synack', 'ackdat', 'smean', 'dmean', 'trans_depth',
                         'response_body_len', 'ct_srv_src', 'ct_state_ttl', 'ct_dst_ltm',
                         'ct_src_dport_ltm', 'ct_dst_sport_ltm', 'ct_dst_src_ltm',
                         'is_ftp_login', 'ct_ftp_cmd', 'ct_flw_http_mthd', 'ct_src_ltm',
                         'ct_srv_dst', 'is_sm_ips_ports','attack cat', 'label']
}

# Mapping from "Friendly/Preset Names" -> "Model Training Names"
# This fixes the "not in index" error
COLUMN_MAPPING = {
    'smean': 'smeansz',
    'dmean': 'dmeansz',
    'response_body_len': 'res_bdy_len',
    'sinpkt': 'sintpkt',
    'dinpkt': 'dintpkt',
    'ct_src_ltm': 'ct_src_ ltm'
}

# Smart presets for common traffic patterns
TRAFFIC_PRESETS = {
    "normal_web_browsing": {
        "dur": 0.5, "proto": "tcp", "service": "http", "state": "FIN",
        "spkts": 12, "dpkts": 10, "sbytes": 800, "dbytes": 10000,
        "rate": 40.0, "sttl": 31, "dttl": 29, "sload": 1200.0, "dload": 2000.0,
        "sloss": 0, "dloss": 0, "sinpkt": 40.0, "dinpkt": 50.0,
        "sjit": 2.0, "djit": 3.0, "swin": 255, "stcpb": 1000000, "dtcpb": 1000000,
        "dwin": 255, "tcprtt": 0.01, "synack": 0.005, "ackdat": 0.005,
        "smean": 66, "dmean": 1000, "trans_depth": 1, "response_body_len": 2000,
        "ct_srv_src": 1, "ct_state_ttl": 0, "ct_dst_ltm": 1, "ct_src_dport_ltm": 1,
        "ct_dst_sport_ltm": 1, "ct_dst_src_ltm": 1, "is_ftp_login": 0,
        "ct_ftp_cmd": 0, "ct_flw_http_mthd": 1, "ct_src_ltm": 1,
        "ct_srv_dst": 1, "is_sm_ips_ports": 0
    },
    
    #This keeps sttl=254 or high packet counts to simulate suspicious transfers
    "file_transfer_ftp": {
        "dur": 2.5, "proto": "tcp", "service": "ftp", "state": "FIN",
        "spkts": 30, "dpkts": 25, "sbytes": 2000, "dbytes": 50000,
        "rate": 20.0, "sttl": 60, "dttl": 29, "sload": 800.0, "dload": 20000.0,
        "sloss": 0, "dloss": 0, "sinpkt": 83.33, "dinpkt": 100.0,
        "sjit": 5.0, "djit": 6.0, "swin": 255, "stcpb": 5000000, "dtcpb": 2000000,
        "dwin": 16384, "tcprtt": 0.002, "synack": 0.002, "ackdat": 0.002,
        "smean": 66.67, "dmean": 2000.0, "trans_depth": 0, "response_body_len": 0,
        "ct_srv_src": 3, "ct_state_ttl": 1, "ct_dst_ltm": 3, "ct_src_dport_ltm": 1,
        "ct_dst_sport_ltm": 1, "ct_dst_src_ltm": 8, "is_ftp_login": 1,
        "ct_ftp_cmd": 1, "ct_flw_http_mthd": 0, "ct_src_ltm": 3,
        "ct_srv_dst": 3, "is_sm_ips_ports": 0
    },
    
    "dns_query": {
        "dur": 0.001, "proto": "udp", "service": "dns", "state": "CON",
        "spkts": 2, "dpkts": 2, "sbytes": 146, "dbytes": 178,
        "rate": 2000.0, "sttl": 31, "dttl": 129, "sload": 146000.0, "dload": 178000.0,
        "sloss": 0, "dloss": 0, "sinpkt": 0.5, "dinpkt": 0.5,
        "sjit": 0.0, "djit": 0.0, "swin": 0, "stcpb": 0, "dtcpb": 0,
        "dwin": 0, "tcprtt": 0.0, "synack": 0.0, "ackdat": 0.0,
        "smean": 73.0, "dmean": 89.0, "trans_depth": 0, "response_body_len": 0,
        "ct_srv_src": 2, "ct_state_ttl": 0, "ct_dst_ltm": 2, "ct_src_dport_ltm": 1,
        "ct_dst_sport_ltm": 1, "ct_dst_src_ltm": 2, "is_ftp_login": 0,
        "ct_ftp_cmd": 0, "ct_flw_http_mthd": 0, "ct_src_ltm": 2,
        "ct_srv_dst": 2, "is_sm_ips_ports": 0
    },
    
    "suspicious_scan": {
        # High sttl (254) + High ct_ counts + Short duration = Classic Attack
        "dur": 0.00001, "proto": "tcp", "service": "-", "state": "INT",
        "spkts": 2, "dpkts": 0, "sbytes": 114, "dbytes": 0,
        "rate": 100000.0, "sttl": 254, "dttl": 0, "sload": 100000000.0, "dload": 0.0,
        "sloss": 0, "dloss": 0, "sinpkt": 0.01, "dinpkt": 0.0,
        "sjit": 0.0, "djit": 0.0, "swin": 0, "stcpb": 0, "dtcpb": 0,
        "dwin": 0, "tcprtt": 0.0, "synack": 0.0, "ackdat": 0.0,
        "smean": 57.0, "dmean": 0.0, "trans_depth": 0, "response_body_len": 0,
        "ct_srv_src":30, "ct_state_ttl": 6, "ct_dst_ltm": 15, "ct_src_dport_ltm": 15,
        "ct_dst_sport_ltm": 15, "ct_dst_src_ltm": 30, "is_ftp_login": 0,
        "ct_ftp_cmd": 0, "ct_flw_http_mthd": 0, "ct_src_ltm": 30,
        "ct_srv_dst": 30, "is_sm_ips_ports": 0
    }
}

# Feature descriptions for tooltips
FEATURE_DESCRIPTIONS = {
    "dur": "Duration of connection in seconds",
    "proto": "Network protocol (TCP, UDP, ARP, etc.)",
    "service": "Network service (HTTP, FTP, DNS, etc.)",
    "state": "Connection state (FIN=finished, CON=connected, INT=interrupted)",
    "spkts": "Number of packets sent from source",
    "dpkts": "Number of packets sent to destination",
    "sbytes": "Total bytes sent from source",
    "dbytes": "Total bytes sent to destination",
    "rate": "Packets per second transmission rate"
}


# Model paths
MODEL_PATHS = {
    'transformer': 'models/network/column_transformer.pkl',
    'isolation_forest': 'models/network/isolation_forest.pkl',
    'ocsvm': 'models/network/ocsvm.pkl',
    'elliptic_envelope': 'models/network/elliptic_envelope.pkl',
    'elliptic_pca': 'models/network/elliptic_pca.pkl',  # PCA for EllipticEnvelope
    'lof': 'models/network/lof.pkl'
}

class NetworkAnomalyDetector:
    def __init__(self):
        """Load all trained models and transformer"""
        self.models = {}
        self.transformer = None
        self.pca_elliptic = None
        
        # Load column transformer
        if os.path.exists(MODEL_PATHS['transformer']):
            with open(MODEL_PATHS['transformer'], 'rb') as f:
                self.transformer = pickle.load(f)
            print("✓ Loaded Column Transformer")
        
        # Load all models
        for model_name, path in MODEL_PATHS.items():
            if model_name != 'transformer' and os.path.exists(path):
                with open(path, 'rb') as f:
                    if model_name == 'elliptic_pca':
                        self.pca_elliptic = pickle.load(f)
                    else:
                        self.models[model_name] = pickle.load(f)
                        print(f"✓ Loaded {model_name}")
                        
    
    def _preprocess(self, data_dict, use_preset=True):
        """Convert input dict to preprocessed features"""
        # Apply smart defaults if enabled
        if use_preset and 'preset' in data_dict:
            preset_name = data_dict.pop('preset')
            data_dict = apply_preset(data_dict, preset_name)
        elif use_preset:
            data_dict = apply_preset(data_dict)
        
        df = pd.DataFrame([data_dict])
        
        # Ensure all expected features are present
        for feat in DATASET_CONFIG['expected_features']:
            if feat not in df.columns:
                df[feat] = 0  # Default value for missing features

        # CRITICAL FIX: Rename columns to match what the model expects
        # The model was trained on UNSW-NB15 csv headers (smeansz, dmeansz, etc.)
        df.rename(columns=COLUMN_MAPPING, inplace=True)
        
        # Transform using saved transformer
        if self.transformer is None:
            raise RuntimeError("Column transformer not loaded. Check that models/network/column_transformer.pkl exists.")
        
        try:
            X = self.transformer.transform(df)
        except Exception as e:
            # Better error message for debugging column mismatches
            raise ValueError(f"Transformer failed. Model expects columns: {e}")

        return X


    def predict_all(self, data_dict):
        """
        Run ALL models and return comprehensive results + ensemble prediction
        
        Args:
            data_dict: Dictionary with network features
        
        Returns:
            dict: {
                'ensemble': {'prediction': 'Normal/Attack', 'confidence': float, 'votes': dict},
                'models': {
                    'isolation_forest': {'prediction': str, 'score': float, 'confidence': float},
                    'ocsvm': {...},
                    'elliptic_envelope': {...},
                    'lof': {...}
                }
            }
        """
        X = self._preprocess(data_dict)
        
        results = {}
        predictions = []  # For ensemble voting
        
        # 1. IsolationForest
        if 'isolation_forest' in self.models:
            model = self.models['isolation_forest']
            pred = model.predict(X)[0]
            score = float(model.score_samples(X)[0]) if hasattr(model, 'score_samples') else None
            
            results['isolation_forest'] = {
                'prediction': 'Normal' if pred == 1 else 'Attack',
                'score': score,
                'confidence': self._calculate_confidence(score),
                'raw_prediction': int(pred)
            }
            predictions.append(pred)
        
        # 2. OneClassSVM
        if 'ocsvm' in self.models:
            model = self.models['ocsvm']
            pred = model.predict(X)[0]
            score = float(model.decision_function(X)[0]) if hasattr(model, 'decision_function') else None
            
            results['ocsvm'] = {
                'prediction': 'Normal' if pred == 1 else 'Attack',
                'score': score,
                'confidence': self._calculate_confidence(score),
                'raw_prediction': int(pred)
            }
            predictions.append(pred)
        
        # 3. EllipticEnvelope (with PCA)
        if 'elliptic_envelope' in self.models:
            model = self.models['elliptic_envelope']
            X_pca = self.pca_elliptic.transform(X) if self.pca_elliptic is not None else X
            pred = model.predict(X_pca)[0]
            score = float(model.decision_function(X_pca)[0]) if hasattr(model, 'decision_function') else None
            
            results['elliptic_envelope'] = {
                'prediction': 'Normal' if pred == 1 else 'Attack',
                'score': score,
                'confidence': self._calculate_confidence(score),
                'raw_prediction': int(pred)
            }
            predictions.append(pred)
        
        # 4. LocalOutlierFactor
        if 'lof' in self.models:
            model = self.models['lof']
            pred = model.predict(X)[0]
            score = float(model.decision_function(X)[0]) if hasattr(model, 'decision_function') else None
            
            results['lof'] = {
                'prediction': 'Normal' if pred == 1 else 'Attack',
                'score': score,
                'confidence': self._calculate_confidence(score),
                'raw_prediction': int(pred)
            }
            predictions.append(pred)
        
        # Ensemble: Majority Voting
        normal_votes = predictions.count(1)
        attack_votes = predictions.count(-1)
        ensemble_pred = 'Normal' if normal_votes > attack_votes else 'Attack'
        ensemble_confidence = max(normal_votes, attack_votes) / len(predictions) * 100 if predictions else 0
        
        return {
            'ensemble': {
                'prediction': ensemble_pred,
                'confidence': round(ensemble_confidence, 2),
                'votes': {
                    'Normal': normal_votes,
                    'Attack': attack_votes
                },
                'total_models': len(predictions)
            },
            'models': results
        }
    
    def _calculate_confidence(self, score):
        """Convert anomaly score to confidence percentage"""
        if score is None:
            return None
        # Sigmoid-based confidence
        confidence = 1 / (1 + np.exp(-abs(score)))
        return round(confidence * 100, 2)
    
def apply_preset(user_input, preset_name="normal_web_browsing"):
    """
    Apply preset values and merge with user input
    User input takes priority over preset values
    """
    if preset_name not in TRAFFIC_PRESETS:
        preset_name = "normal_web_browsing"
    
    # Start with preset
    data = TRAFFIC_PRESETS[preset_name].copy()
    
    # Override with user input
    data.update(user_input)
    
    return data

# Singleton instance
_detector = None

def get_detector():
    """Get or create detector instance"""
    global _detector
    if _detector is None:
        _detector = NetworkAnomalyDetector()
    return _detector

def predict_network(data_dict):
    """
    Main prediction function - runs ALL models and returns comprehensive results
    """
    detector = get_detector()
    return detector.predict_all(data_dict)