import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

declare global {
  interface Window {
    google?: any;
  }
}

export default function Login({ addToast }: { addToast: (message: string, type?: 'success' | 'error' | 'info') => void }) {
  const { user, loginWithGoogle } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (user) {
      navigate('/');
    }
  }, [user, navigate]);

  useEffect(() => {
    if (!window.google?.accounts?.id) {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = () => renderGoogleButton();
      document.body.appendChild(script);
      return () => {
        document.body.removeChild(script);
      };
    }
    renderGoogleButton();
  }, []);

  const renderGoogleButton = () => {
    if (!window.google?.accounts?.id) return;
    window.google.accounts.id.initialize({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      callback: handleCredentialResponse,
      auto_select: false,
    });
    window.google.accounts.id.renderButton(
      document.getElementById('google-signin-button')!,
      { theme: 'outline', size: 'large', width: '100%' },
    );
  };

  const handleCredentialResponse = async (response: any) => {
    if (!response?.credential) {
      addToast('Google login failed.', 'error');
      return;
    }
    setIsLoading(true);
    try {
      await loginWithGoogle(response.credential);
      navigate('/');
      addToast('Bienvenido! Has iniciado sesión.', 'success');
    } catch (error) {
      addToast((error as Error).message || 'Login failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page-content" style={{ maxWidth: 500, margin: '0 auto' }}>
      <div className="card">
        <div className="card-header">
          <h2>Iniciar sesión</h2>
          <p>Accede con tu cuenta de Google para usar Enmask.</p>
        </div>
        <div style={{ display: 'grid', gap: 16, padding: '24px 16px' }}>
          <div id="google-signin-button" />
          {isLoading && <div className="spinner" style={{ margin: '0 auto' }} />}
          <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
            Requiere un cliente de Google configurado en VITE_GOOGLE_CLIENT_ID.
          </p>
        </div>
      </div>
    </div>
  );
}
