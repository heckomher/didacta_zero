from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware
from .models import Evento, Usuario
from .forms import EventoForm, CustomUserCreationForm, CustomAuthenticationForm


class UsuarioModelTest(TestCase):
    """Pruebas para el modelo Usuario"""
    
    def setUp(self):
        self.usuario_data = {
            'rut': '12345678-9',
            'password': 'testpassword123'
        }
    
    def test_crear_usuario(self):
        """Prueba la creación de un usuario normal"""
        usuario = Usuario.objects.create_user(**self.usuario_data)
        self.assertEqual(usuario.rut, '12345678-9')
        self.assertTrue(usuario.check_password('testpassword123'))
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
    
    def test_crear_superusuario(self):
        """Prueba la creación de un superusuario"""
        superusuario = Usuario.objects.create_superuser(**self.usuario_data)
        self.assertEqual(superusuario.rut, '12345678-9')
        self.assertTrue(superusuario.is_staff)
        self.assertTrue(superusuario.is_superuser)
        self.assertTrue(superusuario.is_active)
    
    def test_usuario_sin_rut(self):
        """Prueba que no se puede crear usuario sin RUT"""
        with self.assertRaises(ValueError):
            Usuario.objects.create_user(rut='', password='testpassword123')
    
    def test_str_usuario(self):
        """Prueba la representación string del usuario"""
        usuario = Usuario.objects.create_user(**self.usuario_data)
        self.assertEqual(str(usuario), '12345678-9')


class EventoModelTest(TestCase):
    """Pruebas para el modelo Evento"""
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            rut='12345678-9',
            password='testpassword123'
        )
        self.evento_data = {
            'titulo': 'Evento de Prueba',
            'descripcion': 'Descripción del evento de prueba',
            'fecha_inicio': timezone.now(),
            'fecha_fin': timezone.now() + timedelta(hours=2),
            'usuario': self.usuario
        }
    
    def test_crear_evento(self):
        """Prueba la creación de un evento"""
        evento = Evento.objects.create(**self.evento_data)
        self.assertEqual(evento.titulo, 'Evento de Prueba')
        self.assertEqual(evento.usuario, self.usuario)
        self.assertIsNotNone(evento.fecha_inicio)
        self.assertIsNotNone(evento.fecha_fin)
    
    def test_str_evento(self):
        """Prueba la representación string del evento"""
        evento = Evento.objects.create(**self.evento_data)
        self.assertEqual(str(evento), 'Evento de Prueba')
    
    def test_evento_multidia(self):
        """Prueba el método es_evento_multidia"""
        # Evento del mismo día
        evento_mismo_dia = Evento.objects.create(
            titulo='Evento mismo día',
            fecha_inicio=make_aware(datetime(2025, 10, 1, 9, 0)),
            fecha_fin=make_aware(datetime(2025, 10, 1, 17, 0)),
            usuario=self.usuario
        )
        self.assertFalse(evento_mismo_dia.es_evento_multidia())
        
        # Evento multi-día
        evento_multidia = Evento.objects.create(
            titulo='Evento multi-día',
            fecha_inicio=make_aware(datetime(2025, 10, 1, 18, 0)),
            fecha_fin=make_aware(datetime(2025, 10, 3, 10, 0)),
            usuario=self.usuario
        )
        self.assertTrue(evento_multidia.es_evento_multidia())
    
    def test_duracion_dias(self):
        """Prueba el método duracion_dias"""
        evento = Evento.objects.create(
            titulo='Evento 3 días',
            fecha_inicio=make_aware(datetime(2025, 10, 1, 9, 0)),
            fecha_fin=make_aware(datetime(2025, 10, 3, 17, 0)),
            usuario=self.usuario
        )
        self.assertEqual(evento.duracion_dias(), 3)
    
    def test_ocurre_en_fecha(self):
        """Prueba el método ocurre_en_fecha"""
        evento = Evento.objects.create(
            titulo='Evento para fecha',
            fecha_inicio=make_aware(datetime(2025, 10, 1, 9, 0)),
            fecha_fin=make_aware(datetime(2025, 10, 3, 17, 0)),
            usuario=self.usuario
        )
        
        # Fecha dentro del rango
        self.assertTrue(evento.ocurre_en_fecha(date(2025, 10, 2)))
        # Fecha de inicio
        self.assertTrue(evento.ocurre_en_fecha(date(2025, 10, 1)))
        # Fecha de fin
        self.assertTrue(evento.ocurre_en_fecha(date(2025, 10, 3)))
        # Fecha fuera del rango
        self.assertFalse(evento.ocurre_en_fecha(date(2025, 10, 4)))
    
    def test_clean_evento_invalido(self):
        """Prueba la validación de fechas"""
        evento = Evento(
            titulo='Evento inválido',
            fecha_inicio=timezone.now() + timedelta(hours=2),
            fecha_fin=timezone.now(),  # Fecha fin anterior a inicio
            usuario=self.usuario
        )
        with self.assertRaises(ValidationError):
            evento.clean()


