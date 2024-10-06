const neo4j = require('neo4j-driver');

const driver = neo4j.driver(
    process.env.NEO4J_HOST + ':' + process.env.NEO4J_PORT,
    neo4j.auth.basic(
        process.env.NEO4J_USER,
        process.env.NEO4J_PASSWORD
    )
);

module.exports = {
    read: (cypher, params = {}, database = process.env.NEO4J_DATABASE) => {
        const session = driver.session({
            defaultAccessMode: neo4j.session.READ,
            database: database
        });

        return session.run(cypher, params)
            .then(result => {
                session.close();
                return result;
            })
            .catch(err => {
                session.close();
                throw err;
            });
    },

    write: (cypher, params = {}, database = process.env.NEO4J_DATABASE) => {
        const session = driver.session({
            defaultAccessMode: neo4j.session.WRITE,
            database: database
        });

        return session.run(cypher, params)
            .then(result => {
                session.close();
                return result;
            })
            .catch(err => {
                session.close();
                throw err;
            });
    }
}
