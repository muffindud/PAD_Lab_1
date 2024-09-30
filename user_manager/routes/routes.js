module.exports = app => {
    const users = require('../controllers/user.controller');

    var router = require('express').Router();

    router.use((req, res, next) => {
        console.log(`${req.ip} - - [${new Date().toUTCString()}] "${req.method} ${req.path} HTTP/1.1" ${res.statusCode} - "${req.headers['user-agent']}"`);
        next();
        }
    );

    router.get('/', (req, res) => {
        res.send('Hello World!');
        }
    );
};