class EventoFormTest(TestCase):
    """Pruebas para el formulario de eventos"""
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            rut='12345678-9',
            password='testpassword123'
        )
    
    def test_form_valido(self):
        """Prueba un formulario válido"""
        form_data = {
            'titulo': 'Evento de Prueba',
            'descripcion': 'Descripción del evento',
            'fecha_inicio': '2025-10-01T09:00',
            'fecha_fin': '2025-10-01T17:00'
        }
        form = EventoForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_sin_titulo(self):
        """Prueba formulario sin título"""
        form_data = {
            'descripcion': 'Descripción del evento',
            'fecha_inicio': '2025-10-01T09:00',
            'fecha_fin': '2025-10-01T17:00'
        }
        form = EventoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('titulo', form.errors)


class CustomUserCreationFormTest(TestCase):
    """Pruebas para el formulario de creación de usuarios"""
    
    def test_form_valido(self):
        """Prueba un formulario válido"""
        form_data = {
            'rut': '12345678-9',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_passwords_no_coinciden(self):
        """Prueba contraseñas que no coinciden"""
        form_data = {
            'rut': '12345678-9',
            'password1': 'testpassword123',
            'password2': 'testpassword456'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())


class AuthenticationFormTest(TestCase):
    """Pruebas para el formulario de autenticación"""
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            rut='12345678-9',
            password='testpassword123'
        )
    
    def test_form_valido(self):
        """Prueba autenticación válida"""
        form_data = {
            'username': '12345678-9',
            'password': 'testpassword123'
        }
        form = CustomAuthenticationForm(data=form_data)
        form.request = type('obj', (object,), {'META': {}})()  # Mock request
        self.assertTrue(form.is_valid())


