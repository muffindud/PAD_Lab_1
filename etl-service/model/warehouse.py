from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase


class Warehouse(DeclarativeBase):
    pass


class User(Warehouse):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(50))

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class Log(Warehouse):
    __tablename__ = 'game_logs'
    id = Column(String(50), primary_key=True)
    lobby_id = Column(Integer)

    def __repr__(self):
        return f"<Log(id={self.id}, lobby_id={self.lobby_id})>"


class Message(Warehouse):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    log_id = Column(String(50), ForeignKey('game_logs.id'))
    text = Column(String(255))

    def __repr__(self):
        return f"<Message(id={self.id}, user_id={self.user_id}, log_id={self.log_id}, text={self.text})>"


class Transfer(Warehouse):
    __tablename__ = 'transfers'
    id = Column(BigInteger, primary_key=True)
    from_user_id = Column(Integer, ForeignKey('users.id'))
    to_user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Integer)

    def __repr__(self):
        return f"<Transfer(id={self.id}, from_user_id={self.from_user_id}, to_user_id={self.to_user_id}, amount={self.amount})>"


def get_id_from_username(session, username):
    return session.query(User).filter(User.username == username).first().id


def get_last_user_id(session):
    try:
        return session.query(User).order_by(User.id.desc()).first().id
    except AttributeError:
        return 0


def get_last_log_id(session):
    try:
        return session.query(Log).order_by(Log.id.desc()).first().id
    except AttributeError:
        return 0


def get_last_transfer_ts(session):
    try:
        return session.query(Transfer).order_by(Transfer.id.desc()).first().id
    except AttributeError:
        return 0


def insert_users(session, users):
    try:
        for user in users:
            session.add(User(id=user[0], username=user[1], email=user[2]))
        session.commit()
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()


def insert_transfers(session, transfers):
    try:
        for tranferId, transfer in transfers.items():
            from_user_id = get_id_from_username(session, transfer['from'])
            to_user_id = get_id_from_username(session, transfer['to'])
            session.add(Transfer(id=tranferId, from_user_id=from_user_id, to_user_id=to_user_id, amount=transfer['amount']))
        session.commit()
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()


def insert_logs(session, logs):
    try:
        for logId, log in logs.items():
            session.add(Log(id=str(logId), lobby_id=log['lobby']))
            for action in log['actions']:
                user_id = get_id_from_username(session, action[0])
                session.add(Message(user_id=user_id, log_id=logId, text=action[1]))
        session.commit()
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()


def get_all_table_data(session, table):
    return session.query(table).all()
