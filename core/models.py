
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class UsuarioManager(BaseUserManager):
    def create_user(self, rut, password=None, **extra_fields):
        if not rut:
            raise ValueError(_("El RUT es obligatorio"))
        user = self.model(rut=rut, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(rut, password, **extra_fields)

class Usuario(AbstractUser):
    rut = models.CharField(max_length=12, unique=True, verbose_name=_("RUT"))
    username = None  # Eliminar el campo username

    USERNAME_FIELD = "rut"
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    def __str__(self) -> str:
        return str(self.rut)

class Evento(models.Model):
    titulo = models.CharField(max_length=200, verbose_name=_("Título"))
    descripcion = models.TextField(blank=True, null=True, verbose_name=_("Descripción"))
    fecha_inicio = models.DateTimeField(verbose_name=_("Fecha de inicio"))
    fecha_fin = models.DateTimeField(verbose_name=_("Fecha de fin"))
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='eventos', verbose_name=_("Usuario"))

    objects = models.Manager()  # Agregar explícitamente el manager

    class Meta:
        verbose_name = _("Evento")
        verbose_name_plural = _("Eventos")
        ordering = ['fecha_inicio']

    def __str__(self):
        return self.titulo

    def clean(self):
        """Validar que la fecha de fin sea posterior a la fecha de inicio"""
        from django.core.exceptions import ValidationError
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError(_("La fecha de fin debe ser posterior a la fecha de inicio."))

    def es_evento_multidia(self):
        """Retorna True si el evento dura más de un día"""
        return self.fecha_inicio.date() != self.fecha_fin.date()

    def duracion_dias(self):
        """Retorna la cantidad de días que dura el evento"""
        return (self.fecha_fin.date() - self.fecha_inicio.date()).days + 1

    def ocurre_en_fecha(self, fecha):
        """Verifica si el evento ocurre en una fecha específica"""
        return self.fecha_inicio.date() <= fecha <= self.fecha_fin.date()


