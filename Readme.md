# 🤖 Techniques to Overcome Class Imbalance using Anomaly Detection  

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-1.9+-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/Class_Imbalance-Solved-success.svg)
![Ensemble Learning](https://img.shields.io/badge/Method-Ensemble_Learning-orange.svg)

**A specialized framework designed to handle extreme class imbalance by treating minority classes as anomalies. This project demonstrates high-precision detection across Network, Manufacturing quality control and Medical domains using machine learning methods.**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Class Imbalance Strategy](#-class-imbalance-strategy)
- [Case Study : Isolation Forest](#case-study--isolation-forest)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Datasets](#datasets)
- [Architecture](#architecture)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Performance Metrics](#performance-metrics)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## 🎯 Overview

This project addresses the "Imbalanced Data" problem in Machine Learning. In real-world scenarios like Network Intrusion or Medical Diagnosis, the "Anomaly" is often extremely rare. This API uses **Ensemble Anomaly Detection** to find those rare events without needing a perfectly balanced training set.

<!-- This project implements a **multi-domain anomaly detection system** that applies ensemble machine learning techniques across three distinct domains:

1. **🌐 Network Intrusion Detection** - Identify malicious network traffic (UNSW-NB15 dataset)
2. **🏭 Product Quality Inspection** - Detect manufacturing defects (MVTec AD dataset)
3. **🏥 Medical Image Analysis** - Analyze chest X-rays for abnormalities (NIH Chest X-ray14 dataset)

Each module uses an **ensemble of multiple models** to achieve robust, accurate predictions with high confidence scores. -->

---

## 🔧 Class Imbalance Strategy

| Technique | Implementation | Benefit |
| :--- | :--- | :--- |
| **One-Class SVM** | Learns the boundary of "Normal" data. | Ignores the lack of minority samples. |
| **Autoencoders** | Reconstructs input; high error = anomaly. | Self-supervised; no labels required. |
| **Isolation Forest** | Isolates points in a tree structure. | Efficiently finds outliers in large data. |

---
## 🔬 Case Study : Isolation Forest
> **The Theory:** Anomalies are "few and different." In a tree-based structure, they are isolated much faster (shorter path) than normal points (longer path). This allows the API to detect attacks even if they were never seen during training.

---
## ✨ Features

### Core Capabilities
- **Multi-domain support** - 3 independent detection modules
- **Ensemble learning** - Combines 4-7 models per domain using majority voting
- **RESTful API** - Clean Flask-based API with JSON responses
- **Web interface** - User-friendly HTML/CSS/JS frontend
- **Real-time processing** - Fast inference with processing time tracking
- **Comprehensive results** - Individual model outputs + ensemble predictions

### Technical Features
- 🔥 **Deep Learning** - ResNet34 for feature extraction, Autoencoders for anomaly detection
- 📊 **Classical ML** - Isolation Forest, One-Class SVM, Elliptic Envelope, LOF
- 🎯 **High Accuracy** - 92-99% across different domains
- 📈 **Detailed Metrics** - Confidence scores, processing times, model agreement
- 🔒 **Secure uploads** - File validation, size limits, automatic cleanup
- 📝 **Logging** - Comprehensive logging for debugging and monitoring

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, Windows 10+
- **Python**: 3.8 or higher
- **RAM**: 8GB (16GB recommended for X-ray module)
- **Storage**: 5GB for models and dependencies
- **GPU**: Optional (CUDA-compatible for faster inference)

### Python Dependencies

flask>=2.0.0
torch>=1.9.0
torchvision>=0.10.0
scikit-learn>=1.0.0
numpy>=1.21.0
pandas>=1.3.0
pillow>=8.3.0
scipy>=1.7.0


---

## 🚀 Installation

### 1. Clone the Repository
```Bash
git clone https://github.com/tanishq14
cd anomaly-detection-api
```
### 2. Create Virtual Environment
```CMD
python -m venv anom_det
```
#### Activate (Linux/Mac)
```
source anom_det/bin/activate
```
#### Activate (Windows)
```CMD
anom_det\Scripts\activate
```
### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Download/Train Models

Place your trained models in the models/ directory:
models/network/*.pkl
models/mvtec/*.pkl, *.pt
models/xray/*.pkl, *.pt


### 5. Verify Installation
```
python check_system.py
```
If all checks pass ✅, you're ready to go!

---

## ⚡ Quick Start

### Start the API Server

```
python app.py
```

The API will be available at: [**http://localhost:5000**](http://localhost:5000)

### Test the API

#### Network Detection
```
curl -X POST http://localhost:5000/api/predict/network
-H "Content-Type: application/json"
-d '{
"dur": 0.5,
"proto": "tcp",
"service": "http",
"state": "FIN",
"spkts": 12,
"dpkts": 10,
"sbytes": 800,
"dbytes": 15000,
"rate": 40.0
}'
```

#### Image Analysis (MVTec/X-ray)
curl -X POST http://localhost:5000/api/predict/mvtec
-F "file=@product_image.png"

curl -X POST http://localhost:5000/api/predict/xray
-F "file=@chest_xray.png"


---

## 📚 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Homepage |
| `GET` | `/network` | Network detection UI |
| `GET` | `/mvtec` | MVTec inspection UI |
| `GET` | `/xray` | X-ray analysis UI |
| `POST` | `/api/predict/network` | Network intrusion detection |
| `POST` | `/api/predict/mvtec` | Product quality inspection |
| `POST` | `/api/predict/xray` | Chest X-ray analysis |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/models/info` | Model information |

### Response Format

#### All API responses follow this structure:
```
{
"success": true,
"timestamp": "2025-12-26T15:13:00.000000",
"api_version": "2.0",
"data": {
"ensemble": {
"prediction": "Normal",
"confidence": 95.5,
"votes": { "Normal": 3, "Anomaly": 1 }
},
"models": { ... },
"processing_time": "0.234s"
}
}
```

For detailed API documentation, see [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

---

## 📊 Datasets

### Network: UNSW-NB15
- **Records**: 2.5 million network flows
- **Features**: 44 dimensions
- **Attack Types**: 9 categories (DoS, Exploits, Reconnaissance, etc.)
- **Split**: 80% train, 20% test

### MVTec: Anomaly Detection
- **Images**: 5,000+ high-resolution product images
- **Categories**: 15 product types
- **Defects**: Cracks, scratches, contamination, missing parts
- **Split**: Per-category train/test

### X-ray: NIH Chest X-ray14
- **Images**: 112,120 frontal chest X-rays
- **Conditions**: 14 thoracic pathologies
- **Classes**: Multi-label classification
- **Resolution**: 224x224 (preprocessed)

For dataset details, see [DATASETS.md](docs/DATASETS.md)

---

## 🏗️ Architecture

### System Overview

User Input → Flask API → Pipeline Module → Ensemble Models → Prediction
→
Validation & Preprocessing
→
Feature Extraction (if image)
→
Parallel Model Execution
→
Majority Voting Ensemble
→
JSON Response + Confidence


### Models by Domain

**Network** (4 models):
- Isolation Forest
- One-Class SVM
- Elliptic Envelope
- Local Outlier Factor (LOF)

**MVTec** (5 components):
- ResNet34 (feature extraction)
- Isolation Forest
- One-Class SVM
- Elliptic Envelope
- LOF

**X-ray** (7 models):
- Autoencoder (unsupervised)
- Isolation Forest (unsupervised)
- One-Class SVM (unsupervised)
- Elliptic Envelope (unsupervised)
- LOF (unsupervised)
- Decision Tree (supervised)
- K-Nearest Neighbors (supervised)

---

## 📝 Usage Examples

### Python API
```python
from modules import predict_network, predict_mvtec, predict_xray

Network detection with preset
result = predict_network({'preset': 'normal_web_browsing'})
print(result['ensemble']['prediction']) # 'Normal' or 'Attack'

Product quality inspection
result = predict_mvtec('product_image.png')
if result['ensemble']['prediction'] == 'Anomaly':
print(f"Defect detected! Confidence: {result['ensemble']['confidence']}%")

Medical X-ray analysis
result = predict_xray('chest_xray.png')
for model, data in result['supervised_models'].items():
print(f"{model}: {data['prediction']} ({data['confidence']:.1f}%)")
```

### Web Interface

1. Navigate to http://localhost:5000
2. Select a detection module
3. Upload image or enter data
4. View comprehensive results with visualizations

---

## 📁 Project Structure

```text
anomaly-detection-api/
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── app.py              # Flask application
├── check_system.py     # System diagnostics
├── modules/            # Pipeline modules
│ ├── __init__.py
│ ├── network_pipeline.py
│ ├── mvtec_pipeline.py
│ └── xray_pipeline.py
├── models/             # Trained models
│ ├── network/
│ ├── mvtec/
│ └── xray/
├── templates/          # HTML templates
├── static/             # CSS/JS assets
└── docs/               # Documentation
```
---

## 📈 Performance Metrics

| Domain | Imabalance Ratio | Accuracy | Precision | Recall | F1-Score | Models |
|--------|------------------|----------|-----------|--------|----------|--------|
| **Network** | Extreme | 99.2% | 98.5% | 99.1% | 98.8% | 4 |
| **MVTec** | High | 95.8% | 94.2% | 96.1% | 95.1% | 4 |
| **X-ray** | Moderate | 92.3% | 91.8% | 92.7% | 92.2% | 7 |

*Metrics calculated on respective test sets using ensemble predictions*

---

## 🧪 Testing

### Run system diagnostics:
Basic check
```
python check_system.py
```

Verbose output
```
python check_system.py --verbose
```

Attempt fixes
```
python check_system.py --fix
```

Run unit tests (if implemented):
```
pytest tests/
```

---

<!-- ## 🚢 Deployment

For production deployment:

1. **Set production config** in `app.py`:
app.config['DEBUG'] = False

2. **Use production server** (e.g., Gunicorn):
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app


3. **Set up reverse proxy** (Nginx/Apache)

4. **Enable HTTPS** with SSL certificates

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions. -->

<!-- --- -->

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Tanishq Rahul Shelke**

- Masters in Engineering (MEng) - Machine Learning Engineer
- Focus: Anomaly Detection, Ensemble Methods, Deep Learning
- LinkedIn: [Tanishq Shelke](https://www.linkedin.com/in/tanishq-rahul-s-614220210/)
- GitHub: [Tanishq14](https://github.com/tanishq14)

---

## 🙏 Acknowledgments

- **UNSW-NB15 Dataset**: University of New South Wales
- **MVTec AD Dataset**: MVTec Software GmbH
- **NIH Chest X-ray14**: National Institutes of Health
- **PyTorch Team**: For the deep learning framework
- **Scikit-learn Team**: For machine learning tools

---

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/tanishq14/anomaly-detection-api/issues)

---

**⭐ If you find this project useful, please consider giving it a star!**

*Last Updated: February 1, 2026*
# anomaly_detection_api

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
