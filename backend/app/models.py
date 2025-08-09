from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from .db import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, index=True, nullable=True)
    phone = Column(String(32), unique=True, nullable=True)
    hashed_password = Column(String(256), nullable=True)
    display_name = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    searches = relationship('SearchHistory', back_populates='user')
    reports = relationship('RouteReport', back_populates='user')

class SearchHistory(Base):
    __tablename__ = 'search_history'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    query = Column(String(512))
    lat = Column(Float)
    lng = Column(Float)
    ts = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship('User', back_populates='searches')

class RouteReport(Base):
    __tablename__ = 'route_reports'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    type = Column(String(64))
    description = Column(Text)
    lat = Column(Float)
    lng = Column(Float)
    ts = Column(DateTime, default=datetime.datetime.utcnow)
    trust_score = Column(Integer, default=0)

    user = relationship('User', back_populates='reports')
