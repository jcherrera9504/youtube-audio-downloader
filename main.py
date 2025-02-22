from flask import Flask, request, jsonify, send_from_directory
import os
import subprocess
import time

app = Flask(__name__)

# Carpeta para guardar los archivos descargados
DOWNLOADS_FOLDER = "downloads"
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

@app.route('/download', methods=['POST'])
def download():
    # Obtener la URL del video desde el cuerpo de la solicitud
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL no proporcionada"}), 400

    try:
        # Limpiar la carpeta `downloads` antes de descargar
        clean_downloads_folder()
        time.sleep(2)

        # Comando para descargar el audio usando yt-dlp
        output_path = os.path.join(DOWNLOADS_FOLDER, "%(title)s.%(ext)s")
        command = f"yt-dlp --geo-bypass -x --audio-format mp3 -o '{output_path}' {url}"
        print(f"Ejecutando comando: {command}")  # Mensaje de depuración

        # Ejecutar el comando
        subprocess.run(command, shell=True, check=True)

        # Esperar unos segundos para asegurarnos de que el archivo esté completamente descargado
        time.sleep(5)  # Retraso de 5 segundos (ajusta según sea necesario)

        # Verificar que el archivo descargado exista y tenga un tamaño mayor a cero
        downloaded_files = os.listdir(DOWNLOADS_FOLDER)
        if not downloaded_files:
            return jsonify({"error": "No se encontraron archivos descargados"}), 500

        # Asumimos que el primer archivo en la carpeta es el que necesitamos
        downloaded_file = downloaded_files[0]
        file_path = os.path.join(DOWNLOADS_FOLDER, downloaded_file)

        # Verificar que el archivo tenga un tamaño mayor a cero
        if os.path.getsize(file_path) == 0:
            return jsonify({"error": "El archivo descargado está vacío"}), 500

        # Devolver la ruta del archivo descargado
        return jsonify({
            "status": "success",
            "message": "Audio descargado correctamente",
            "file_url": f"/files/{downloaded_file}"
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Error al ejecutar yt-dlp: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    # Servir el archivo descargado
    return send_from_directory(DOWNLOADS_FOLDER, filename)

def clean_downloads_folder():
    """
    Elimina todos los archivos de la carpeta `downloads` antes de realizar una nueva descarga.
    """
    print("Limpiando la carpeta 'downloads'...")  # Mensaje de depuración
    try:
        for filename in os.listdir(DOWNLOADS_FOLDER):
            file_path = os.path.join(DOWNLOADS_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)  # Elimina el archivo
                    print(f"Archivo eliminado: {file_path}")
                elif os.path.isdir(file_path):
                    print(f"Saltando directorio: {file_path}")
            except Exception as e:
                print(f"No se pudo eliminar el archivo {file_path}: {e}")
    except Exception as e:
        print(f"Error al limpiar la carpeta 'downloads': {e}")

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))