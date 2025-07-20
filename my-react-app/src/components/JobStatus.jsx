import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../utils/api';

const JobStatus = () => {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const response = await api.get(`/jobs/${jobId}`);
        setJob(response.data);
      } catch (error) {
        console.error('Error fetching job status:', error);
      }
    };

    fetchJob();
  }, [jobId]);

  if (!job) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Job Status</h1>
      <p>Job ID: {job.id}</p>
      <p>Status: {job.status}</p>
    </div>
  );
};

export default JobStatus;
