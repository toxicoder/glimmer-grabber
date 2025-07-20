import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div>
      <h1>Home</h1>
      <Link to="/login">Login</Link>
      <br />
      <Link to="/register">Register</Link>
      <br />
      <Link to="/profile">Profile</Link>
      <br />
      <Link to="/jobs">Jobs</Link>
      <br />
      <Link to="/collection">Collection</Link>
    </div>
  );
};

export default Home;
