const bcrypt = require('bcrypt');
const db = require('../models');
const User = db.users;
const Op = db.Sequelize.Op;
const { generateUserToken, verifyUserToken, verifyInternalToken } = require('../utils/authJwt');
const session = require('../neo4j');

User.secureCreate = async (req, res) => {
    try {
        const password_hash = bcrypt.hashSync(req.body.password, 8);
        const user = {
            username: req.body.username,
            password_hash: password_hash,
            email: req.body.email,
            balance: req.body.balance
        };

        const existingUser = await User.findOne({ where: { username: user.username } });
        if (existingUser) {
            return res.status(409).send({ message: 'Username already exists.' });
        }

        const newUser = await User.create(user);
        const token = generateUserToken(newUser.username);
        res.send({ token: token });
    } catch (err) {
        console.log(err);
        res.status(500).send({ message: err.message || 'Some error occurred while creating the User.' });
    }
};

User.secureLogin = async (req, res) => {
    try {
        const username = req.body.username;
        const password = req.body.password;

        const user = await User.findOne({ where: { username: username } });
        if (!user) {
            return res.status(404).send({ message: 'User Not found.' });
        }

        const passwordIsValid = bcrypt.compareSync(password, user.password_hash);
        if (!passwordIsValid) {
            return res.status(401).send({ message: 'Invalid Password!' });
        }

        const token = generateUserToken(user.username);
        res.status(200).send({ token: token });
    } catch (err) {
        console.log(err);
        res.status(500).send({ message: err.message });
    }
};

User.secureFind = async (req, res) => {
    if (!req.get('Authorization')) {
        return res.status(401).send({ message: 'Unauthorized' });
    }

    try {
        const token = req.get('Authorization').split(' ')[1];
        if (!token) {
            return res.status(401).send({ message: 'Unauthorized' });
        }
        const decoded = verifyUserToken(token);

        const user = await User.findOne({ where: { username: decoded.username } });
        if (!user) {
            return res.status(404).send({ message: 'User Not found.' });
        }

        res.status(200).send({
            username: user.username,
            email: user.email,
            balance: user.balance
        });
    } catch (err) {
        console.log(err);
        res.status(500).send({ message: err.message });
    }
};

User.secureTransfer = async (req, res) => {
    if (!req.get('Authorization')) {
        return res.status(401).send({ message: 'Unauthorized' });
    }

    try {
        const token = req.get('Authorization').split(' ')[1];
        const decoded = verifyUserToken(token);
        const sender = decoded.username;
        const receiver = req.body.username;
        const amount = req.body.amount;

        if (sender === receiver) {
            return res.status(400).send({ message: 'Cannot transfer to self.' });
        }

        const senderData = await User.findOne({ where: { username: sender } });
        if (!senderData) {
            return res.status(404).send({ message: 'Sender Not found.' });
        }
        if (senderData.balance < amount) {
            return res.status(400).send({ message: 'Insufficient balance.' });
        }

        const receiverData = await User.findOne({ where: { username: receiver } });
        if (!receiverData) {
            return res.status(404).send({ message: 'Receiver Not found.' });
        }

        await User.update({ balance: parseInt(receiverData.balance) + parseInt(amount) }, { where: { username: receiver } });
        await User.update({ balance: parseInt(senderData.balance) - parseInt(amount) }, { where: { username: sender } });
        const transferResult = await session.run(
            `
            MERGE (from:User {username: $sender})
            MERGE (to:User {username: $receiver})
            CREATE (from)-[:TRANSFERRED {amount: $amount, timestamp: timestamp()}]->(to)
            RETURN from, to
            `,
            { sender: sender, receiver: receiver, amount: amount }
        );

        res.status(200).send({ message: 'Transfer successful.' });
    } catch (err) {
        console.log(err);
        res.status(500).send({ message: err.message });
    }
};

User.internalBalance = async (req, res) => {
    if (!req.get('Authorization')) {
        return res.status(401).send({ message: 'Unauthorized' });
    }

    try {
        const token = req.get('Authorization').split(' ')[1];
        const decoded = verifyInternalToken(token);

        if (!decoded) {
            return res.status(401).send({ message: 'Unauthorized' });
        }

        const user = await User.findOne({ where: { id: req.params.user_id } });
        if (!user) {
            return res.status(404).send({ message: 'User Not found.' });
        }

        res.status(200).send({ balance: user.balance });
    } catch (err) {
        console.log(err);
        res.status(500).send({ message: err.message });
    }
};

User.internalUpdateBalance = async (req, res) => {
    if (!req.get('Authorization')) {
        return res.status(401).send({ message: 'Unauthorized' });
    }

    try {
        const token = req.get('Authorization').split(' ')[1];
        const decoded = verifyInternalToken(token);

        if (!decoded) {
            return res.status(401).send({ message: 'Unauthorized' });
        }

        const user = await User.findOne({ where: { id: req.params.user_id } });
        if (!user) {
            return res.status(404).send({ message: 'User Not found.' });
        }

        await User.update({ balance: req.body.balance }, { where: { id: req.params.user_id } });
        res.status(200).send({ message: 'Balance updated successfully.' });
    } catch (err) {
        console.log(err);
        res.status(500).send({ message: err.message });
    }
};

User.secureGetTransferHistory = async (req, res) => {
    if (!req.get('Authorization')) {
        return res.status(401).send({ message: 'Unauthorized' });
    }

    try {
        const token = req.get('Authorization').split(' ')[1];
        const decoded = verifyUserToken(token);
        const username = decoded.username;

        const result = await session.run(
            `
            MATCH (user:User {username: $username})
            OPTIONAL MATCH (user)-[outgoing:TRANSFERRED]->(recipient:User)
            OPTIONAL MATCH (sender:User)-[incoming:TRANSFERRED]->(user)
            RETURN user, 
                   collect({recipient: recipient.username, amount: outgoing.amount, timestamp: outgoing.timestamp}) AS outgoingTransfers, 
                   collect({sender: sender.username, amount: incoming.amount, timestamp: incoming.timestamp}) AS incomingTransfers
            `,
            { username }
        );

        if (result.records.length === 0) {
            return res.status(404).send({ message: 'User Not found.' });
        }

        const record = result.records[0];
        const transfers = [];

        // Process outgoing transfers (positive amounts)
        const outgoingTransfers = record.get('outgoingTransfers');
        outgoingTransfers.forEach(transfer => {
            if (transfer.recipient && transfer.timestamp) {
                transfers.push({
                    timestamp: transfer.timestamp,
                    transfer: `${transfer.recipient} -${transfer.amount}`
                });
            }
        });

        // Process incoming transfers (negative amounts)
        const incomingTransfers = record.get('incomingTransfers');
        incomingTransfers.forEach(transfer => {
            if (transfer.sender && transfer.timestamp) {
                transfers.push({
                    timestamp: transfer.timestamp,
                    transfer: `${transfer.sender} +${transfer.amount}`
                });
            }
        });

        transfers.sort((a, b) => {
            if (a.timestamp < b.timestamp) {
                return -1;
            }
            if (a.timestamp > b.timestamp) {
                return 1;
            }
            return 0;
        })

        res.status(200).send({
            username: username,
            transfers: transfers.reduce((acc, t) => {
                acc[t.timestamp] = t.transfer;
                return acc;
            }, {})
        });
    } catch (err) {
        console.log(err);
        res.status(500).send({ message: err.message });
    }
};

module.exports = User;
