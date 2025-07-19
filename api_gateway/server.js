// Placeholder server.js for api_gateway
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

const services = [
  {
    route: '/auth',
    target: 'http://auth_service:8000'
  },
  {
    route: '/jobs',
    target: 'http://job_service:8000'
  }
];

services.forEach(({ route, target }) => {
  app.use(route, createProxyMiddleware({ target, changeOrigin: true }));
});

const PORT = 8080;
app.listen(PORT, () => {
  console.log(`API Gateway listening on port ${PORT}`);
});
