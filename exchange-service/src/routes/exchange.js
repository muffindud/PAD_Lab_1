const axios = require("axios");
const router = require("express").Router();
const session = require("../neo4j");
const { verifyInternalToken, verifyUserToken } = require("../authJwt");

const cacheDiscoveryUrl = `http://${process.env.SERVICE_DISCOVERY_HOST}:${process.env.SERVICE_DISCOVERY_PORT}/cache`;
var cacheServers = [];
var cacheServerIndex = 0;

setInterval(() => {
  axios.get(cacheDiscoveryUrl)
  .then((response) => {
    cacheServers = Object.values(response.data);
  })
}, 10000);

const requestWithTimeout = (url, timeout = 10000) => {
  return Promise.race([
    axios.get(url),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error("Request timed out")), timeout)
    ),
  ]);
};

const getCacheServer = () => {
  const cacheServer = cacheServers[cacheServerIndex];
  cacheServerIndex = (cacheServerIndex + 1) % cacheServers.length;
  return cacheServer;
}

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
    const apiUrl = `http://${getCacheServer()}/?baseCurrency=${baseCurrency}&targetCurrency=${targetCurrency}`;
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

      const cacheUrl = `http://${getCacheServer()}/`;
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

router.post('/transfer', async (req, res) => {
  if (!req.get('Authorization')) {
    return res.status(401).send({ message: 'Unauthorized' });
  }

  try {
      try{
          const token = req.get('Authorization').split(' ')[1];
          const decoded = verifyInternalToken(token);
          if (decoded.server != 'Gateway') {
              return res.status(401).send({ message: 'Unauthorized' });
          }
      } catch (err) {
          return res.status(401).send({ message: 'Unauthorized' });
      }

      if (!req.body.sender || !req.body.receiver || !req.body.amount) {
          return res.status(400).send({ message: 'Missing required fields.' });
      }

      const transferResult = await session.run(
          `
          MERGE (from:User {username: $sender})
          MERGE (to:User {username: $receiver})
          CREATE (from)-[:TRANSFERRED {amount: $amount, timestamp: timestamp()}]->(to)
          RETURN from, to
          `,
          { sender: req.body.sender, receiver: req.body.receiver, amount: req.body.amount }
      );

      res.status(200).send({ message: 'Transfer logged successfully.' });
  } catch (err) {
      console.log(err);
      res.status(500).send({ message: err.message });
  }
});

router.get('/transfer', async (req, res) => {
  try {
    let username;
    try {
      username = verifyUserToken(req.get('Authorization').split(' ')[1]).username;
    } catch (err) {
        return res.status(401).send({ message: 'Unauthorized' });
    }

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
});

router.get("/status", (req, res) => {
  res.json({ status: "healthy" });
});

module.exports = router;
