import React from 'react';
import './App.css';
import GoogleDriveEmbed from './GoogleDriveEmbed';
import JamboardEmbed from './JamboardEmbed';

function App() {
  // Example embed URLs
  const googleDriveUrl = "https://docs.google.com/document/d/1BvE2b_3a1i1E1c_1d1E1F1g1H1I1J1K1L1M1N1O1P1/edit?usp=sharing";
  const jamboardUrl = "https://jamboard.google.com/d/1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z/edit?usp=sharing";

  return (
    <div className="App">
      <header className="App-header">
        <h1>Google Drive and Jamboard Integration</h1>
      </header>
      <div className="embed-container">
        <h2>Google Drive Embed</h2>
        <GoogleDriveEmbed embedUrl={googleDriveUrl} />
        <h2>Jamboard Embed</h2>
        <JamboardEmbed embedUrl={jamboardUrl} />
      </div>
    </div>
  );
}

export default App;
