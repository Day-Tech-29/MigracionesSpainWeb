from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from google.cloud.dialogflowcx_v3.services.sessions import SessionsClient
from google.cloud.dialogflowcx_v3.types import session

# Inicializa la aplicación Flask y habilita CORS
app = Flask(__name__)
CORS(app)  # Permite solicitudes desde cualquier origen (para pruebas locales)

# Configura las credenciales desde el archivo JSON
file_path = 'ubicación del arcivo json con las credenciales'
print(f"Intentando cargar credenciales desde {file_path}...")
try:
    credentials = service_account.Credentials.from_service_account_file(
        file_path,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    print("Credenciales cargadas exitosamente.")
except Exception as e:
    print(f"Error al cargar las credenciales: {e}")
    raise

# Configura los parámetros del agente de Dialogflow CX
project_id = "Ingresar aquí la identificación del proyecto"
location = "Ingresar aquí la ubicación del agente"
agent_id = "Ingresar aquí el ID del agente, este se obtiene desde la url cuándo estás dentro del diagrama de flujo del mismo agente, "
language_code = "idioma esperado, en este momento se obtiene como es"

# Crea el cliente de sesiones con el endpoint regional
client = SessionsClient(
    credentials=credentials,
    client_options={"api_endpoint": "us-central1-dialogflow.googleapis.com"}
)
print("Cliente de sesiones creado.")

# Define una función para generar el session_path
def get_session_path(session_id):
    return client.session_path(project_id, location, agent_id, session_id)

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
                language_code=language_code
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