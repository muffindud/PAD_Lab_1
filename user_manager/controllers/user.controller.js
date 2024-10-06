const bcrypt = require('bcrypt');
const db = require('../models');
const User = db.users;
const Op = db.Sequelize.Op;
const { generateUserToken, verifyUserToken, verifyInternalToken } = require('../utils/authJwt');

User.secureCreate = (req, res) => {
    password_hash = bcrypt.hashSync(req.body.password, 8);

    const user = {
        username: req.body.username,
        password_hash: password_hash,
        email: req.body.email,
        balance: req.body.balance
    }

    User.findOne({
        where: {
            username: user.username
        }
    })
        .then(data => {
            if (data) {
                return res.status(409).send({ message: 'Username already exists.' });
            }

            User.create(user)
                .then(data => {
                    const token = generateUserToken(data.username);
                    res.send({ token: token });
                })
                .catch(err => {
                    console.log(err);
                    res.status(500).send({
                        message: err.message || 'Some error occurred while creating the User.'
                    });
                });
        })
        .catch(err => {
            console.log(err);
            res.status(500).send({ message: err.message });
        });
}

User.secureLogin = (req, res) => {
    const username = req.body.username;
    const password = req.body.password;

    User.findOne({
        where: {
            username: username
        }
    })
        .then(data => {
            if (!data) {
                return res.status(404).send({ message: 'User Not found.' });
            }

            const passwordIsValid = bcrypt.compareSync(password, data.password_hash);

            if (!passwordIsValid) {
                return res.status(401).send({
                    accessToken: null,
                    message: 'Invalid Password!'
                });
            }

            const token = generateUserToken(data.username);
            res.status(200).send({ token: token });
        })
        .catch(err => {
            console.log(err);
            res.status(500).send({ message: err.message });
        });
};

User.secureFind = (req, res) => {
    const token = req.headers['x-access-token'];
    const decoded = verifyUserToken(token);
    // get the user from the database
    const user = User.findOne({
        where: {
            username: decoded.username
        }
    })
        .then(data => {
            if (!data) {
                return res.status(404).send({ message: 'User Not found.' });
            }

            res.status(200).send({
                username: data.username,
                email: data.email,
                balance: data.balance
            });
        })
        .catch(err => {
            res.status(500).send({ message: err.message });
        });
};

User.secureTransfer = (req, res) => {
    const token = req.headers['x-access-token'];
    const decoded = verifyUserToken(token);
    const sender = decoded.username;
    const receiver = req.body.username;
    const amount = req.body.amount;

    // get the sender from the database
    User.findOne({
        where: {
            username: sender
        }
    })
        .then(data => {
            if (!data) {
                return res.status(404).send({ message: 'Sender Not found.' });
            }

            if (data.balance < amount) {
                return res.status(400).send({ message: 'Insufficient balance.' });
            }

            User.findOne({
                where: {
                    username: receiver
                }
            })
                .then(data => {
                    if (!data) {
                        return res.status(404).send({ message: 'Receiver Not found.' });
                    }

                    User.update({
                        balance: data.balance + amount
                    }, {
                        where: {
                            username: receiver
                        }
                    })
                        .then(num => {
                            if (num == 1) {
                                User.update({
                                    balance: data.balance - amount
                                }, {
                                    where: {
                                        username: sender
                                    }
                                })
                                    .then(num => {
                                        if (num == 1) {
                                            // TODO: Add transfer to neo4j database
                                            return res.status(200).send({ message: 'Transfer successful.' });
                                        }
                                    })
                                    .catch(err => {
                                        res.status(500).send({ message: err.message });
                                    });
                            }
                        })
                        .catch(err => {
                            res.status(500).send({ message: err.message });
                        });
                })
                .catch(err => {
                    res.status(500).send({ message: err.message });
                });
        })
        .catch(err => {
            res.status(500).send({ message: err.message });
        });
};

User.internalBalance = (req, res) => {
    const token = req.headers['x-access-token'];

    if (!token) {
        return res.status(401).send({ message: 'Unauthorized' });
    }

    const decoded = verifyInternalToken(token);

    if (!decoded) {
        return res.status(401).send({ message: 'Unauthorized' });
    }

    const user_id = req.params.user_id;
    User.findOne({
        where: {
            id: user_id
        }
    })
        .then(data => {
            if (!data) {
                return res.status(404).send({ message: 'User Not found.' });
            }

            res.status(200).send({
                balance: data.balance
            });
        })
        .catch(err => {
            res.status(500).send({ message: err.message });
        });
};

User.internalUpdateBalance = (req, res) => {
    const token = req.headers['x-access-token'];

    if (!token) {
        return res.status(401).send({ message: 'Unauthorized' });
    }

    const decoded = verifyInternalToken(token);

    if (!decoded) {
        return res.status(401).send({ message: 'Unauthorized' });
    }

    const user_id = req.params.user_id;
    const balance = req.body.balance;

    User.findOne({
        where: {
            id: user_id
        }
    })
        .then(data => {
            if (!data) {
                return res.status(404).send({ message: 'User Not found.' });
            }
        })
        .catch(err => {
            res.status(500).send({ message: err.message });
        });

    User.update({
        balance: balance
    }, {
        where: {
            id: user_id
        }
    })
        .then(num => {
            if (num == 1) {
                // TODO: Add update balance to neo4j database
                res.status(200).send({ message: 'Balance updated successfully.' });
            }
        })
        .catch(err => {
            res.status(500).send({ message: err.message });
        });
};

module.exports = User;
