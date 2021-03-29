from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user
from flask_login import LoginManager, login_required
from flask import render_template, flash, redirect, url_for, request, redirect, jsonify, make_response
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import simplejson as json

from app.models import User, Tramo, Tramo_user, estrada_l_25, decisiones
from app import db
from app.forms import RegistrationForm


# @app.route("/")
# @app.route("/index")
# @login_required
# def index():
#     return "Hello, World!"

Session = sessionmaker()
session = Session()


@app.route("/")
@app.route("/index")
@app.route("/consultasFilter", methods=["GET", "POST"])
@login_required
def consultasConFilter():
    reslist = []
    categorias = []

    if request.method == "POST":
        # obtenemos resultados y los metemos en una var
        req = request.form

        reslistUser = Tramo_user.query.filter(
            Tramo_user.user_id == current_user.id)
        listaIdTramos = []
        for x in reslistUser:
            listaIdTramos.append(x.tramo_id)

        # for x in reslistUser:
        #     print(x.user_id, x.tramo_id)

        reslist = estrada_l_25.query.filter_by(
            categoria=req["categoria"]).filter(estrada_l_25.id.in_(listaIdTramos))

        paginaResultado = request.args.get("page", 1, type=int)
        metadata = [
            {
                "pages": reslist.paginate(page=paginaResultado).pages,
                "page": reslist.paginate(page=paginaResultado).page,
                "total": reslist.paginate(page=paginaResultado).total,
                "per_page": reslist.paginate(page=paginaResultado).per_page,
                "has_next": reslist.paginate(page=paginaResultado).has_next,
                "has_prev": reslist.paginate(page=paginaResultado).has_prev,
                "prev_num": reslist.paginate(page=paginaResultado).prev_num,
                "next_num": reslist.paginate(page=paginaResultado).next_num,
            }
        ]

        resultadoConsulta = jsonify(
            metadata=metadata,
            json_list=[
                i.serialize for i in reslist.paginate(page=paginaResultado).items
            ],
        )

        return resultadoConsulta

    # consulta para obtener las categorías
    consulta_categoria = estrada_l_25.query.distinct("categoria")
    estradas_categorias = []
    for categoria in consulta_categoria:
        estradas_categorias.append(categoria.categoria)

    return render_template(
        "consultasFilter.html",
        tiposEstrada=estradas_categorias,
        titulo="Consulta completa",
    )


@app.route("/consultas", methods=["GET", "POST"])
@login_required
def consultasp1():
    reslist = []
    categorias = []

    if request.method == "POST":
        # obtenemos resultados y los metemos en una var
        req = request.form
        reslist = estrada_l_25.query.filter_by(categoria=req["categoria"])
        paginaResultado = request.args.get("page", 1, type=int)
        metadata = [
            {
                "pages": reslist.paginate(page=paginaResultado).pages,
                "page": reslist.paginate(page=paginaResultado).page,
                "total": reslist.paginate(page=paginaResultado).total,
                "per_page": reslist.paginate(page=paginaResultado).per_page,
                "has_next": reslist.paginate(page=paginaResultado).has_next,
                "has_prev": reslist.paginate(page=paginaResultado).has_prev,
                "prev_num": reslist.paginate(page=paginaResultado).prev_num,
                "next_num": reslist.paginate(page=paginaResultado).next_num,
            }
        ]

        resultadoConsulta = jsonify(
            metadata=metadata,
            json_list=[
                i.serialize for i in reslist.paginate(page=paginaResultado).items
            ],
        )

        return resultadoConsulta

    # consulta para obtener las categorías
    consulta_categoria = estrada_l_25.query.distinct("categoria")
    estradas_categorias = []
    for categoria in consulta_categoria:
        estradas_categorias.append(categoria.categoria)

    return render_template(
        "consultas.html",
        tiposEstrada=estradas_categorias,
        titulo="Consulta completa",
    )


