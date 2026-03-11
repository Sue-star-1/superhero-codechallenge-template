from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    hero_powers = db.relationship(
        'HeroPower',
        back_populates='hero',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    serialize_rules = ('-hero_powers.hero',)

    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    hero_powers = db.relationship(
        'HeroPower',
        back_populates='power',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    serialize_rules = ('-hero_powers.power',)

    @validates('description')
    def validate_description(self, key, value):
        if not value or not isinstance(value, str) or len(value.strip()) < 20:
            raise ValueError('description must be present and 20+ characters')
        return value

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id', ondelete='CASCADE'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id', ondelete='CASCADE'))

    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    serialize_rules = ('-hero.hero_powers', '-power.hero_powers',)

    @validates('strength')
    def validate_strength(self, key, value):
        valid_strengths = {'Strong', 'Weak', 'Average'}
        if value not in valid_strengths:
            raise ValueError('strength must be Strong, Weak, or Average')
        return value

    def __repr__(self):
        return f'<HeroPower {self.id}>'
