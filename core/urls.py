
from django.urls import path
from . import views

urlpatterns = [
    path("", views.calendario_view, name="calendario"),
    path("calendario/<int:year>/", views.calendario_view, name="calendario_anual"),
    path("calendario/<int:year>/<int:month>/", views.calendario_view, name="calendario_mensual"),
    path("calendario/<int:year>/<int:month>/<int:day>/", views.calendario_view, name="calendario_diario"),
    path("semana/", views.calendario_semanal_view, name="calendario_semanal_actual"),
    path("semana/<int:year>/<int:week>/", views.calendario_semanal_view, name="calendario_semanal"),
    path("evento/crear/", views.evento_crear, name="evento_crear"),
    path("evento/editar/<int:pk>/", views.evento_editar, name="evento_editar"),
    path("evento/eliminar/<int:pk>/", views.evento_eliminar, name="evento_eliminar"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]

