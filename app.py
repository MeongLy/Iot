from flask import Flask, render_template, jsonify, request
from flask_mysqldb import MySQL
from flask_socketio import SocketIO

app = Flask(__name__)

# Konfigurasi database MySQL
app.config['MYSQL_HOST']        = 'localhost'
app.config['MYSQL_USER']        = 'root'
app.config['MYSQL_PASSWORD']    = ''
app.config['MYSQL_DB']          = 'Monitoring'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Inisialisasi objek MySQL
mysql = MySQL(app)

# Menambahkan secret key untuk sesi
app.secret_key = '101202'

# Inisialisasi objek SocketIO
socketio = SocketIO(app)

# Route untuk halaman monitoring
@app.route('/')
def index():
    return render_template('monitoring.html')

# Route untuk mengambil data orang masuk dan keluar
@app.route('/data')
def get_data():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT orang_masuk, orang_keluar FROM counting ORDER BY ID DESC LIMIT 1")
    result = cursor.fetchone()
    
    if result:
        data = {
            'in': result['orang_masuk'],
            'out': result['orang_keluar']
        }
    else:
        data = {'in': 0, 'out': 0}
    
    return jsonify(data)

# Menambahkan route untuk daftar semua route yang ada
@app.route('/routes')
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():
        output.append(f"{rule.endpoint}: {rule.rule}")
    return "<br>".join(output)

# Tentukan event WebSocket
@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# Route untuk mereset data
@app.route('/reset', methods=['POST'])
def reset_data():
    cur = mysql.connection.cursor()
    
    # Menjalankan query untuk menghapus data orang masuk dan keluar
    cur.execute("UPDATE counting SET orang_masuk = 0, orang_keluar = 0, total = 0 WHERE id = 1")
    
    # Menyimpan perubahan ke database
    mysql.connection.commit()
    
    # Menutup cursor
    cur.close()

    # Emit data baru ke semua klien yang terhubung
    data = {'in': 0, 'out': 0}
    socketio.emit('update_data', data)  # Emit tanpa menggunakan broadcast=True

    return jsonify({'status': 'success'})

@app.route('/update_data', methods=['POST'])
def update_data():
    if request.method == 'POST':
        # Mengambil data dalam format JSON
        data = request.get_json()  # Mengambil data JSON dari request
        
        # Periksa apakah data lengkap
        id_value = data.get('ID')           # ID untuk menentukan data yang akan diupdate
        orang_masuk = data.get('orang_masuk')  # Nilai Orang Masuk
        orang_keluar = data.get('orang_keluar')  # Nilai Orang Keluar
        
        # Validasi input data
        if not id_value or not orang_masuk or not orang_keluar:
            return jsonify({"message": "Semua data harus diisi!"}), 400
        
        try:
            orang_masuk = int(orang_masuk)
            orang_keluar = int(orang_keluar)
        except ValueError:
            return jsonify({"message": "Input orang masuk dan keluar harus berupa angka!"}), 400

        # Gunakan cursor dari mysql.connection
        cursor = mysql.connection.cursor()

        # Update data di tabel counting tanpa menghitung total
        update_query = """
        UPDATE counting 
        SET orang_masuk = %s, orang_keluar = %s 
        WHERE ID = %s
        """
        cursor.execute(update_query, (orang_masuk, orang_keluar, id_value))
        mysql.connection.commit()  # Simpan perubahan ke database

        # Cek apakah data berhasil diupdate
        if cursor.rowcount > 0:
            cursor.close()  # Menutup cursor setelah query dijalankan
            return jsonify({"message": "Data berhasil diupdate!"}), 200
        else:
            cursor.close()  # Menutup cursor
            return jsonify({"message": "Data dengan ID tersebut tidak ditemukan."}), 404

# Menjalankan aplikasi dengan SocketIO
if __name__ == '__main__':
    # Jalankan aplikasi Flask dengan SocketIO
    socketio.run(app, host='0.0.0.0', port=65432)
