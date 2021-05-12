from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class accion(db.Model):
    __tablename__ = "accion"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64))
    fecha = db.Column(db.DATETIME)
    idcomponente = db.Column(db.Integer)
    idtipodeaccion = db.Column(db.Integer)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# u = User(username="samu1")
# t = Tramo(nombre='tramo a', descripcion='este tramo es el a', zona='zona a')
# tu = Tramo_user(user_id=1,tramo_id=2)
# db.session.add(u)
# db.session.add(t)
# db.session.add(tu)
# db.session.commit()

# flask db migrate -m "update"
# flask db upgrade

#  from app.models import User
#  from app.models import Tramo

# t1 = Tramo(nombre='tramo a', descripcion='este tramo es el a', zona='zona a')
# t2=  Tramo(nombre='tramo b', descripcion='este tramo es el b', zona='zona b')
# t3=  Tramo(nombre='tramo c', descripcion='este tramo es el c', zona='zona c')
# t4 = Tramo(nombre='tramo d', descripcion='este tramo es el d', zona='zona d')
# t5 = Tramo(nombre='tramo e', descripcion='este tramo es el e', zona='zona e')
# t6 = Tramo(nombre='tramo f', descripcion='este tramo es el f', zona='zona f')
# t7 = Tramo(nombre='tramo g', descripcion='este tramo es el g', zona='zona g')
# t8 = Tramo(nombre='tramo h', descripcion='este tramo es el h', zona='zona h')


# db.session.add(t1)
# db.session.add(t2)
# db.session.add(t3)
# db.session.add(t4)
# db.session.add(t5)
# db.session.add(t6)
# db.session.add(t7)
# db.session.add(t8)

# t1 = Tramo_user(user_id=2, tramo_id=1)
# t2 = Tramo_user(user_id=2, tramo_id=2)
# t3 = Tramo_user(user_id=2, tramo_id=3)
# t4 = Tramo_user(user_id=2, tramo_id=4)
# t5 = Tramo_user(user_id=2, tramo_id=5)
