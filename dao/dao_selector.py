from singleton import Singleton
from dao.sqlalchemy.sqlalchemydao import SQLAlchemyDao
from dao.pythondao.pythondao import PythonDao
from system_config import Config, DAO

SQLALCHEMYDAO = "SQLAlchemyDao"
PYTHONDAO = "PythonDao"


def dao():
    if Config().config[DAO] == SQLALCHEMYDAO:
        return SQLAlchemyDao()
    elif Config().config[DAO] == PYTHONDAO:
        return PythonDao()
    else:
        raise RuntimeError("Incorrect dao specified in config:" + Config().config[DAO])


    
