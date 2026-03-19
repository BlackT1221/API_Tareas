from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import TareasSerializer
from .authentication import FirebaseAuthentication
from backend.firebase_config import get_firestore_client
from firebase_admin import firestore

db = get_firestore_client()

class TareaAPIView(APIView):
    # Traemos nuestro guardia de seguridad
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    
    """
    Endpoint para listar todas las tareas (GET) y crear una nueva tarea (POST)
    """
    def get(self, request):
        """
        Lista tareas con paginación. 
        Instructores: Ven todo.
        Aprendices: Solo lo propio.
        """
        rol = request.user.rol
        uid = request.user.uid
        
        # Parámetros de consulta
        limit = int(request.query_params.get('limit', 10))
        last_doc_id = request.query_params.get('last_doc_id')

        # 1. Definir la base de la consulta según el ROL
        if rol == 'instructor':
            # El instructor no tiene filtros de usuario
            query = db.collection('api_tareas')
            mensaje = "Listado completo (Rol: Instructor)"
        else:
            # El aprendiz solo filtra por su UID
            query = db.collection('api_tareas').where('usuario_id', '==', uid)
            mensaje = "Listado personal (Rol: Aprendiz)"

        # 2. Ordenar (Indispensable para usar start_after)
        query = query.order_by('fecha_creacion')

        # 3. Lógica de Paginación (start_after)
        if last_doc_id:
            last_doc = db.collection('api_tareas').document(last_doc_id).get()
            if last_doc.exists:
                query = query.start_after(last_doc)

        # 4. Aplicar límite y ejecutar
        docs = query.limit(limit).stream()
        
        tareas = []
        for doc in docs:
            t = doc.to_dict()
            t['id'] = doc.id
            tareas.append(t)
            
        # 5. Respuesta estructurada
        return Response({
            "mensaje": mensaje,
            "total_en_pagina": len(tareas),
            "datos": tareas,
            "next_page_token": tareas[-1]['id'] if tareas else None
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        # 1. Pasar el JSON al serializador para que valide los campos

        serializer = TareasSerializer(data=request.data)

        #2. Si el json cumple las reglas:
        if serializer.is_valid():
            datos_validados = serializer.validated_data

            datos_validados['usuario_id'] = request.user.uid
            datos_validados['fecha_creacion'] = firestore.SERVER_TIMESTAMP

            try:
                #3. Guardamos los datos en Firestore
                nuevo_doc = db.collection('api_tareas').add(datos_validados)
                # Obtener el id generado
                id_generado = nuevo_doc[1].id

                return Response({
                    "mensaje": "Tarea creada correctamente",
                    "id": id_generado
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, tarea_id=None):
        if not tarea_id:
            return Response({"error": "ID requerido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tarea_ref = db.collection('api_tareas').document(tarea_id)
            doc = tarea_ref.get()

            if not doc.exists:
                return Response({"error": "No encontrado"}, status=status.HTTP_404_NOT_FOUND)

            tarea_data = doc.to_dict()

            # CORRECCIÓN: Usar .uid (o .id según tu FirebaseAuthentication)
            # y validar si el usuario es Instructor para permitirle editar todo si quieres
            if tarea_data.get('usuario_id') != request.user.uid and request.user.rol != 'instructor':
                return Response(
                    {"error":"No tienes permiso para editar esta tarea"},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = TareasSerializer(data=request.data, partial=True)
            if serializer.is_valid():
                tarea_ref.update(serializer.validated_data)
                return Response({
                    "mensaje": f"Tarea {tarea_id} actualizada",
                    "datos": serializer.validated_data
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, tarea_id):
        if not tarea_id:
            return Response({"Error":"Se requiere el id"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            tarea_ref = db.collection('api_tareas').document(tarea_id)
            doc = tarea_ref.get() # CORRECCIÓN: Guardar el documento en la variable 'doc'

            if not doc.exists:
                return Response({"error": "No encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            tarea_data = doc.to_dict()

            # CORRECCIÓN: Usar .uid y permitir al instructor borrar
            if tarea_data.get('usuario_id') != request.user.uid and request.user.rol != 'instructor':
                return Response(
                    {"error":"No tienes permiso para eliminar esta tarea"},
                    status=status.HTTP_403_FORBIDDEN
                )

            tarea_ref.delete()
            return Response(
                {"mensaje": f"Tarea {tarea_id} eliminada correctamente"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)