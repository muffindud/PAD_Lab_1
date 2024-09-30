const db = require('../models');
const User = db.users;
const Op = db.Sequelize.Op;

// Create and Save a new User
exports.create = (req, res) => {
    if (!req.body.username || !req.body.password) {
        res.status(400).send({
            message: 'Content can not be empty!'
        });

        return;
    }

    const user = {
        username: req.body.username,
        password_hash: req.body.password,
        balance: req.body.balance
    };

    User.create(user)
        .then(data => {
            res.send(data);
        })
        .catch(err => {
            res.status(500).send({
                message: err.message || 'Some error occurred while creating the User.'
            });
        });
};


