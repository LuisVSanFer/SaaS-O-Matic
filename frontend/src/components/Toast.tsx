import React, { useEffect } from 'react';

interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'info';
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ message, type, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const colors = {
    success: { bg: '#10b981', border: '#059669' },
    error: { bg: '#ef4444', border: '#dc2626' },
    info: { bg: '#3b82f6', border: '#2563eb' },
  };

  const style = colors[type];

  // Animación con keyframes en CSS-in-JS simple
  const toastStyle: React.CSSProperties = {
    position: 'fixed',
    top: '20px',
    right: '20px',
    zIndex: 9999,
    padding: '14px 20px',
    borderRadius: '8px',
    color: '#fff',
    background: style.bg,
    borderLeft: `5px solid ${style.border}`,
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    minWidth: '280px',
    maxWidth: '400px',
    animation: 'slideIn 0.3s ease-out',
    fontFamily: 'Arial, sans-serif',
    fontSize: '14px',
  };

  // Inyectamos la animación globalmente una vez (truco simple)
  useEffect(() => {
    if (!document.getElementById('toast-animations')) {
      const styleEl = document.createElement('style');
      styleEl.id = 'toast-animations';
      styleEl.innerHTML = `
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `;
      document.head.appendChild(styleEl);
    }
  }, []);

  return <div style={toastStyle}>{message}</div>;
};