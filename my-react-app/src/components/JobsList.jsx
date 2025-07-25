import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/api';

const JobsList = () => {
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await api.get('/jobs');
        setJobs(response.data);
      } catch (error) {
        console.error('Error fetching jobs:', error);
      }
    };

    fetchJobs();
  }, []);

  return (
    <div>
      <h1>Jobs</h1>
      <ul>
        {jobs.map((job) => (
          <li key={job.id}>
            <Link to={`/jobs/${job.id}`}>
              Job {job.id} - {job.status}
            </Link>
            {job.status === 'completed' && (
              <Link to={`/jobs/${job.id}/result`} style={{ marginLeft: '10px' }}>
                View Result
              </Link>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default JobsList;
