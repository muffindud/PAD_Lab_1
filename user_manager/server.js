const express = require('express');
const cors = require('cors');

const app = express();

app.use(cors());

app.use(express.json());

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
