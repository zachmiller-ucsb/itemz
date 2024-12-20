from app import db

class Item(db.Model):
  __tablename__ = "items"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), nullable=False)
  description = db.Column(db.String(256), nullable=False)
  price = db.Column(db.Float, nullable=False)

  def __init__(self, name, description, price):
    self.name = name
    self.description = description
    self.price = price

  def __repr__(self):
    return f"<Item {self.name}>"