class CalendarioViewsTest(TestCase):
    """Pruebas para las vistas del calendario"""
    
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            rut='12345678-9',
            password='testpassword123'
        )
        self.superusuario = Usuario.objects.create_superuser(
            rut='87654321-0',
            password='adminpassword123'
        )
        
        # Crear eventos de prueba
        self.evento_mismo_dia = Evento.objects.create(
            titulo='Evento Mismo Día',
            descripcion='Evento de un solo día',
            fecha_inicio=make_aware(datetime(2025, 10, 15, 9, 0)),
            fecha_fin=make_aware(datetime(2025, 10, 15, 17, 0)),
            usuario=self.usuario
        )
        
        self.evento_multidia = Evento.objects.create(
            titulo='Evento Multi-día',
            descripcion='Evento de varios días',
            fecha_inicio=make_aware(datetime(2025, 10, 20, 18, 0)),
            fecha_fin=make_aware(datetime(2025, 10, 23, 10, 0)),
            usuario=self.usuario
        )
    
    def test_vista_login_get(self):
        """Prueba la vista de login (GET)"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Iniciar Sesión')
    
    def test_vista_login_post_valido(self):
        """Prueba login con credenciales válidas"""
        response = self.client.post(reverse('login'), {
            'username': '12345678-9',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('calendario'))
    
    def test_vista_login_post_invalido(self):
        """Prueba login con credenciales inválidas"""
        response = self.client.post(reverse('login'), {
            'username': '12345678-9',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'RUT o contraseña inválidos')
    
    def test_vista_register(self):
        """Prueba la vista de registro"""
        response = self.client.post(reverse('register'), {
            'rut': '11111111-1',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Usuario.objects.filter(rut='11111111-1').exists())
    
    def test_vista_calendario_anual_sin_login(self):
        """Prueba acceso sin autenticación"""
        response = self.client.get(reverse('calendario_anual', args=[2025]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/calendario/login/', response.url)
    
    def test_vista_calendario_anual_con_login(self):
        """Prueba vista anual con usuario autenticado"""
        self.client.login(username='12345678-9', password='testpassword123')
        response = self.client.get(reverse('calendario_anual', args=[2025]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Calendario Anual 2025')
        self.assertContains(response, 'Octubre')
    
    def test_vista_calendario_mensual(self):
        """Prueba vista mensual"""
        self.client.login(username='12345678-9', password='testpassword123')
        response = self.client.get(reverse('calendario_mensual', args=[2025, 10]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Calendario Mensual')
    
    def test_vista_calendario_diario(self):
        """Prueba vista diaria"""
        self.client.login(username='12345678-9', password='testpassword123')
        response = self.client.get(reverse('calendario_diario', args=[2025, 10, 15]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Eventos para el')
        self.assertContains(response, 'Evento Mismo Día')
    
    def test_vista_calendario_semanal(self):
        """Prueba vista semanal"""
        self.client.login(username='12345678-9', password='testpassword123')
        response = self.client.get(reverse('calendario_semanal', args=[2025, 42]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Calendario Semanal')
    
    def test_vista_calendario_semanal_actual(self):
        """Prueba vista semanal actual"""
        self.client.login(username='12345678-9', password='testpassword123')
        response = self.client.get(reverse('calendario_semanal_actual'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Calendario Semanal')
    
    def test_logout(self):
        """Prueba cerrar sesión"""
        self.client.login(username='12345678-9', password='testpassword123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class EventoCRUDTest(TestCase):
    """Pruebas para las operaciones CRUD de eventos"""
    
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            rut='12345678-9',
            password='testpassword123'
        )
        self.superusuario = Usuario.objects.create_superuser(
            rut='87654321-0',
            password='adminpassword123'
        )
        self.evento = Evento.objects.create(
            titulo='Evento Original',
            descripcion='Descripción original',
            fecha_inicio=make_aware(datetime(2025, 10, 15, 9, 0)),
            fecha_fin=make_aware(datetime(2025, 10, 15, 17, 0)),
            usuario=self.superusuario
        )
    
    def test_crear_evento_sin_permisos(self):
        """Prueba crear evento sin permisos de admin"""
        self.client.login(username='12345678-9', password='testpassword123')
        response = self.client.get(reverse('evento_crear'))
        self.assertEqual(response.status_code, 302)  # Redirección por falta de permisos
    
    def test_crear_evento_con_permisos(self):
        """Prueba crear evento con permisos de admin"""
        self.client.login(username='87654321-0', password='adminpassword123')
        response = self.client.get(reverse('evento_crear'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Crear')
    
    def test_crear_evento_post(self):
        """Prueba crear evento via POST"""
        self.client.login(username='87654321-0', password='adminpassword123')
        response = self.client.post(reverse('evento_crear'), {
            'titulo': 'Nuevo Evento',
            'descripcion': 'Nueva descripción',
            'fecha_inicio': '2025-11-01T10:00',
            'fecha_fin': '2025-11-01T18:00'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Evento.objects.filter(titulo='Nuevo Evento').exists())
    
    def test_editar_evento(self):
        """Prueba editar evento"""
        self.client.login(username='87654321-0', password='adminpassword123')
        response = self.client.post(reverse('evento_editar', args=[self.evento.pk]), {
            'titulo': 'Evento Editado',
            'descripcion': 'Descripción editada',
            'fecha_inicio': '2025-10-15T10:00',
            'fecha_fin': '2025-10-15T18:00'
        })
        self.assertEqual(response.status_code, 302)
        evento_actualizado = Evento.objects.get(pk=self.evento.pk)
        self.assertEqual(evento_actualizado.titulo, 'Evento Editado')
    
    def test_eliminar_evento(self):
        """Prueba eliminar evento"""
        self.client.login(username='87654321-0', password='adminpassword123')
        response = self.client.post(reverse('evento_eliminar', args=[self.evento.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Evento.objects.filter(pk=self.evento.pk).exists())


class EventosMultidiaTest(TestCase):
    """Pruebas específicas para eventos de múltiples días"""
    
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            rut='12345678-9',
            password='testpassword123'
        )
        
        # Evento que se extiende por una semana
        self.evento_semana = Evento.objects.create(
            titulo='Evento de una Semana',
            descripcion='Evento que dura una semana completa',
            fecha_inicio=make_aware(datetime(2025, 10, 13, 9, 0)),  # Lunes
            fecha_fin=make_aware(datetime(2025, 10, 19, 17, 0)),    # Domingo
            usuario=self.usuario
        )
    
    def test_evento_aparece_en_vista_diaria(self):
        """Prueba que evento multi-día aparece en todas las fechas relevantes"""
        self.client.login(username='12345678-9', password='testpassword123')
        
        # Debe aparecer el lunes (inicio)
        response = self.client.get(reverse('calendario_diario', args=[2025, 10, 13]))
        self.assertContains(response, 'Evento de una Semana')
        
        # Debe aparecer el miércoles (medio)
        response = self.client.get(reverse('calendario_diario', args=[2025, 10, 15]))
        self.assertContains(response, 'Evento de una Semana')
        
        # Debe aparecer el domingo (fin)
        response = self.client.get(reverse('calendario_diario', args=[2025, 10, 19]))
        self.assertContains(response, 'Evento de una Semana')
        
        # No debe aparecer el día siguiente
        response = self.client.get(reverse('calendario_diario', args=[2025, 10, 20]))
        self.assertNotContains(response, 'Evento de una Semana')
    
    def test_evento_aparece_en_vista_semanal(self):
        """Prueba que evento multi-día aparece correctamente en vista semanal"""
        self.client.login(username='12345678-9', password='testpassword123')
        response = self.client.get(reverse('calendario_semanal', args=[2025, 42]))  # Semana 42 de 2025
        self.assertContains(response, 'Evento de una Semana')
    
    def test_evento_aparece_en_vista_mensual(self):
        """Prueba que evento multi-día aparece en vista mensual"""
        self.client.login(username='12345678-9', password='testpassword123')
        response = self.client.get(reverse('calendario_mensual', args=[2025, 10]))
        # El evento aparece truncado en la vista mensual
        self.assertContains(response, 'Evento de u')
    
    def test_evento_aparece_en_vista_anual(self):
        """Prueba que evento multi-día aparece en vista anual"""
        self.client.login(username='12345678-9', password='testpassword123')
        response = self.client.get(reverse('calendario_anual', args=[2025]))
        self.assertContains(response, 'Evento de una Semana')


class IntegracionCompleta(TestCase):
    """Pruebas de integración completas"""
    
    def setUp(self):
        self.client = Client()
        self.superusuario = Usuario.objects.create_superuser(
            rut='87654321-0',
            password='adminpassword123'
        )
    
    def test_flujo_completo_usuario(self):
        """Prueba el flujo completo: registro, login, crear evento, ver calendario"""
        # 1. Registro
        response = self.client.post(reverse('register'), {
            'rut': '22222222-2',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        })
        self.assertEqual(response.status_code, 302)
        
        # 2. Login automático después del registro
        self.assertTrue(Usuario.objects.filter(rut='22222222-2').exists())
        
        # 3. Logout y login manual
        self.client.get(reverse('logout'))
        response = self.client.post(reverse('login'), {
            'username': '22222222-2',
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, 302)
        
        # 4. Ver calendario (usuario normal no puede crear eventos)
        response = self.client.get(reverse('calendario'))
        self.assertEqual(response.status_code, 200)
    
    def test_flujo_admin_completo(self):
        """Prueba el flujo completo de un administrador"""
        # 1. Login como admin
        self.client.login(username='87654321-0', password='adminpassword123')
        
        # 2. Crear evento
        response = self.client.post(reverse('evento_crear'), {
            'titulo': 'Evento Admin',
            'descripcion': 'Evento creado por admin',
            'fecha_inicio': '2025-12-01T09:00',
            'fecha_fin': '2025-12-01T17:00'
        })
        self.assertEqual(response.status_code, 302)
        
        # 3. Verificar que aparece en el calendario
        response = self.client.get(reverse('calendario_mensual', args=[2025, 12]))
        self.assertContains(response, 'Evento Admin')
        
        # 4. Editar evento
        evento = Evento.objects.get(titulo='Evento Admin')
        response = self.client.post(reverse('evento_editar', args=[evento.pk]), {
            'titulo': 'Evento Admin Editado',
            'descripcion': 'Descripción editada',
            'fecha_inicio': '2025-12-01T10:00',
            'fecha_fin': '2025-12-01T18:00'
        })
        self.assertEqual(response.status_code, 302)
        
        # 5. Verificar la edición
        evento_actualizado = Evento.objects.get(pk=evento.pk)
        self.assertEqual(evento_actualizado.titulo, 'Evento Admin Editado')
        
        # 6. Eliminar evento
        response = self.client.post(reverse('evento_eliminar', args=[evento.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Evento.objects.filter(pk=evento.pk).exists())
