module.exports = app => {
    const users = require('../controllers/user.controller');

    var router = require('express').Router();

    router.get('/', (req, res) => {
        res.send('Hello World!');
    });

    // Client endpoints
    router.post('/register', users.secureCreate);
    router.get('/login', users.secureLogin);
    router.get('/profile', users.secureFind);
    router.post('/transfer', users.secureTransfer);

    // Internal endpoints
    router.get('/balance/:user_id', users.internalBalance);
    router.put('/balance/:user_id', users.internalUpdateBalance);

    app.use('/', router);
};