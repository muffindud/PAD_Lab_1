const express = require("express");
const axios = require("axios");
const router = express.Router();

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
    const apiUrl = `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/${baseCurrency}.json`;
    const response = await axios.get(apiUrl);
    const rates = response.data[baseCurrency];

    if (rates && rates[targetCurrency]) {
      const exchangeRate = rates[targetCurrency];
      res.json({
        baseCurrency,
        targetCurrency,
        exchangeRate,
      });
    } else {
      res.status(404).json({ message: "Target currency not found." });
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: "Error fetching exchange rate." });
  }
});

router.get("/status", (req, res) => {
  res.json({ status: "healthy" });
});

module.exports = router;
