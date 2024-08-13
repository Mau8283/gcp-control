from flask import Flask, render_template, request, jsonify, redirect, url_for
import googleapiclient.discovery

app = Flask(__name__)

project = "micro-answer-431212-p0"
zone = "europe-west4-c"
instance_name = "instancia-pro"
PASSWORD = "yellbautista"  # Cambia esto por la contraseña que desees

def get_instance_status():
    compute = googleapiclient.discovery.build('compute', 'v1')
    result = compute.instances().get(project=project, zone=zone, instance=instance_name).execute()
    return result['status']

def start_instance():
    compute = googleapiclient.discovery.build('compute', 'v1')
    compute.instances().start(project=project, zone=zone, instance=instance_name).execute()

def stop_instance():
    compute = googleapiclient.discovery.build('compute', 'v1')
    compute.instances().stop(project=project, zone=zone, instance=instance_name).execute()

@app.route('/')
def index():
    status = get_instance_status()
    return render_template('index.html', status=status)

@app.route('/start', methods=['POST'])
def start():
    password = request.form.get('password')
    if password != PASSWORD:
        return jsonify(status="Access denied"), 403  # Denegar acceso si la contraseña es incorrecta

    start_instance()
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop():
    password = request.form.get('password')
    if password != PASSWORD:
        return jsonify(status="Access denied"), 403  # Denegar acceso si la contraseña es incorrecta

    stop_instance()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
