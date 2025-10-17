// src/index.js (The correct structure for React 18+)

import React from 'react';
// 1. IMPORT from 'react-dom/client'
import ReactDOM from 'react-dom/client'; 
import App from './App';
// import './index.css'; // Keep or remove based on your files

// 2. USE createRoot() and render() on the root object
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you have routing, ensure your Router wraps the App component in App.js 
// or around <App /> here.