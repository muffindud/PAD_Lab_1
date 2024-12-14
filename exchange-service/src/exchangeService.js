const express = require("express");
const axios = require("axios");
const promMid = require("express-prometheus-middleware");
const exchangeRoutes = require("./routes/exchange");
const os = require("os");

const app = express();
const port = process.env.PORT;
const serviceDiscoveryUrl = `http://${process.env.SERVICE_DISCOVERY_HOST}:${process.env.SERVICE_DISCOVERY_PORT}/discovery`;
const serviceId = fetch(
  serviceDiscoveryUrl,
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      service_name: "Exchange Service",
      host: os.hostname(),
      port: port.toString(),
    }),
  }
)
  .then((response) => response.json())
  .then((data) => data.id)
  .catch((error) => {
    console.error("Error registering service with service discovery", error);
    process.exit(1);
  })
  .finally(() => {
    app.use(express.json());

    app.use(
      promMid({
        metricsPath: '/metrics',
        collectDefaultMetrics: true,
        requestDurationBuckets: [0.1, 0.5, 1, 1.5],
        requestLengthBuckets: [512, 1024, 5120, 10240, 51200, 102400],
        responseLengthBuckets: [512, 1024, 5120, 10240, 51200, 102400],
      })
    );

    app.use((req, res, next) => {
      console.log(`${req.ip} - - [${new Date().toUTCString()}] "${req.method} ${req.path} HTTP/1.1" ${res.statusCode} - "${req.headers['user-agent']}"`);
      next();
    })

    app.use("/api", exchangeRoutes);

    app.get("/", (req, res) => {
      res.send("Welcome to the Exchange Service!");
    });

    app.get("/health", (req, res) => {
      res.status(200).json({ status: "healthy" });
    });

    app.use((err, req, res, next) => {
      console.error(err.stack);
      res.status(500).send("Something went wrong!");
    });

    app.listen(port, () => {
      console.log(`Exchange Service listening at http://localhost:${port}`);
    });
});