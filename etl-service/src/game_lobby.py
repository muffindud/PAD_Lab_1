import pymongo
from bson import ObjectId


class MongoConn:
    def __init__(self, host, port, user, password, dbname):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname

        self.client = pymongo.MongoClient(
            f"mongodb://{user}:{password}@{host}:{port}/",
        )
        self.db = self.client[dbname]

    @staticmethod
    def pack_record(record):
        result = {}
        for r in record:
            id = int(str(r['_id']), 16)
            result[id] = {
                'lobby': r['lobbyId'],
                'actions': [
                    (entry.split(' ')[0][:-1], entry.split(' ')[1:]) for entry in r['gameActions']
                ],
            }

        return result

    def get_last_id(self):
        last_id = self.db.game_logs.find_one(
            sort=[('_id', pymongo.DESCENDING)]
        )
        return int(str(last_id['_id']), 16)

    def check_if_updated(self, last_id):
        return self.get_last_id() != last_id

    def get_data_since_last_id(self, last_id):
        return self.pack_record(
            self.db.game_logs.find(
                {'_id': {'$gt': ObjectId(hex(int(last_id))[2:])}}
            )
        )

    def get_all_data(self):
        return self.pack_record(self.db.game_logs.find())
