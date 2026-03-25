from django.urls import path
from .views import TareaAPIView
from .views_auth import RegistroAPIView, LoginAPIView
from .views_perfil import PerfilAPIView
from .views_chat import ChatHistorialAPIView

urlpatterns = [
    path('auth/registro/', RegistroAPIView.as_view(), name='api_registro'),
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),

    path('tareas/', TareaAPIView.as_view(), name='api_tareas'),
    path('tareas/<str:tarea_id>/', TareaAPIView.as_view(), name='api_tarea_detalle'),

    path('perfil/foto/', PerfilAPIView.as_view(), name='api_perfil_foto'),
    path('perfil/', PerfilAPIView.as_view(), name='api_perfil'),
    path('chat/historial/', ChatHistorialAPIView.as_view(), name='api_chat_historial'),
]