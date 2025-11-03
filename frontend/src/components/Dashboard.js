import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [shifts, setShifts] = useState([]);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchShifts = async () => {
      try {
        const response = await api.get('/shifts');
        setShifts(response.data);
      } catch (error) {
        setMessage('Failed to load shifts');
      }
    };
    fetchShifts();
  }, []);

  const handleCheckin = async (shiftId) => {
    const userId = localStorage.getItem('user_id');
    try {
      await api.post('/attendance/checkin', { user_id: userId, shift_id: shiftId });
      setMessage('Check-in recorded');
    } catch (error) {
      setMessage('Check-in failed');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl mb-4">Dashboard</h1>
      <div className="mb-4">
        <h2 className="text-xl">Shifts</h2>
        <ul>
          {shifts.map(shift => (
            <li key={shift.id} className="bg-white p-4 mb-2 rounded shadow">
              {shift.date} - {shift.type} - {shift.nurse_group}
              <button onClick={() => handleCheckin(shift.id)} className="ml-4 bg-green-500 text-white p-2">Check-in</button>
            </li>
          ))}
        </ul>
      </div>
      <p>{message}</p>
    </div>
  );
};

export default Dashboard;