import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import PrivateRoute from './components/PrivateRoute';
import Home from './pages/Home';
import Profile from './pages/Profile';
import Upload from './components/Upload';
import JobStatus from './components/JobStatus';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route element={<PrivateRoute />}>
        <Route path="/profile" element={<Profile />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/jobs/:jobId" element={<JobStatus />} />
      </Route>
    </Routes>
  );
}

export default App;
