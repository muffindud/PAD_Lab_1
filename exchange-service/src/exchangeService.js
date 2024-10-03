const express = require("express");
const exchangeRoutes = require("./routes/exchange");

const app = express();
const port = 3000;

app.use(express.json());

app.use("/api", exchangeRoutes);

app.get('/', (req, res) => {
    res.send('Welcome to the Exchange Service!');
});

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send("Something went wrong!");
});

app.listen(port, () => {
    console.log(`Exchange Service listening at http://localhost:${port}`);
});
