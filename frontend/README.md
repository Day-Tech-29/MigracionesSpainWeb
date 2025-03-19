# MigracionesSpainWeb
Esta es una página diseñada para brindar información precisa y fácil de entender a personas inmigrantes que buscan asilo a través de chatbot que está impulso por un modelo RAG con base en Vertex AI.

version 0.1
Se crea la página web dónde se muestra el botón de inicio y el botón que te dirige a los avisos legales
Se generan los textos explicando los avisos legales
Se genera la interfaz de la página de inicio

version 0.2
Se genera la llamada de api, la transformación de la respuesta y la interfaz del chat. 
Para hacer que la llamada a a la api funcione necesitas configurar unas cosas antes
# En app.py
identificaciones necesarias: 
project_id = "Ingresar aquí la identificación del proyecto"
location = "Ingresar aquí la ubicación del agente"
agent_id = "Ingresar aquí el ID del agente, este se obtiene desde la url cuándo estás dentro del diagrama de flujo del mismo agente, "
language_code = "idioma esperado, en este momento se obtiene como es"

La mayoría de los datos puedes encontrarlos ingresando al diagrama de tu agente en Dialogflow CX y en la url podrás encontrar los datos
https://dialogflow.cloud.google.com/cx/projects/{project_id}/locations/{location}/agents/{agent_id}

Tambien requerirás un archivo json con las identificaciones de cuenta de servicio, este se encuentra en IAM y administracion / cuenta de servicio.
Esta se hará referencia en file_path, en app.py

Considera que el servicio también requiere un session_id pero debido a la maduración este no requiere que tenga una estructura en especifico. 
session_id = "mi-sesion-123"