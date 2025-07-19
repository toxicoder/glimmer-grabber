import React from 'react';

const GoogleDriveEmbed = ({ embedUrl }) => {
  return (
    <div className="google-drive-embed">
      <iframe
        src={embedUrl}
        width="100%"
        height="100%"
        frameBorder="0"
        allow="fullscreen"
      ></iframe>
    </div>
  );
};

export default GoogleDriveEmbed;
