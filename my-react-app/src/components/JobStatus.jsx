import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../utils/api';

const JobStatus = () => {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const response = await api.get(`/jobs/${jobId}`);
        setJob(response.data);
        setError(null);
      } catch (error) {
        console.error('Error fetching job status:', error);
        setError('Error fetching job status');
      }
    };

    fetchJob();

    const interval = setInterval(fetchJob, 5000);

    return () => clearInterval(interval);
  }, [jobId]);

  if (error) {
    return <div>{error}</div>;
  }

  if (!job) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Job Status</h1>
      <p>Job ID: {job.job_id}</p>
      <p>Status: {job.status}</p>
      {job.result && (
        <div>
          <h3>Result</h3>
          <pre>{JSON.stringify(job.result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default JobStatus;
