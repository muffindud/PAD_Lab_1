const executeWithTimeout = require('../middleware/timeout');

module.exports = app => {
    const users = require('../controllers/user.controller');

    var router = require('express').Router();

    router.get('/', (req, res) => {
        res.send('Hello World!');
    });

    // Client endpoints
    router.post('/register', executeWithTimeout(users.secureCreate));
    router.get('/login', executeWithTimeout(users.secureLogin));
    router.get('/profile', executeWithTimeout(users.secureFind));
    router.post('/transfer', executeWithTimeout(users.secureTransfer));
    // router.post('/register', (req, res) => {executeWithTimeout(users.secureCreate)});
    // router.get('/login', (req, res) => {executeWithTimeout(users.secureLogin)});
    // router.get('/profile', (req, res) => {executeWithTimeout(users.secureFind)});
    // router.post('/transfer', (req, res) => {executeWithTimeout(users.secureTransfer)});

    // Internal endpoints
    router.get('/balance/:user_id', users.internalBalance);
    router.put('/balance/:user_id', users.internalUpdateBalance);

    // Health check
    router.get('/health', (req, res) => {
        res.status(200).json({ status: 'healthy' });
    });

    app.use('/', router);
};