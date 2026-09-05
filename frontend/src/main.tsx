import { createRoot } from 'react-dom/client'
import './index.css'
import { StrictMode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { I18nextProvider } from 'react-i18next'
import i18n from './i18n'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import App from './App'

console.log('ATLASCODE: main.tsx EXECUTING');

const root = document.getElementById('root');
console.log('ATLASCODE: root element found:', !!root);

if (!root) {
  console.error('ATLASCODE: root element NOT FOUND');
  document.body.innerHTML = '<div style="padding:40px;color:red;font-size:24px;background:#0f172a">ROOT ELEMENT NOT FOUND</div>';
} else {
  console.log('ATLASCODE: ABOUT TO MOUNT REACT');

  const reactRoot = createRoot(root);
  console.log('ATLASCODE: React root created, rendering App...');

  try {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } }
    });

    reactRoot.render(
      <StrictMode>
        <QueryClientProvider client={queryClient}>
          <I18nextProvider i18n={i18n}>
            <BrowserRouter>
              <AuthProvider>
                <App />
              </AuthProvider>
            </BrowserRouter>
          </I18nextProvider>
        </QueryClientProvider>
      </StrictMode>
    );
    console.log('ATLASCODE: React mounted successfully');
  } catch (e: unknown) {
    const err = e as Error;
    console.error('ATLASCODE: React mount FAILED:', err);
    root.innerHTML = '<div style="padding:40px;color:red;font-size:24px;background:#0f172a">React mount error: ' + err.message + '</div>';
  }
}