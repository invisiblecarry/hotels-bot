from database.utils.CRUD import CRUDInterface
from database.common.models import *

db.connect()
db.create_tables([RequestsHistory, ResultsHistory, RequestsResults])
crud = CRUDInterface()

if __name__ == "__main__":
    crud()
