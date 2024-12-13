const express = require("express");
const axios = require("axios");
const router = express.Router();

const cacheDiscoveryUrl = `http://${process.env.SERVICE_DISCOVERY_HOST}:${process.env.SERVICE_DISCOVERY_PORT}/cache`;
var cacheServers = [];

setInterval(() => {
  cacheServers = fetch(
    cacheDiscoveryUrl,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    }
  )
    .then((response) => response.json())
    .then((data) => {
      return Object.values(data);
    })
    .catch((error) => {
      console.error("Error fetching cache servers from service discovery", error);
    });
}, 15000);

const requestWithTimeout = (url, timeout = 10000) => {
  return Promise.race([
    axios.get(url),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error("Request timed out")), timeout)
    ),
  ]);
};

router.get("/exchange-rate", async (req, res) => {
  const { baseCurrency, targetCurrency } = req.query;

  if (!baseCurrency || !targetCurrency) {
    return res
      .status(400)
      .json({ message: "Both baseCurrency and targetCurrency are required." });
  }

  if (baseCurrency.toLowerCase() === targetCurrency.toLowerCase()) {
    return res.json({ baseCurrency, targetCurrency, exchangeRate: 1 });
  }

  try {
    const apiUrl = `http://${process.env.EXCHANGE_CACHE_HOST}:${process.env.EXCHANGE_CACHE_PORT}/?baseCurrency=${baseCurrency}&targetCurrency=${targetCurrency}`;
    const response = await requestWithTimeout(apiUrl);
    const exchangeRate = response.data.rate;

    return res.json({
      baseCurrency,
      targetCurrency,
      exchangeRate,
    });
  } catch (error) {
    if (error.response && error.response.status === 404) {
      console.log(`Exchange rate for ${baseCurrency} to ${targetCurrency} not found in cache. Fetching from currency-api...`);
    } else {
      return res
        .status(500)
        .json({ message: "Error fetching exchange rate." + error.message });
    }
  }

  try {
    const apiUrl = `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/${baseCurrency}.json`;
    const response = await requestWithTimeout(apiUrl);
    const rates = response.data[baseCurrency];

    if (rates && rates[targetCurrency]) {
      const exchangeRate = rates[targetCurrency];

      // store the exchange rate in the exchange-cache service
      const cacheUrl = `http://${process.env.EXCHANGE_CACHE_HOST}:${process.env.EXCHANGE_CACHE_PORT}/`;
      try {
        await axios.post(cacheUrl, {
          [baseCurrency]: rates,
        });
      } catch (error) {
        console.error("Error storing exchange rate in cache.", error.message);
      }

      return res.json({
        baseCurrency,
        targetCurrency,
        exchangeRate,
      });
    } else {
      return res.status(404).json({ message: "Target currency not found." });
    }
  } catch (error) {
    console.error(error);
    return res
      .status(500)
      .json({ message: "Error fetching exchange rate." + error.message });
  }
});

router.get("/status", (req, res) => {
  res.json({ status: "healthy" });
});

module.exports = router;
