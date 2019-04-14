#!/usr/bin/env python
# coding=utf-8
import enum
import os

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Sequence, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

import util.bootstrap
import util.logger as logger

_log = logger.get_logger(__name__)

Session = sessionmaker()
Base = declarative_base()
DATABASE_FILE_NAME = 'rca_telemetry.sqlite3'


class VerdictEnum(enum.Enum):
    VERDICT_OK = 1
    VERDICT_LAG = 2


class User(Base):
    """
    Represents a user identified by a @dell.com email address
    """
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    email = Column(String)

    # Relationship with 'Usage' comes later as the class is not yet defined

    def __repr__(self):
        return "<User('%s')>" % (self.email)


class Usage(Base):
    """
    Represents some interaction with the RCA tool (not actual analysi) with a timestamp
    """
    __tablename__ = 'usage'
    id = Column(Integer, Sequence('usage_id_seq'), primary_key=True)
    ip = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='usage')

    def __repr__(self):
        return "<Usage(IP='%s', timestamp='%s')>" % (self.ip, self.timestamp)


class Analysis(Base):
    """
    Represents the result of a successful analysis
    """
    __tablename__ = 'analysis'
    id = Column(Integer, Sequence('analysis_id_seq'), primary_key=True)
    ddos_version = Column(String, nullable=False)
    serialno = Column(String, nullable=False)
    replctx = Column(String, nullable=False)
    verdict = Column(Enum(VerdictEnum), nullable=False)
    suggested_fix = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='analysis')

    def __repr__(self):
        return "<Analysis(%s running %s for replctx %s: %s (suggested_fix: %s))>" % (self.serialno, self.ddos_version, self.replctx, self.verdict, self.suggested_fix)


# Relationships of other tables to the Users table
User.usage = relationship('Usage', order_by=Usage.id, back_populates='user', cascade='all, delete, delete-orphan')
User.analysis = relationship('Analysis', order_by=Analysis.id, back_populates='user', cascade='all, delete, delete-orphan')


def initialize_db(runtime_path):
    """
    Create or read the SQlite DB file for telemetry

    :param runtime_path: Absolute path to directory containing the DB file
    """
    db_path = os.path.join(runtime_path, DATABASE_FILE_NAME)
    _log.info("Initializing telemetry database at: %s", db_path)

    engine = create_engine('sqlite:///' + db_path, echo=False)
    Base.metadata.create_all(engine)

    Session.configure(bind=engine)


def track_user(user_email, ip, timestamp):
    """
    Add a record for the specified user in the telemetry DB

    :param user_email: @dell.com email address
    :param ip: IP address string
    :param timestamp: datetime object
    """
    session = Session()
    user = session.query(User).filter_by(email=user_email).first()

    if not user:
        _log.info("New user in DB: %s", user_email)
        user = User(email=user_email)
        session.add(user)

    user.usage.append(Usage(ip=ip, timestamp=timestamp))

    _log.info("[TELEMETRY] %s %s", user, user.usage[-1])
    session.commit()


def track_analysis(user_email, analysis):
    """
    Add a record for an RCA result for the spefified user
    Note that track_user() MUST have been called for this user_email before this call

    :param user_email: @dell.com email address
    :param analysis: Dict with analysis results
    """
    session = Session()
    user = session.query(User).filter_by(email=user_email).first()

    if not user:
        raise Exception("Must call track_user() for %s before tracking analysis results" % (user_email))

    user.analysis.append(Analysis(ddos_version=analysis['ddos_version'],
                                  serialno=analysis['serialno'],
                                  replctx=analysis['replctx'],
                                  verdict=analysis['verdict'],
                                  suggested_fix=analysis['suggested_fix']))

    session.add(user)

    _log.info("[TELEMETRY] %s %s", user, user.analysis[-1])
    session.commit()


def main():
    """
    For unit testing only
    """
    initialize_db(".")
    track_user("someone@dell.com", "10.3.4.5", datetime.now())
    track_analysis("someone@dell.com", {
        'ddos_version': '6.0.1.10-12345',
        'serialno': 'ABCD12345',
        'replctx': '1',
        'verdict': VerdictEnum.VERDICT_OK,
        'suggested_fix': ''
    })

    session = Session()

    for u in session.query(User).all():
        _log.info(u)
        _log.info(u.usage)
        _log.info(u.analysis)

    return


if __name__ == '__main__':
    main()
