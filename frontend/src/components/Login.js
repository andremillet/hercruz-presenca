import React, { useState, useEffect } from 'react';
import QrReader from 'react-qr-scanner';
import api from '../services/api';

const Login = () => {
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [cpf, setCpf] = useState('');
  const [isNewUser, setIsNewUser] = useState(false);
  const [name, setName] = useState('');
  const [crm, setCrm] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const isScan = urlParams.get('scan') === 'true';

    if (!isScan) {
      const fetchQr = async () => {
        try {
          console.log('Fetching QR from:', api.defaults.baseURL + '/qr/generate');
          const response = await api.get('/qr/generate', { responseType: 'blob' });
          console.log('QR response:', response);
          const url = URL.createObjectURL(response.data);
          setQrCodeUrl(url);
        } catch (error) {
          console.log('QR fetch error:', error);
          setMessage('Failed to generate QR code: ' + error.message);
        }
      };
      fetchQr();
    } else {
      setShowModal(true);
    }
  }, []);



  const handleCpfSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/auth/validate_cpf', { cpf });
      if (response.data.exists) {
        localStorage.setItem('user_id', response.data.user_id);
        window.location.href = '/dashboard'; // Redirect to check-ins page
      } else {
        setIsNewUser(true);
      }
    } catch (error) {
      setMessage('CPF validation failed');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/auth/register_cpf', { cpf, name, crm });
      localStorage.setItem('user_id', response.data.user_id);
      window.location.href = '/dashboard';
    } catch (error) {
      setMessage('Registration failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      {!showModal && (
        <div className="bg-white p-6 rounded shadow-md text-center">
          <h2 className="text-2xl mb-4">Confirme Presença</h2>
          {qrCodeUrl && <img src={qrCodeUrl} alt="QR Code" className="mx-auto mb-4 w-96 h-96" />}
          <p className="mb-4">Escanear com câmera do celular para confirmar presença</p>
          <button onClick={() => { setShowModal(true); }} className="w-full bg-gray-500 text-white p-2">Simular Escanear (Teste)</button>
          <p className="mt-4">{message}</p>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded shadow-md">
            {!isNewUser ? (
              <form onSubmit={handleCpfSubmit}>
                <h3 className="text-xl mb-4">Digite seu CPF</h3>
                <input
                  type="tel"
                  placeholder="CPF"
                  value={cpf}
                  onChange={(e) => setCpf(e.target.value)}
                  className="w-full p-2 mb-4 border"
                  required
                />
                <button type="submit" className="w-full bg-green-500 text-white p-2">Confirmar</button>
              </form>
            ) : (
              <form onSubmit={handleRegister}>
                <h3 className="text-xl mb-4">Cadastro</h3>
                <input
                  type="text"
                  placeholder="Nome Completo"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full p-2 mb-4 border"
                  required
                />
                <input
                  type="number"
                  placeholder="CRM"
                  value={crm}
                  onChange={(e) => setCrm(e.target.value)}
                  className="w-full p-2 mb-4 border"
                />
                <button type="submit" className="w-full bg-green-500 text-white p-2">Registrar</button>
              </form>
            )}
            <button onClick={() => setShowModal(false)} className="mt-4 text-red-500">Fechar</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;