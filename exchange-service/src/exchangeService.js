const express = require("express");
const axios = require("axios");
const exchangeRoutes = require("./routes/exchange");

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

app.use("/api", exchangeRoutes);

app.get("/", (req, res) => {
  res.send("Welcome to the Exchange Service!");
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send("Something went wrong!");
});

const healthCheck = async () => {
  console.log("Performing health check...");

  try {
    const response = await axios.get(`http://localhost:${port}/api/status`);
    if (response.status === 200) {
      console.log("Service is healthy (status endpoint reachable)");
    }
  } catch (error) {
    console.error(
      "Health check failed: Service is down or unreachable",
      error.message
    );
  }
};

setInterval(healthCheck, 10000);

app.listen(port, () => {
  console.log(`Exchange Service listening at http://localhost:${port}`);
});