@app.route("/consultasTramos", methods=["GET", "POST"])
@login_required
def consultasTramosdef():
    if request.method == "POST":
        # obtenemos resultados y los metemos en una var
        req = request.form
        reslist = estrada_l_25.query.filter_by(categoria=req["categoria"])
        texto = text(f""" SELECT json_build_object(
                'type', 'Feature',
                'id', ogc_fid,
                'tipo',tipo,
                'matricula', matricula,
                'categoria', categoria,
                'geometry', ST_AsGeoJSON(ST_Transform(wkb_geometry,4326))::json
            )
            FROM estrada_l_25
            where categoria = '{req["categoria"]}'
            """)

        resultado = db.engine.execute(texto)
        # arrayResultado = jsonify(
        #     json_list=[i.serialize for i in resultado.fetchall()])
        # arrayResultado = [row[0] for row in resultado.fetchall()]

        reslist2 = jsonify(json_list=[i.serialize for i in reslist.all()])
        return reslist2

    # Obtener las categorías para el seleccionar categorias.
    texto = text(""" SELECT json_build_object(
            'categoria', categoria
        )
        FROM estrada_l_25
        group by categoria
        """)
    resultado = db.engine.execute(texto)
    arrayResultado = [row[0] for row in resultado.fetchall()]
    arrayResultadoLimpio = [elemento["categoria"]
                            for elemento in arrayResultado]
    return render_template(
        "consultasTramos.html",
        tiposEstrada=arrayResultadoLimpio,
        titulo="Consulta completa",
    )


@ app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("consultasTramosdef"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # print(f'user o pass invalidos {user}')
            flash("Invalid username or password")
            return redirect(url_for("login"))
        # print('logueando...')
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("consultasTramosdef"))
    return render_template("login.html", title="Sign In", form=form)


@ app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("consultasTramosdef"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@ app.route("/logout")
# @login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@ app.route("/formularioInsert", methods=["GET", "POST"])
# @login_required
def forminsert():
    # si hay POST es que el usuario ya recibió el form y nos lo envia
    if request.method == "POST":
        tramo_a_editar = request.form["tramo"]

        for key, accion in request.form.items():
            if "acciones" in key:
                # FIXME: posible bug cuando el indice tenga >1 digitos
                componente = key[9:-4]
                print(f"{key}: {accion} --> {componente}: {accion}")
                new_row = decisiones(
                    tramoId=tramo_a_editar,
                    activo="estrada_l_25",
                    componente=componente,
                    accion=accion,
                )
                db.session.add(new_row)

        db.session.commit()

        return redirect(url_for("forminsert"))

    #  renderizado de plantilla que se ejecuta cuando no recibimos POST. Es decir,
    #  cuando tenemos que enviarle al usuario el formulario
    #  para que el formulario "sepa" el tramo que vamos a editar lo recibiremos por GET
    return render_template(
        "formularioDecisiones.html", tramoid=request.args.get("tramo", 1, type=int)
    )


@ app.route("/consultasActivos", methods=["GET", "POST"])
# @login_required
def consultasActivosdef():
    if request.method == "GET":
        # obtenemos resultados y los metemos en una var
        texto = text(f""" SELECT json_build_object(
                'type', 'Feature',
                'id', id,
                'nombre', nombre,
                'descripcion', descripcion,
                'idtramo', activo.idtramo
            )
            FROM activo
            where idTramo = {request.args.get("tramo",  type=int)}
            """)

        resultado = db.engine.execute(texto)
        arrayJsons = [row[0] for row in resultado.fetchall()]

    return render_template(
        "consultasActivos.html", tramoid=request.args.get("tramo", 1, type=int), resultado=arrayJsons
    )


@ app.route("/matriculas", methods=["GET"])
# @login_required
def getMatriculas():
    #  consulta que devuelve la fila con ese id
    row = estrada_l_25.query.filter_by(id=request.args.get("id_tramo"))
    # print(row[0].matricula)
    #  consulta que devuelve todas las matriculas iguales al anterior para pintarlas despues
    consulta = estrada_l_25.query.filter_by(matricula=row[0].matricula)
    lista = []
    for tramo in consulta:
        lista.append(tramo.id)
    resultadoConsulta = jsonify(json_list=lista)
    return resultadoConsulta


@app.route("/paso3", methods=["GET"])
def paso3():
    return f'hello world al tramo {request.args.get("tramo", 1, type=int)}'


@app.route("/consultasComponentes", methods=["GET"])
def consultasComponentesdef():
    if request.method == "GET":
        # obtenemos resultados y los metemos en una var
        texto = text(f""" SELECT json_build_object(
                'type', 'Feature',
                'id', id,
                'nombre', nombre,
                'descripcion', descripcion,
                'idactivo', componente.idactivo
            )
            FROM componente
            where idactivo = {request.args.get("activo",  type=int)}
            """)

        resultado = db.engine.execute(texto)
        arrayJsons = [row[0] for row in resultado.fetchall()]

    return render_template(
        "consultasComponentes.html", tramoid=request.args.get("activo", 1, type=int), resultado=arrayJsons
    )


if __name__ == "__main__":
    app.run(debug=True)
    db.init_app(app)
    db.create_all()
