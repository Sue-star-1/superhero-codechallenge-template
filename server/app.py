#!/usr/bin/env python3

from flask import Flask, request, jsonify
import flask_migrate
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = flask_migrate.Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


@app.route('/heroes')
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes])


@app.route('/heroes/<int:hero_id>')
def get_hero(hero_id):
    hero = db.session.get(Hero, hero_id)
    if not hero:
        return jsonify({'error': 'Hero not found'}), 404

    hero_powers = []
    for hp in hero.hero_powers:
        hero_powers.append({
            'id': hp.id,
            'hero_id': hp.hero_id,
            'power_id': hp.power_id,
            'strength': hp.strength,
            'power': hp.power.to_dict(only=('id', 'name', 'description'))
        })

    return jsonify({
        'id': hero.id,
        'name': hero.name,
        'super_name': hero.super_name,
        'hero_powers': hero_powers
    })


@app.route('/powers')
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict(only=('id', 'name', 'description')) for power in powers])


@app.route('/powers/<int:power_id>')
def get_power(power_id):
    power = db.session.get(Power, power_id)
    if not power:
        return jsonify({'error': 'Power not found'}), 404
    return jsonify(power.to_dict(only=('id', 'name', 'description')))


@app.route('/powers/<int:power_id>', methods=['PATCH'])
def patch_power(power_id):
    power = db.session.get(Power, power_id)
    if not power:
        return jsonify({'error': 'Power not found'}), 404

    data = request.get_json() or {}
    try:
        if 'description' in data:
            power.description = data['description']
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'errors': ['validation errors']}), 400

    return jsonify(power.to_dict(only=('id', 'name', 'description')))



@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json() or {}
    try:
        hero_power = HeroPower(
            strength=data.get('strength'),
            hero_id=data.get('hero_id'),
            power_id=data.get('power_id')
        )
        db.session.add(hero_power)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'errors': ['validation errors']}), 400

    return jsonify({
        'id': hero_power.id,
        'hero_id': hero_power.hero_id,
        'power_id': hero_power.power_id,
        'strength': hero_power.strength,
        'hero': hero_power.hero.to_dict(only=('id', 'name', 'super_name')),
        'power': hero_power.power.to_dict(only=('id', 'name', 'description'))
    })


if __name__ == '__main__':
    app.run(port=5555, debug=True)
