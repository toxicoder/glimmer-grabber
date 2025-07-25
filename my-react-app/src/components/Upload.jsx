import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';

const Upload = () => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert('Please select a file');
      return;
    }

    try {
      const response = await api.post('/jobs', {
        filename: file.name,
        contentType: file.type,
      });
      const { uploadUrl, jobId } = response.data;

      await fetch(uploadUrl, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type,
        },
      });

      navigate(`/jobs/${jobId}`);
    } catch (error) {
      console.error('Error uploading file:', error);
      setError(error.response?.data?.detail || 'Error uploading file');
    }
  };

  return (
    <div>
      <h1>Upload Image</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <label htmlFor="file">Select a file</label>
        <input type="file" id="file" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
    </div>
  );
};

export default Upload;
