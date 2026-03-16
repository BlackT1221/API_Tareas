import requests
import time
import getpass
from google import genai
from google.genai import types

# --- 1. FUNCIÓN DE LOGIN ---
def login_usuario():
    print("--- 🔐 Login de Aprendiz/Instructor ---")
    email = input("Email: ")
    password = getpass.getpass("Contraseña: ")
    url_login = "http://127.0.0.1:8000/api/auth/login/"
    try:
        response = requests.post(url_login, json={"email": email, "password": password})
        if response.status_code == 200:
            print("✅ Autenticación exitosa.")
            return response.json().get('token')
        print(f"❌ Error: {response.json().get('error')}")
    except Exception as e:
        print(f"⚠️ Error de conexión: {e}")
    return None

def eliminar_mi_tarea():
    #to do: Implementar la logica
    return None

# --- 2. HERRAMIENTA ---
def consultar_mis_tareas(token_firebase: str):
    """Consulta las tareas del usuario logueado en la base de datos de Django."""
    print("\n[SISTEMA] 🔍 Consultando API de Django...")
    url = "http://127.0.0.1:8000/api/tareas/"
    headers = {"Authorization": f"Bearer {token_firebase}"}
    print(f"Enviando cabeceras: {headers}")
    
    try:
        res = requests.get(url, headers=headers)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

# --- 3. CONFIGURACIÓN IA ---
# ¡IMPORTANTE! Genera una llave nueva y NO la compartas, Chris. 
# Las anteriores ya están invalidadas por seguridad.
# --- CONFIGURACIÓN ---
API_KEY = "AIzaSyDo-YX0DmOaytCWira2DLm7i6NjBFhEpho" 
client = genai.Client(api_key=API_KEY)

# Cambiamos al modelo que SÍ está en tu lista:
modelo_id = "gemini-2.5-flash"

# --- 4. FLUJO PRINCIPAL ---
token = login_usuario()

if token:
    print("\n🤖 IA: ¡Hola! Soy tu asistente de ADSO. ¿Qué deseas consultar hoy?")
    
    while True:
        user_input = input("\nTú: ")
        if user_input.lower() in ['salir', 'exit', 'bye']: break
    
        # Sé muy específico aquí:
        prompt = (
            f"Instrucción: Eres un asistente para ADSO. "
            f"Para cualquier consulta técnica, utiliza EXCLUSIVAMENTE este token de Firebase: {token}. "
            f"IMPORTANTE: No uses tu propia API Key. "
            f"Pregunta del usuario: {user_input}"
        )
    
        try:
            response = client.models.generate_content(
                model=modelo_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[consultar_mis_tareas]
                )
            )
            print(f"🤖 IA: {response.text}")
            
        except Exception as e:
            # Manejo inteligente de errores para la clase
            error_str = str(e)
            if "429" in error_str:
                print("⚠️ IA: Agotamos las peticiones gratuitas del minuto. Espera 20 segundos...")
                time.sleep(20)
            elif "404" in error_str:
                print("⚠️ IA: Error de versión de modelo. Intentando reconectar...")
                # Aquí podrías intentar cambiar el modelo_id dinámicamente
            else:
                print(f"⚠️ Ups! Algo pasó: {e}")