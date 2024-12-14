import neo4j
from time import sleep


class Neo4jConn:
    def __init__(self, host, port, user, password, dbname):
        self.dbname = dbname
        self.driver = neo4j.GraphDatabase.driver(
            f"bolt://{host}:{port}",
            auth=(user, password),
        )

        while True:
            sleep(5)
            try:
                with self.driver:
                    self.driver.execute_query("MATCH (n) RETURN n LIMIT 1")
                break
            except Exception as e:
                print(f"Error: {e}")

    @staticmethod
    def pack_record(record):
        result = {}
        for i in range(len(record)):
            result[record[i]['t']['timestamp']] = {
                'from': record[i]['from']['username'],
                'to': record[i]['to']['username'],
                'amount': record[i]['t']['amount']
            }

        return result

    def get_last_ts(self):
        with self.driver:
            result = self.driver.execute_query("""
                MATCH ()-[t:TRANSFERRED]->()
                RETURN t.timestamp AS lastTimestamp
                ORDER BY t.timestamp DESC
                LIMIT 1
            """)

            return result[0][0]['lastTimestamp']

    def check_if_updated(self, last_ts):
        return self.get_last_ts() != last_ts

    def get_data_since_last_ts(self, last_ts):
        with self.driver:
            result = self.driver.execute_query(f"""
                MATCH (from)-[t:TRANSFERRED]->(to)
                WHERE t.timestamp >= {last_ts}
                RETURN from, to, t
            """)

            return self.pack_record(result[0])

    def get_all_data(self):
        with self.driver:
            result = self.driver.execute_query("""
                MATCH (from)-[t:TRANSFERRED]->(to)
                RETURN from, to, t
            """)

            return self.pack_record(result[0])
