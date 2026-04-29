from flask import Flask, render_template
import socket
import platform

app = Flask(__name__)

@app.route("/")
def index():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    os_info = platform.system() + " " + platform.release()
    return render_template("index.html", hostname=hostname, ip=ip_address, os=os_info)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)