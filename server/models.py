from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, validates

from config import db, bcrypt


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), nullable=False, unique=True)
    _password_hash = Column(String, nullable=False)
    image_url = Column(String)
    bio = Column(String)

    recipes = relationship("Recipe", back_populates="user")

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username must be present.")
        if self.__class__.query.filter_by(username=username).first():
            raise ValueError("Username must be unique.")
        return username

    @hybrid_property
    def _password_hash(self):
        raise AttributeError("Password is not a readable attribute.")

    @_password_hash.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password_hash(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    def __repr__(self) -> str:
        return f"username: {self.username}"


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=False)
    instructions = Column(String)
    minutes_to_complete = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="recipes")

    __table_args__ = (
        CheckConstraint("LENGTH(instructions) >= 50", name='check_instructions_length'),
    )

    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title must be present.")
        return title
