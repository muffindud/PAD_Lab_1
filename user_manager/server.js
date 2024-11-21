const express = require('express');
const promMid = require('express-prometheus-middleware');
const cors = require('cors');
const os = require('os');

const app = express();
const PORT = process.env.PORT;
const serviceDiscoveryUrl = `http://${process.env.SERVICE_DISCOVERY_HOST}:${process.env.SERVICE_DISCOVERY_PORT}/discovery`;
const serviceId = fetch(
    serviceDiscoveryUrl,
    {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            service_name: "User Manager",
            host: os.hostname(),
            port: PORT.toString(),
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
        app.use(cors());

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

        app.listen(PORT, () => {
            console.log(`Server is running on port ${PORT}`);
        });
});