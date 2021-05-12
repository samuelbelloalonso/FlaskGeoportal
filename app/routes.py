from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user
from flask_login import LoginManager, login_required
from datetime import date
from pprint import pprint
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    redirect,
    jsonify,
    make_response,
)
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import simplejson as json

from app.models import User, accion
from app import db
from app.forms import RegistrationForm


Session = sessionmaker()
session = Session()


@app.route("/")
@app.route("/index")
@app.route("/geoportal", methods=["GET", "POST"])
@login_required
def consultasGeoportal():
    req = request.form
    if request.method == "POST":

        # obtenemos resultados y los metemos en una var
        texto = text(
            f""" SELECT json_build_object(
                'id',id,
                'nombre_activo', nombre,
                'id_tramo', idtramo
            )
            FROM activos2 a where a.idtramo = {req["tramo"]}
            """
        )

        resultado = db.engine.execute(texto)
        arrayJsons = [row[0] for row in resultado.fetchall()]
        return jsonify(tramos=arrayJsons)

    texto = text(
        """ SELECT json_build_object(
        'type', 'Feature',
        'geometry',  ST_AsGeoJSON(ST_Transform(geom, 4326),15,0)::json,
        'properties', json_build_object(
            'Tramo', nombre,
            'id', id
        )
    )
    FROM tramos2
    group by nombre, geom,id
    order by nombre
    """
    )
    resultado = db.engine.execute(texto)
    arrayResultado1 = [row[0] for row in resultado.fetchall()]

    return render_template(
        "geoportal.html",
        tramosJson=arrayResultado1,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("consultasGeoportal"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # print(f'user o pass invalidos {user}')
            flash("Invalid username or password")
            return redirect(url_for("login"))
        # print('logueando...')
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("consultasGeoportal"))
    return render_template("login.html", title="Sign In", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("consultasGeoportal"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/logout")
# @login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/consultasComponentes", methods=["GET"])
def consultasComponentesdef():
    if request.method == "GET":
        # obtenemos resultados y los metemos en una var
        texto = text(
            f""" SELECT json_build_object(
                'type', 'Feature',
                'id', id,
                'nombre', nombre,
                'id_activo', idactivo
            )
            FROM componentes2
            where idactivo = {request.args.get("activo",  type=int)}
            """
        )

        resultado = db.engine.execute(texto)
        arrayJsons = [row[0] for row in resultado.fetchall()]

    return render_template(
        "consultasComponentes.html",
        activoid=request.args.get("activo", 1, type=int),
        resultado=arrayJsons,
    )


@app.route("/consultasKpisConMediciones", methods=["GET"])
def consultasKpisConMedicionedef():
    if request.method == "GET":
        # obtenemos resultados y los metemos en una var

        texto = text(
            f""" SELECT json_build_object(
                'type', 'Feature',
                'idKpi', k.id,
                'nombreKpi',k.nombre,
                'idMedicion', m.id,
                'valor', m.valor,
                'idComponente', idcomponente
            )
            FROM medicion m join kpi k on m.idkpi = k.id
            where idcomponente = {request.args.get("componente",  type=int)}
            """
        )

        resultado = db.engine.execute(texto)
        arrayJsons = [row[0] for row in resultado.fetchall()]

    return render_template(
        "consultasKpisConMediciones.html",
        activoid=request.args.get("activo", type=int),
        componenteid=request.args.get("componente", 1, type=int),
        resultado=arrayJsons,
    )


@app.route("/componentesGeojson", methods=["GET"])
def consultasComponentesGeojsondef():
    if request.method == "GET":
        # obtenemos resultados y los metemos en una var
        texto = text(
            f""" SELECT json_build_object(
                'type', 'Feature',
                'geometry',  ST_AsGeoJSON(ST_Transform(geom, 4326),15,0)::json
            )
            FROM componentes2
            where id = {request.args.get("id_componente",  type=int)}
            """
        )

        resultado = db.engine.execute(texto)
        arrayJsons = [row[0] for row in resultado.fetchall()]
        resultado = jsonify(arrayJsons)

    return resultado


@app.route("/activosGeojson", methods=["GET"])
def paso2323():

    texto = text(
        f""" SELECT json_build_object(
            'type', 'Feature',
            'geometry',  ST_AsGeoJSON(ST_Transform(geom, 4326),15,0)::json,
            'properties', json_build_object(
            )
        )
        FROM activos2
        where id = {request.args.get("id_tramo", type=int)}

        """
    )

    resultado = db.engine.execute(texto)
    arrayJsons = [row[0] for row in resultado.fetchall()]
    res = jsonify(arrayJsons)

    return res


@app.route("/decisiones", methods=["GET", "POST"])
def decisionesdef():
    # si hay POST es que el usuario ya recibió el form y nos lo envia
    # if request.method == "POST":

    if request.method == "POST":

        # componenteid = request.args.get("componenteid", type=int)

        # for accion in request.form.items():
        #     print(accion[0][-1:])
        #     print(accion[1])

        componenteid = request.form["componenteid"]

        for key, decision in request.form.items():
            # print(f"{key}: {accion} -->  {componenteid}: {accion}")

            if "acciones" in key:
                idtipoaccion = key[-1:]

                new_row = accion(
                    fecha=date.today(),
                    idcomponente=componenteid,
                    idtipodeaccion=idtipoaccion,
                    nombre=decision,
                )

                db.session.add(new_row)

        db.session.commit()
        return redirect(url_for("decisionesdef"))

    #  renderizado de plantilla que se ejecuta cuando no recibimos POST. Es decir,
    #  cuando tenemos que enviarle al usuario el formulario
    #  para que el formulario "sepa" el tramo que vamos a editar lo recibiremos por GET
    return render_template(
        "formularioDecisiones.html",
        componenteid=request.args.get("componenteid", 1, type=int),
    )


@app.route("/activoycomponenteGeojson", methods=["GET"])
def pgeojsondef():

    texto1 = text(
        f""" SELECT json_build_object(
            'type', 'Feature',
            'geometry',  ST_AsGeoJSON(ST_Transform(geom, 4326),15,0)::json,
            'properties', json_build_object(
            )
        )
        FROM activos2
        where id = {request.args.get("id_activo", type=int)}

        """
    )

    resultado1 = db.engine.execute(texto1)
    activos = [row[0] for row in resultado1.fetchall()]

    texto = text(
        f""" SELECT json_build_object(
            'type', 'Feature',
            'geometry',  ST_AsGeoJSON(ST_Transform(geom, 4326),15,0)::json
        )
        FROM componentes2
        where id = {request.args.get("id_componente",  type=int)}
        """
    )

    resultado = db.engine.execute(texto)
    componentes = [row[0] for row in resultado.fetchall()]

    res = jsonify(activos=activos, componentes=componentes)

    return res


if __name__ == "__main__":
    app.run(debug=True)
    db.init_app(app)
    db.create_all()
