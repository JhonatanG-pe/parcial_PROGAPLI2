from flask import Flask, render_template, request, redirect, jsonify

import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cur  = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            nombre   TEXT NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo      TEXT UNIQUE NOT NULL,
            nombre      TEXT NOT NULL,
            descripcion TEXT,
            precio      REAL NOT NULL,
            stock       INTEGER NOT NULL,
            categoria   TEXT
        )
    ''')
    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO usuarios (username, password, nombre) VALUES (?, ?, ?)",
            [('admin', '1234', 'Administrador'), 
             ('juan', 'pass1', 'Juan García')
             ]
        )
    cur.execute("SELECT COUNT(*) FROM productos")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO productos (codigo, nombre, descripcion, precio, stock, categoria) VALUES (?, ?, ?, ?, ?, ?)",
            [
                ('P001', 'Laptop HP 15',    'Laptop HP Core i5 8GB RAM 512GB SSD',  2899.90, 15, 'Electrónica'),
                ('P002', 'Mouse Logitech',  'Mouse inalámbrico ergonómico 1600 DPI',   89.90, 50, 'Accesorios'),
                ('P003', 'Teclado Mecánico','Teclado mecánico RGB switches Blue',    199.90, 30, 'Accesorios'),
            ]
        )
    conn.commit()
    conn.close()

app = Flask(__name__)
@app.route('/',methods=['GET', 'POST'])
def login():

    if request.method== 'POST':
        print(request.form)
        usuario = request.form['usuario']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (usuario, password))

        user = cur.fetchone()
        conn.close()

        if user:
            return redirect('/principal')
        return render_template(
            'login.html',
            mensaje = "Usuario y/o contraseña incorrectas"
        )

    return render_template('login.html')

@app.route('/principal')
def principal():
    return render_template('principal.html')

@app.route('/buscador')
def buscador():
    return render_template('buscador.html')

@app.route('/api/buscar_producto' , methods=['POST'])
def buscar_producto():
    data = request.get_json()
    codigo = data.get('codigo', '')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos WHERE codigo=?", (codigo,))
    producto = cur.fetchone()
    conn.close()

    if producto:
        return jsonify({
            'encontrado': True,
            'id': producto[0],
            'codigo': producto[1],
            'nombre': producto[2],
            'descripcion': producto[3],
            'precio': producto[4],
            'stock': producto[5],
            'categoria': producto[6]
        })  
    else:
        return jsonify({'encontrado': False, 'mensaje': f'Producto {codigo} no encontrado'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

