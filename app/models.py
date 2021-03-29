from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy.orm import relationship, backref


class estrada_l_25(db.Model):
    id = db.Column("ogc_fid", db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    categoria = db.Column(db.String(50))
    matricula = db.Column(db.String(50))

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "categoria": self.categoria,
            "matricula": self.matricula,
        }


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    tramos = relationship("Tramo", secondary="tramo_user")

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Tramo(db.Model):
    __tablename__ = "tramo"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True)
    descripcion = db.Column(db.String(128))
    zona = db.Column(db.String(64))
    users = relationship("User", secondary="tramo_user")

    def __repr__(self):
        return "<Tramo {}>".format(self.nombre)


class Tramo_user(db.Model):
    __tablename__ = "tramo_user"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    tramo_id = db.Column(db.Integer, db.ForeignKey("tramo.id"))

    user = relationship(User, backref=backref(
        "tramo_user", cascade="all, delete-orphan"))
    tramo = relationship(Tramo, backref=backref(
        "tramo_user", cascade="all, delete-orphan"))


class Activo(db.Model):
    __tablename__ = "activo"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True)
    descripcion = db.Column(db.String(128))
    idtramo = db.Column(db.Integer, db.ForeignKey("tramo.id"))

    def __repr__(self):
        return "<Activo {}>".format(self.nombre)


class Activo(db.Model):
    __tablename__ = "componente"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True)
    descripcion = db.Column(db.String(128))
    idactivo = db.Column(db.Integer, db.ForeignKey("activo.id"))

    def __repr__(self):
        return "<Componente {}>".format(self.nombre)


class decisiones(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tramoId = db.Column(db.Integer)
    activo = db.Column(db.String(50))
    componente = db.Column(db.String(50))
    accion = db.Column(db.String(50))

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "id": self.id,
            "tramoId": self.tramoId,
            "activo": self.activo,
            "componente": self.componente,
            "accion": self.accion,
        }


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
