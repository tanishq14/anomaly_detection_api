# 🤖 Multi-Domain Anomaly Detection - React Frontend

This is the modern, responsive web interface for the **Multi-Domain Anomaly Detection API**. Built with React and Vite, it provides an intuitive user experience for analyzing network traffic, inspecting product quality, and diagnosing medical X-rays using AI.

## ✨ Features

- **🌐 Network Intrusion Detection**: Enter network traffic parameters or load presets (Normal Web Browsing, FTP Transfer, Port Scans) to instantly detect malicious activity.
- **🏭 Product Quality Inspection**: Drag-and-drop file upload for industrial product images (MVTec AD dataset) to detect manufacturing defects.
- **🏥 Medical X-ray Analysis**: Secure upload for chest X-rays to run unsupervised anomaly detection and supervised disease classification (NIH Chest X-ray14 dataset).
- **📊 Rich Results Dashboard**: Visual confidence bars, ensemble voting summaries, and dynamic color-coded alerts based on model predictions.

## 🛠️ Technology Stack

- **Framework**: [React 18](https://react.dev/)
- **Build Tool**: [Vite](https://vitejs.dev/) (Super-fast HMR and optimized builds)
- **Routing**: [React Router v6](https://reactrouter.com/)
- **Styling**: Custom CSS3 (Fully responsive, no external UI libraries required)

## 🚀 Getting Started

### Prerequisites

You need to have **Node.js** (v18 or higher recommended) installed on your machine. 

### 1. Install Dependencies

Open your terminal, navigate to the `frontend` folder, and install the required npm packages:

```bash
cd frontend
npm install
```

### 2. Start the Development Server
```bash
npm run dev
```

The application will start, and you can view it in your browser at http://localhost:5173.

⚠️ Important: The frontend requires the Python Flask API to be running simultaneously to make predictions. Make sure you start your backend (python app.py or via Docker) on port 5000.

## 🔌 API Connection (Proxy)
To avoid CORS (Cross-Origin Resource Sharing) issues during development, this React app uses Vite's built-in proxy.

Any request made to /api/* from the frontend is automatically forwarded to the Flask backend running on http://127.0.0.1:5000. This is configured in vite.config.js.

##📁 Project Structure

```text
anomaly-detection-api/
frontend/
├── public/                 # Static public assets
├── src/
│   ├── components/         # Reusable UI components
│   │   └── Navbar.jsx      # Top navigation bar
│   ├── pages/              # Application views/routes
│   │   ├── Home.jsx        # Landing page
│   │   ├── NetworkPage.jsx # Network intrusion form
│   │   ├── MVTecPage.jsx   # Product quality drag & drop
│   │   └── XrayPage.jsx    # Medical analysis UI
│   ├── App.jsx             # Main router and layout wrapper
│   ├── main.jsx            # React DOM entry point
│   └── index.css           # Global stylesheet
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite & Proxy configuration
└── README.md               # This file
```
## 📦 Building for Production
When you are ready to deploy the frontend, run:

```bash
npm run build
```

This will create a dist directory containing the optimized, minified HTML, JS, and CSS files ready to be served by any static file server (like Nginx, Apache, or Vercel).