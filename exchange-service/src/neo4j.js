const neo4j = require('neo4j-driver');

const driver = neo4j.driver(
    `bolt://${process.env.NEO4J_HOST}:${process.env.NEO4J_BOLT_PORT}`,
    neo4j.auth.basic(
        process.env.NEO4J_USER,
        process.env.NEO4J_PASS
    )
);

const session = driver.session();

module.exports = session;
