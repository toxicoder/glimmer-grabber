// Placeholder server.js for api_gateway
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

const authMiddleware = (req, res, next) => {
  if (req.headers.authorization) {
    next();
  } else {
    res.status(401).send('Unauthorized');
  }
};

const { getFile } = require('./googleDrive');
const { getJamboard } = require('./jamboard');

const services = [
  {
    route: '/auth',
    target: 'http://auth_service:8000'
  },
  {
    route: '/api/v1/jobs',
    target: 'http://job_service:8000',
    middleware: [authMiddleware]
  },
  {
    route: '/api/v1/collections',
    target: 'http://job_service:8000',
    middleware: [authMiddleware]
  }
];

services.forEach(({ route, target, middleware }) => {
  if (middleware) {
    app.use(route, ...middleware, createProxyMiddleware({ target, changeOrigin: true }));
  } else {
    app.use(route, createProxyMiddleware({ target, changeOrigin: true }));
  }
});

app.get('/api/v1/google-drive/:fileId', authMiddleware, async (req, res) => {
  try {
    const file = await getFile(req.params.fileId);
    res.json(file);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

app.get('/api/v1/jamboard/:fileId', authMiddleware, async (req, res) => {
  try {
    const file = await getJamboard(req.params.fileId);
    res.json(file);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

const PORT = 8080;
app.listen(PORT, () => {
  console.log(`API Gateway listening on port ${PORT}`);
});
