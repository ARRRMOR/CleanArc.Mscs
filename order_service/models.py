from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, ARRAY
from database import Base


class Order(Base):
    __tablename__ = "Orders"

    id = Column(Integer, primary_key=True, index=True)
    items = Column(JSONB)
    user_id = Column(Integer, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "items": self.items,
            "user_id": self.user_id
        }