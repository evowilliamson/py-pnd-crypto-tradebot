from singleton import Singleton
from dao.sqlalchemy.sqlalchemydao import SQLAlchemyDao
from dao.pythondao.pythonDao import PythonDao
from system_config import Config, DAO

SQLALCHEMYDAO = "SQLAlchemyDao"
PYTHONDAO = "PythonDao"


def dao():

    dao = None

    if Config().config[DAO] == SQLALCHEMYDAO:
        return SQLAlchemyDao()
    else:
        return PythonDao()
    


    
