from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, CheckConstraint

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    favorites = db.relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
        }


class Planet(db.Model):
    __tablename__ = "planet"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), unique=True, nullable=False)
    climate = db.Column(db.String(80))
    terrain = db.Column(db.String(80))
    population = db.Column(db.String(40))

    favorites = db.relationship("Favorite", back_populates="planet")

    def __repr__(self):
        return f"<Planet id={self.id} name={self.name}>"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population
        }


class People(db.Model):
    __tablename__ = "people"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(20))
    birth_year = db.Column(db.String(20))

    favorites = db.relationship("Favorite", back_populates="people")

    def __repr__(self):
        return f"<People id={self.id} name={self.name}>"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "birth_year": self.birth_year
        }


class Favorite(db.Model):
    __tablename__ = "favorite"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"), nullable=True)
    people_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=True)

    user = db.relationship("User", back_populates="favorites")
    planet = db.relationship("Planet", back_populates="favorites")
    people = db.relationship("People", back_populates="favorites")

    __table_args__ = (
        # evita duplicados
        UniqueConstraint("user_id", "planet_id", name="uq_user_planet_fav"),
        UniqueConstraint("user_id", "people_id", name="uq_user_people_fav"),

   
        CheckConstraint(
            "(planet_id IS NOT NULL AND people_id IS NULL) OR (planet_id IS NULL AND people_id IS NOT NULL)",
            name="ck_favorite_one_target"
        ),
    )

    def __repr__(self):
        if self.planet_id is not None:
            return f"<Favorite id={self.id} user_id={self.user_id} planet_id={self.planet_id}>"
        if self.people_id is not None:
            return f"<Favorite id={self.id} user_id={self.user_id} people_id={self.people_id}>"
        return f"<Favorite id={self.id} user_id={self.user_id} empty>"

    def serialize(self):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "people_id": self.people_id,
        }

        if self.planet_id is not None and self.planet is not None:
            data.update({"type": "planet", "planet": self.planet.serialize()})

        elif self.people_id is not None and self.people is not None:
            data.update({"type": "people", "people": self.people.serialize()})

        else:
            data.update({"type": "unknown"})

        return data
