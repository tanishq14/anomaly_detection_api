import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
  const location = useLocation(); // Tells us which page we are on

  // Helper to check if link is active
  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <nav classN-ame="nav-bar">
      <ul>
        <li><Link to="/" className={isActive('/')}>Home</Link></li>
        <li><Link to="/network" className={isActive('/network')}>Network</Link></li>
        <li><Link to="/mvtec" className={isActive('/mvtec')}>MVTec</Link></li>
        <li><Link to="/xray" className={isActive('/xray')}>X-ray</Link></li>
      </ul>
    </nav>
  );
}