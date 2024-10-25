const express = require('express');
const cors = require('cors');

const app = express();

app.use(cors());

app.use(express.json());

app.use((req, res, next) => {
    console.log(`${req.ip} - - [${new Date().toUTCString()}] "${req.method} ${req.path} HTTP/1.1" ${res.statusCode} - "${req.headers['user-agent']}"`);
    // console.log("Headers: ", req.headers);
    // console.log("Body: ", req.body);
    next();
})

const db = require('./models');
db.sequelize.sync()
    .then(() => {
        console.log('Database connected');
    })
    .catch(err => {
        console.error(err);
    });

require('./routes/routes')(app);

const PORT = process.env.PORT;

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
