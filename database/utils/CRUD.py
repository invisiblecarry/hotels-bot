from typing import Dict, List, TypeVar
from ..common.models import db, BaseModel
from peewee import ModelSelect

T = TypeVar('T')


def _store_data(dtbs: db, model: T, **data: [Dict]) -> None:
    with dtbs.atomic():
        return model.create(**data)


def _retrive_data(dtbs: db, model: T, *columns: BaseModel) -> ModelSelect:
    with dtbs.atomic():
        response = model.select(*columns)

    return response



class CRUDInterface():
    @staticmethod
    def create():
        return _store_data

    @staticmethod
    def retrive():
        return _retrive_data


if __name__ == "__main__":
    _store_data()
    _retrive_data()
    CRUDInterface()
