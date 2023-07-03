from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from pymysql.cursors import DictCursor
from flaskext.mysql import MySQL
from datetime import datetime
import os

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'proyecto'
#app.config['SECRET_KEY'] = 'codoacodo'

UPLOADS = os.path.join('src/uploads')
app.config['UPLOADS'] = UPLOADS  # Guardamos la ruta como un valor en la app

mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor(cursor=DictCursor)


def queryMySql(query, data=None, tipoDeRetorno='none'):
    if data != None:
        cursor.execute(query, data)
    else:
        cursor.execute(query)

    if tipoDeRetorno == "one":
        registro = cursor.fetchone()
    else:
        registro = cursor.fetchall()

    if query.casefold().find("select") != -1:
        conn.commit()

    return registro


@app.route('/imagendepaquete/<path:nombreImagen>')
def uploads(nombreImagen):
    return send_from_directory(os.path.join('uploads'), nombreImagen)


@app.route('/')
def index():
    sql = "SELECT * FROM paquetes;"
    paquetes = queryMySql(sql, None, "all")

    return render_template('paquetes/index.html', paquetes=paquetes)


@app.route('/paquete/crear', methods=["GET", "POST"])
def alta_paquete():
    if request.method == "GET":
        return render_template('paquetes/create.html')
    elif request.method == "POST":
        _nombre = request.form['txtNombre']
        _precio = request.form['txtPrecio']
        _stock = request.form['txtStock']
        _imagen = request.files['txtImagen']

        if _nombre == '' or _precio == '' or _stock == '':
            flash('El nombre, el precio y el stock son obligatorios.')
            return redirect(url_for('alta_paquete'))

        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")

        if _imagen.filename != '':
            nuevoNombreImagen = tiempo + '_' + _imagen.filename
            _imagen.save("src/uploads/" + nuevoNombreImagen)

        sql = "INSERT INTO paquetes (nombre, precio, stock, imagen) values (%s, %s, %s, %s);"
        datos = (_nombre, _precio, _stock, nuevoNombreImagen)

        queryMySql(sql, datos)

        return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):
    sql = "SELECT imagen FROM paquetes WHERE id = (%s)"
    datos = [id]

    nombreImagen = queryMySql(sql, datos, "one")

    try:
        os.remove(os.path.join(app.config['UPLOADS'], nombreImagen[0]))
    except:
        pass

    sql = "DELETE FROM paquetes WHERE id = (%s)"
    queryMySql(sql, datos)

    return redirect('/')


@app.route('/modify/<int:id>')
def modify(id):
    sql = f'SELECT * FROM paquetes WHERE id={id}'
    cursor.execute(sql)
    paquete = cursor.fetchone()
    conn.commit()
    return render_template('paquetes/edit.html', paquete=paquete)


@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _precio = request.form['txtPrecio']
    _stock = request.form['txtStock']
    _imagen = request.files['txtImagen']
    id = request.form['txtId']

    # datos = (_nombre, _precio, _stock, id)

    if _imagen.filename != '':
        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        nuevoNombreImagen = tiempo + '_' + _imagen.filename
        _imagen.save("src/uploads/" + nuevoNombreImagen)

        sql = f'SELECT foto FROM paquetes WHERE id="{id}"'
        cursor.execute(sql)
        conn.commit()

        nombreImagen = cursor.fetchone()[0]

        try:
            os.remove(os.path.join(app.config['UPLOADS'], nombreImagen))
        except:
            pass

        sql = f'UPDATE paquetes SET imagen="{nuevoNombreImagen}" WHERE id="{id}";'
        cursor.execute(sql)
        conn.commit()

    sql = f'UPDATE paquetes SET nombre="{_nombre}", precio="{_precio}", stock="{_stock}" WHERE id="{id}"'
    cursor.execute(sql)
    conn.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
    