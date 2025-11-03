import React, { useState, useEffect } from 'react';
import api from '../services/api';

const CheckIns = () => {
  const [attendances, setAttendances] = useState([]);
  const [message, setMessage] = useState('');
  const [userAttendances, setUserAttendances] = useState([]);

  useEffect(() => {
    const fetchAttendances = async () => {
      const userId = localStorage.getItem('user_id');
      try {
        const response = await api.get('/attendance');
        // Show all attendances for today
        const today = new Date().toISOString().split('T')[0];
        const todayAttendances = response.data.filter(a => a.check_in && a.check_in.startsWith(today));
        setAttendances(todayAttendances);
        const userTodayAttendances = todayAttendances.filter(a => a.user_id == userId);
        setUserAttendances(userTodayAttendances);
      } catch (error) {
        setMessage('Failed to load attendances');
      }
    };
    fetchAttendances();
  }, []);

  const handleCheckIn = async () => {
    const userId = localStorage.getItem('user_id');
    // Assume default shift id 1
    try {
      await api.post('/attendance/checkin', { user_id: userId, shift_id: 1 });
      setMessage('Check-in registrado!');
      refreshAttendances();
    } catch (error) {
      setMessage('Erro ao registrar check-in');
    }
  };

  const handleCheckOut = async (attendanceId) => {
    try {
      await api.post('/attendance/checkout', { attendance_id: attendanceId });
      setMessage('Check-out registrado!');
      refreshAttendances();
    } catch (error) {
      setMessage('Erro ao registrar check-out');
    }
  };

  const refreshAttendances = async () => {
    const userId = localStorage.getItem('user_id');
    try {
      const response = await api.get('/attendance');
      const today = new Date().toISOString().split('T')[0];
      const todayAttendances = response.data.filter(a => a.check_in && a.check_in.startsWith(today));
      setAttendances(todayAttendances);
      const userTodayAttendances = todayAttendances.filter(a => a.user_id == userId);
      setUserAttendances(userTodayAttendances);
    } catch (error) {
      setMessage('Erro ao atualizar check-ins');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl mb-4">Check-ins do Dia</h1>
      <h2 className="text-xl mb-2">Meus Check-ins</h2>
      {userAttendances.length === 0 ? (
        <div>
          <p className="text-gray-600 mb-4">Nenhum check-in registrado ainda.</p>
          <button onClick={handleCheckIn} className="bg-blue-500 text-white p-2 rounded">Registrar Check-in</button>
        </div>
      ) : (
        <ul className="mb-6">
          {userAttendances.map(att => (
            <li key={att.id} className="bg-blue-100 p-4 mb-2 rounded shadow flex justify-between items-center">
              <div>
                Check-in: {att.check_in} - Check-out: {att.check_out || 'Pendente'} - Horas: {att.hours_worked || 'N/A'}
              </div>
              {!att.check_out && (
                <button onClick={() => handleCheckOut(att.id)} className="bg-red-500 text-white p-2 rounded ml-4">
                  Fazer Check-out
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
      <h2 className="text-xl mb-2">Todos os Check-ins do Dia</h2>
      {attendances.length === 0 ? (
        <p className="text-gray-600">Nenhum check-in hoje.</p>
      ) : (
        <ul>
          {attendances.map(att => (
            <li key={att.id} className="bg-white p-4 mb-2 rounded shadow">
              {att.user_name}: Check-in {att.check_in} - Check-out {att.check_out || 'Pendente'}
            </li>
          ))}
        </ul>
      )}
      <p>{message}</p>
    </div>
  );
};

export default CheckIns;