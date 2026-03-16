from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth
from backend.firebase_config import get_firestore_client
import firebase_admin

db = get_firestore_client()

class FirebaseAuthentication(BaseAuthentication):
    """
    Leer el token JWT del encabezado. Lo va a validar con firebase y va a extraer el UID del usuario
    """
    def authenticate(self, request):
        # Extraemos el TOKEN
        auth_header = request.META.get('HTTP_AUTHORIZATION') or request.headers.get('Authorization')
        if not auth_header:
            return None # Si no hay token
        
        # El token viene "Bearer <<Token>>"
        partes = auth_header.split()

        if len(partes) != 2 or partes[0].lower() != 'bearer':
            return None
        
        token = partes[1]

        try:
            # Le pido a firebase que valide la firma del token
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token.get('uid')
            email = decoded_token.get('email')
            user_profile = db.collection('perfiles').document(uid).get()
            rol = user_profile.to_dict().get('rol', 'aprendiz') if user_profile.exists else 'aprendiz'

            # Usuario
            class FirebaseUser:
                def __init__(self, uid, rol, email):
                    self.uid = uid
                    self.rol = rol
                    self.email = email
                    self.is_authenticated = True

            return (FirebaseUser(uid, rol, email), decoded_token)
        
        except Exception as e:
            raise AuthenticationFailed(f"Token no es valido o esta expirado: {str(e)}")