import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import NetworkPage from './pages/NetworkPage';
import MVTecPage from './pages/MVTecPage';
import XrayPage from './pages/XrayPage';
import Home from './pages/Home';

// Placeholder components for now
// const MVTecPage = () => <div className="container"><h2>MVTec Page Coming Soon</h2></div>;
// const XrayPage = () => <div className="container"><h2>X-ray Page Coming Soon</h2></div>;

function App() {
  return (
    <Router>
      <div className="container">
        <header>
          <h1>🤖 Techniques to overcome class imbalance using Anomaly/Defect Detection API</h1>
          <p>AI-Powered Detection Across Network Security, Manufacturing, and Healthcare</p>
        </header>
        
        <Navbar />
        
        {/* This section swaps based on the URL */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/network" element={<NetworkPage />} />
          <Route path="/mvtec" element={<MVTecPage />} />
          <Route path="/xray" element={<XrayPage />} />
        </Routes>

        <footer>
            <p><strong>Anomaly Detection API</strong> - React Frontend</p>
            <p>&copy; 2026 Tanishq Rahul Shelke</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;