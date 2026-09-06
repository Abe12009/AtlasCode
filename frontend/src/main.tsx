import { createRoot } from 'react-dom/client';
import './index.css';
import { StrictMode } from 'react';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import App from './App';

const root = document.getElementById('root');

if (!root) {
  throw new Error('Root element (#root) not found');
}

createRoot(root).render(
  <StrictMode>
    <ThemeProvider>
      <I18nextProvider i18n={i18n}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </I18nextProvider>
    </ThemeProvider>
  </StrictMode>,
);
