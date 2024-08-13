# Usar una imagen base oficial de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de la aplicación
COPY . .

# Instalar las dependencias
RUN pip install --no-cache-dir Flask google-api-python-client google-cloud-monitoring gunicorn

# Comando para correr la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
