import React from 'react';

const JamboardEmbed = ({ embedUrl }) => {
  return (
    <div className="jamboard-embed">
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

export default JamboardEmbed;
