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
            FROM activo a where a.idtramo = {req["tramo"]}
            """
        )
        resultado = db.engine.execute(texto)
        arrayJsons = [row[0] for row in resultado.fetchall()]
        tramoId = arrayJsons[0]["id_tramo"]
        # return jsonify(tramos=arrayJsons, tramoNombre=tramoNombre)
        return render_template(
            "consultasActivos.html", activos=arrayJsons, tramoId=tramoId
        )

    texto = text(
        f""" SELECT json_build_object(
        'type', 'Feature',
        'geometry',  ST_AsGeoJSON(ST_Transform(geom, 4326),15,0)::json,
        'properties', json_build_object(
            'Tramo', t.nombre,
            'id', t.id
        )
    )
    FROM tramos t join usuario_tramos ut on t.id = ut.id_tramo
            where ut.id_user = {current_user.id}
    group by nombre, geom,id
    order by nombre
    """
    )
    print(current_user.id)
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
            flash("El nombre de usuario o contrase??a son incorrectos")
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
        flash("Felicidades, es usted un usuario registrado!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/logout")
# @login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/consultasComponentes", methods=["GET"])
@login_required
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
            FROM componente
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
@login_required
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


@app.route("/activosGeojson", methods=["GET"])
@login_required
def paso2323():

    texto = text(
        f""" SELECT json_build_object(
            'type', 'Feature',
            'geometry',  ST_AsGeoJSON(ST_Transform(geom, 4326),15,0)::json,
            'properties', json_build_object(
            )
        )
        FROM activo
        where id = {request.args.get("id_tramo", type=int)}

        """
    )

    resultado = db.engine.execute(texto)
    arrayJsons = [row[0] for row in resultado.fetchall()]
    res = jsonify(arrayJsons)

    return res


@app.route("/decisiones", methods=["GET", "POST"])
@login_required
def decisionesdef():
    # si hay POST es que el usuario ya recibi?? el form y nos lo envia
    # if request.method == "POST":

    if request.method == "POST":

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
@login_required
def geojsondef():

    consultaActivo = text(
        f""" SELECT json_build_object(
            'type', 'Feature',
            'geometry',  ST_AsGeoJSON(ST_Transform(geom, 4326),15,0)::json,
            'properties', json_build_object(
            )
        )
        FROM activo
        where id = {request.args.get("id_activo", type=int)}

        """
    )

    geojsonActivo = db.engine.execute(consultaActivo)
    activos = [row[0] for row in geojsonActivo.fetchall()]

    consultaComponente = text(
        f""" SELECT json_build_object(
            'type', 'Feature',
            'geometry',  ST_AsGeoJSON(ST_Transform(geom, 4326),15,0)::json
        )
        FROM componente
        where id = {request.args.get("id_componente",  type=int)}
        """
    )

    geojsonComponente = db.engine.execute(consultaComponente)
    componentes = [row[0] for row in geojsonComponente.fetchall()]

    res = jsonify(activos=activos, componentes=componentes)

    return res


if __name__ == "__main__":
    app.run(debug=True)
    db.init_app(app)
    db.create_all()
