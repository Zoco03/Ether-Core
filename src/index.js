
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Inject base dark theme styles
const style = document.createElement('style');
style.innerHTML = `
  body {
    margin: 0;
    padding: 0;
    background-color: #0A0A0A !important;
    color: #e5e7eb;
    font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  }
  ::-webkit-scrollbar {
    width: 6px;
  }
  ::-webkit-scrollbar-track {
    background: #0A0A0A;
  }
  ::-webkit-scrollbar-thumb {
    background: #262626;
    border-radius: 3px;
  }
`;
document.head.appendChild(style);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
