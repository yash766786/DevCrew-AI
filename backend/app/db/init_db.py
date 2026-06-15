from app.db.database import engine
from app.db.models import *

Base.metadata.create_all(bind=engine)
print("Database created")