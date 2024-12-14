from os import environ
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.user_manager import PostgresConn
from src.exchange_service import Neo4jConn
from src.game_lobby import MongoConn
from model.warehouse import *


UPDATE_INTERVAL = 30 # seconds
WAREHOUSE_URL = f"postgresql://{environ['DATA_WAREHOUSE_DB_USER']}:{environ['DATA_WAREHOUSE_DB_PASS']}@{environ['DATA_WAREHOUSE_DB_HOST']}:{environ['DATA_WAREHOUSE_DB_PORT']}/{environ['DATA_WAREHOUSE_DB_NAME']}"
engine = create_engine(WAREHOUSE_URL)

# drop database
# Warehouse.metadata.drop_all(engine)
# exit()

Warehouse.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

user_manager_conn = PostgresConn(
    host=environ["USER_MANAGER_DB_HOST"],
    port=environ["USER_MANAGER_DB_PORT"],
    user=environ["USER_MANAGER_DB_USER"],
    password=environ["USER_MANAGER_DB_PASS"],
    dbname=environ["USER_MANAGER_DB_NAME"],
)

exchange_service_conn = Neo4jConn(
    host=environ["EXCHANGE_SERVICE_TRANSFER_DB_HOST"],
    port=environ["EXCHANGE_SERVICE_TRANSFER_DB_PORT"],
    user=environ["EXCHANGE_SERVICE_TRANSFER_DB_USER"],
    password=environ["EXCHANGE_SERVICE_TRANSFER_DB_PASS"],
    dbname=environ["EXCHANGE_SERVICE_TRANSFER_DB_NAME"],
)

game_lobby_conn = MongoConn(
    host=environ["GAME_LOBBY_LOGS_DB_HOST"],
    port=environ["GAME_LOBBY_LOGS_DB_PORT"],
    user=environ["GAME_LOBBY_LOGS_DB_USER"],
    password=environ["GAME_LOBBY_LOGS_DB_PASS"],
    dbname=environ["GAME_LOBBY_LOGS_DB_NAME"],
)


def main():
    while True:
        print(get_all_table_data(session, User), flush=True)
        print(get_all_table_data(session, Log), flush=True)
        print(get_all_table_data(session, Message), flush=True)
        print(get_all_table_data(session, Transfer), flush=True)

        last_user_id = get_last_user_id(session)
        last_log_id = get_last_log_id(session)
        last_transfer_ts = get_last_transfer_ts(session)

        if last_user_id == 0:
            insert_users(session, user_manager_conn.get_all_data())
        elif user_manager_conn.check_if_updated(last_user_id):
            insert_users(session, user_manager_conn.get_data_since_last_id(last_user_id))

        if last_log_id == 0:
            insert_logs(session, game_lobby_conn.get_all_data())
        elif game_lobby_conn.check_if_updated(last_log_id):
            insert_logs(session, game_lobby_conn.get_data_since_last_id(last_log_id))

        if last_transfer_ts == 0:
            insert_transfers(session, exchange_service_conn.get_all_data())
        elif exchange_service_conn.check_if_updated(last_transfer_ts):
            insert_transfers(session, exchange_service_conn.get_data_since_last_ts(last_transfer_ts))

        sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
