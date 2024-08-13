from flask import Flask, render_template, request, jsonify, redirect, url_for
import googleapiclient.discovery
from google.cloud import monitoring_v3
import time

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

# Nueva función para obtener métricas de la instancia
def get_instance_metrics():
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project}"

    # Definir el recurso
    instance_id = instance_name  # Cambia esto según tu configuración
    resource = {
        "type": "gce_instance",
        "labels": {
            "project_id": project,
            "instance_id": instance_id,
        },
    }

    # Obtener métricas de CPU, RAM, GPU y espacio en disco
    metrics_data = {
        'cpu_usage': [],
        'ram_usage': [],
        'gpu_usage': [],
        'disk_space': []
    }

    # Función auxiliar para listar series de tiempo
    def list_time_series(metric_type):
        return client.list_time_series(
            request={
                "name": project_name,
                "filter": f'metric.type="{metric_type}" AND resource.type="gce_instance"',
                "interval": {
                    "end_time": {"seconds": int(time.time())},
                    "start_time": {"seconds": int(time.time()) - 3600},
                },
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
    # Obtener métricas de CPU
    cpu_metric = "compute.googleapis.com/instance/disk/write_bytes_count"
    for series in list_time_series(cpu_metric):
        for point in series.points:
            metrics_data['cpu_usage'].append(point.value.int64_value)

    # Obtener métricas de RAM
    ram_metric = "compute.googleapis.com/instance/memory/usage"
    for series in list_time_series(ram_metric):
        for point in series.points:
            metrics_data['ram_usage'].append(point.value.int64_value)

    # Obtener métricas de GPU (si la instancia tiene GPU)
    gpu_metric = "compute.googleapis.com/instance/gpu/utilization"
    for series in list_time_series(gpu_metric):
        for point in series.points:
            metrics_data['gpu_usage'].append(point.value.double_value)

    # Obtener espacio en disco
    disk_metric = "compute.googleapis.com/instance/disk/bytes_used"
    for series in list_time_series(disk_metric):
        for point in series.points:
            metrics_data['disk_space'].append(point.value.int64_value
                                              
    return metrics_data
    
@app.route('/')
def index():
    status = get_instance_status()
    metrics = get_instance_metrics()  # Obtener métricas de la instancia
    return render_template('index.html', status=status, metrics=metrics)

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
