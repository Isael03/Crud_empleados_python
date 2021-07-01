from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash
from flaskext.mysql import MySQL
from datetime import datetime
import os
# import json


app = Flask(__name__)
app.secret_key = 'User'

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistema_empleados'
mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA


@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)


@app.route("/")
def index():
    sql = "SELECT * FROM `empleados`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()
    # transformar resultado en diccionario y mostrarlo en json
    # empleados = [{'Id': col1, 'Nombre': col2, 'Correo': col3, 'Foto': col4}
    #              for (col1, col2, col3, col4) in cursor.fetchall()]
    # print(json.dumps(empleados))
    # print(empleados)

    conn.commit()
    return render_template('empleados/index.html', empleados=empleados)


@app.route('/create')
def create():
    return render_template('empleados/create.html')


@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    if _nombre == '' or _correo == '' or _foto == '':
        flash('Recuerda llenar los datos de los campos')
        return redirect(url_for('create'))

    now = datetime.now()
    tiempo = now.strftime('%Y%H%M%S')

    if _foto.filename != '':
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save('uploads/'+nuevoNombreFoto)

    datos = (_nombre, _correo, nuevoNombreFoto)

    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')


@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute('SELECT foto FROM empleados WHERE id=%s', id)
    fila = cursor.fetchall()

    try:
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
    except:
        print('Error al localizar imagen')

    cursor.execute('DELETE FROM empleados WHERE id=%s', (id))
    conn.commit()
    return redirect('/')


@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `empleados` WHERE id=%s;", id)
    empleado = cursor.fetchall()
    conn.commit()
    return render_template('empleados/edit.html', empleado=empleado)


@app.route('/update', methods=['POST'])
def update():

    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id = request.form['txtId']

    sql = 'UPDATE empleados SET nombre=%s, correo =%s WHERE id=%s;'
    datos = (_nombre, _correo, id)

    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now()
    tiempo = now.strftime('%Y%H%M%S')

    if _foto.filename != '':
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save('uploads/'+nuevoNombreFoto)

        cursor.execute('SELECT foto FROM empleados WHERE id=%s', id)
        fila = cursor.fetchall()

        try:
            os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        except:
            print('Error al localizar imagen')

        cursor.execute('UPDATE empleados SET foto=%s WHERE id=%s;',
                       (nuevoNombreFoto, id))

        conn.commit()

    cursor.execute(sql, datos)

    conn.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
