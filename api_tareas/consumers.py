import json
from channels.generic.websocket import AsyncWebsocketConsumer
from backend.firebase_config import get_firestore_client
from firebase_admin import firestore
from asgiref.sync import sync_to_async

db = get_firestore_client()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "adso_chat_global"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        mensaje = data["mensaje"]
        uid_usuario = data["uid_usuario"]

        # 1. Guardar en firestore el mensaje
        await self.guardar_mensaje_firestore(uid_usuario, mensaje)

        # 2. emitir el mensaje
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type' : 'chat_message',
                'mensaje': mensaje,
                'usuario': uid_usuario
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'mensaje': event['mensaje'],
            'usuario': event['usuario']
        }))
        
    @sync_to_async
    def guardar_mensaje_firestore(self, uid_usuario, mensaje):
        """
        Funcion para interactuar con firestore sin interrumpir el websocket
        """
        try:
            db.collection('api_chat_mensajes').add({
                'usuario': uid_usuario,
                'mensaje': mensaje,
                'timestamp' : firestore.SERVER_TIMESTAMP
            })

        except Exception as e:
            print(f"Error guardando el mensaje en BD: {e}")