# backend/app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from google.cloud.dialogflowcx_v3.services.sessions import SessionsClient
from google.cloud.dialogflowcx_v3.types import session
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Leer las variables de entorno
FILE_PATH = os.getenv("DIALOGFLOW_CREDENTIALS")
PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")
LOCATION = os.getenv("DIALOGFLOW_LOCATION")
AGENT_ID = os.getenv("DIALOGFLOW_AGENT_ID")
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE")

# Validar que las variables de entorno estén definidas
if not all([FILE_PATH, PROJECT_ID, LOCATION, AGENT_ID, LANGUAGE_CODE]):
    missing_vars = [var for var, val in [
        ("DIALOGFLOW_CREDENTIALS", FILE_PATH),
        ("DIALOGFLOW_PROJECT_ID", PROJECT_ID),
        ("DIALOGFLOW_LOCATION", LOCATION),
        ("DIALOGFLOW_AGENT_ID", AGENT_ID),
        ("LANGUAGE_CODE", LANGUAGE_CODE)
    ] if not val]
    raise ValueError(f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")

# Inicializa la aplicación Flask y habilita CORS
app = Flask(__name__)
CORS(app)  # Permite solicitudes desde cualquier origen (para pruebas locales)

# Configura las credenciales desde el archivo JSON
print(f"Intentando cargar credenciales desde {FILE_PATH}...")
try:
    credentials = service_account.Credentials.from_service_account_file(
        FILE_PATH,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    print("Credenciales cargadas exitosamente.")
except Exception as e:
    print(f"Error al cargar las credenciales: {e}")
    raise

# Crea el cliente de sesiones con el endpoint regional
client = SessionsClient(
    credentials=credentials,
    client_options={"api_endpoint": f"{LOCATION}-dialogflow.googleapis.com"}
)
print("Cliente de sesiones creado.")

# Define una función para generar el session_path
def get_session_path(session_id):
    return client.session_path(PROJECT_ID, LOCATION, AGENT_ID, session_id)

# Ruta para manejar las solicitudes de chat
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Extrae el mensaje del cuerpo de la solicitud
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400
        
        user_message = data['message']
        print(f"Recibido mensaje: {user_message}")

        # Genera un ID de sesión único
        session_id = "mi-sesion-123"

        # Configura la solicitud para Dialogflow CX
        session_path = get_session_path(session_id)
        request_dialogflow = session.DetectIntentRequest(
            session=session_path,
            query_input=session.QueryInput(
                text=session.TextInput(text=user_message),
                language_code=LANGUAGE_CODE
            )
        )

        # Hace la llamada a la API de Dialogflow
        print("Haciendo la llamada a la API...")
        response = client.detect_intent(request=request_dialogflow)

        # Extrae la respuesta del agente
        response_messages = response.query_result.response_messages
        responded = ""
        for message in response_messages:
            if hasattr(message, 'text') and message.text is not None:  # Verificación más robusta
                responded += " ".join(message.text.text if message.text.text else [])
                break

        if not responded:
            responded = "No se encontró una respuesta de texto. Revisa la configuración del flujo."

        print(f"Respuesta del agente: {responded}")
        return jsonify({"response": responded})

    except Exception as e:
        print(f"Error en la solicitud: {e}")
        return jsonify({"error": str(e)}), 500

# Inicia el servidor Flask
if __name__ == '__main__':
    print("Iniciando servidor Flask en http://localhost:5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)