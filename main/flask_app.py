from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/aeroconnect')
def aeroconnect():
    return redirect('http://localhost:5001')

@app.route('/TelecomNetPlanes')
def TelecomNetPlanes():
    return redirect('http://localhost:5002')

@app.route('/TelecomNetAgendamiento')
def TelecomNetAgendamiento():
    return redirect('http://localhost:5003')

@app.route('/TelecomNetTecnico')
def TelecomNetTecnico():
    return redirect('http://localhost:5004')


if __name__ == '__main__':
    app.run(port=5000)