from flask import Flask, jsonify, request
from flask_socketio import SocketIO

app = Flask(__name__)

# Inisialisasi objek SocketIO
socketio = SocketIO(app)

# Endpoint untuk menerima data dari Wemos
@app.route('/update_data', methods=['POST'])
def update_data():
    if request.method == 'POST':
        # Mengambil data yang dikirimkan oleh Wemos
        data = request.json  # Jika Wemos mengirim data dalam format JSON
        print("Data diterima:", data)
        
        # Lakukan pemrosesan atau simpan data ke database di sini
        
        # Memberikan respon bahwa data telah diterima
        return jsonify({"message": "Data berhasil diterima!"}), 200

@app.route('/routes')
def list_routes():
    output = []
    # Menampilkan semua route yang terdaftar
    for rule in app.url_map.iter_rules():
        output.append(f"{rule.endpoint}: {rule.rule}")
    return "<br>".join(output)  # Menampilkan route sebagai teks

if __name__ == '__main__':
    # Jalankan aplikasi Flask dengan SocketIO
    socketio.run(app, host='0.0.0.0', port=65432)

