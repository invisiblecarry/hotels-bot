from peewee import SqliteDatabase, Model, IntegerField, TextField, DateTimeField, ForeignKeyField
from datetime import datetime

# создание соединения с БД
db = SqliteDatabase('hotels.db')


# класс, чтобы наследовать от него все таблицы базы данных
class BaseModel(Model):
    class Meta:
        database = db


# модель таблицы истории запросов пользователя
class RequestsHistory(BaseModel):
    user_id = IntegerField()
    command = TextField()
    used_at = DateTimeField()
    searched = TextField()


# модель таблицы истории результатов
class ResultsHistory(BaseModel):
    search_result = TextField()
    hotel_id = IntegerField()
    hotel_name = TextField()
    address = TextField()
    photo_links = TextField()
    created_at = DateTimeField(default=datetime.utcnow())

    # добавьте здесь другие поля, если необходимо


# модель таблицы связи между историей команд и отелями
class RequestsResults(BaseModel):
    request_id = ForeignKeyField(RequestsHistory.id)
    result_id = ForeignKeyField(ResultsHistory.id)
    created_at = DateTimeField(default=datetime.utcnow())
    # добавьте здесь другие поля, если необходимо
