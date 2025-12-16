from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


