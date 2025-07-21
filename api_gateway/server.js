// Placeholder server.js for api_gateway
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

const jwt = require('jsonwebtoken');

const authMiddleware = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (authHeader) {
    const token = authHeader.split(' ')[1];
    jwt.verify(token, 'your_secret_key', (err, user) => {
      if (err) {
        return res.sendStatus(403);
      }
      req.user = user;
      next();
    });
  } else {
    res.sendStatus(401);
  }
};

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

const PORT = 8080;
app.listen(PORT, () => {
  console.log(`API Gateway listening on port ${PORT}`);
});
