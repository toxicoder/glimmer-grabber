const { google } = require('googleapis');

const oAuth2Client = new google.auth.OAuth2(
  // YOUR_CLIENT_ID,
  // YOUR_CLIENT_SECRET,
  // YOUR_REDIRECT_URL
);

const drive = google.drive({
  version: 'v3',
  auth: oAuth2Client,
});

async function getFile(fileId) {
  const res = await drive.files.get({
    fileId: fileId,
    fields: 'webViewLink, thumbnailLink',
  });
  return res.data;
}

module.exports = {
  getFile,
};
