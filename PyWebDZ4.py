import os
import socket
import json
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from datetime import datetime

app = Flask(__name__)

static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']

        send_message_to_socket(username, message)

    return render_template('message.html')

def send_message_to_socket(username, message):
    data = {
        "username": username,
        "message": message
    }
    
    udp_server_address = ('localhost', 5000)
    udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_client_socket.sendto(json.dumps(data).encode('utf-8'), udp_server_address)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(static_folder, 'static/' + filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

if __name__ == '__main__':
    import threading

    def socket_server():
        udp_server_address = ('localhost', 5000)
        udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server_socket.bind(udp_server_address)

        while True:
            data, addr = udp_server_socket.recvfrom(1024)
            data = json.loads(data.decode('utf-8'))
            timestamp = str(datetime.now())
            data_list = []

            try:
                with open('storage/data.json', 'r') as data_file:
                    data_list = json.load(data_file)
            except FileNotFoundError:
                data_list = []

            data_list.append({timestamp: data})

            with open('storage/data.json', 'w') as data_file:
                json.dump(data_list, data_file, indent=4)

    socket_thread = threading.Thread(target=socket_server)
    socket_thread.daemon = True
    socket_thread.start()

    app.run(port=3000)
