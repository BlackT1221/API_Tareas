from google import genai
client = genai.Client(api_key="AIzaSyDo-YX0DmOaytCWira2DLm7i6NjBFhEpho")
for m in client.models.list():
    print(f"Modelo disponible: {m.name}")