from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError

def validate_rut(value):
    if not value.isalnum():  # Verifica que solo contenga letras y números
        raise ValidationError('El RUT solo debe contener letras y números')
    if len(value) != 9:
        raise ValidationError('El RUT debe tener exactamente 9 caracteres')

class CustomUser(AbstractUser):
    """Modelo de usuario personalizado con RUT como username y perfil específico"""
    
    class Perfil(models.TextChoices):
        ADMINISTRADOR = 'ADM', 'Administrador'
        PROFESOR = 'PRF', 'Profesor'
        MIXTO = 'MIX', 'Mixto'

    # Sobreescribimos username para usar RUT
    username = models.CharField(
        'RUT',
        max_length=9,
        unique=True,
        validators=[
            MinLengthValidator(9),
            MaxLengthValidator(9),
            validate_rut
        ],
        help_text='RUT de 9 caracteres sin puntos ni guión',
        error_messages={
            'unique': 'Ya existe un usuario con este RUT.',
        }
    )

    perfil = models.CharField(
        max_length=3,
        choices=Perfil.choices,
        default=Perfil.PROFESOR,
        help_text='Tipo de perfil del usuario'
    )

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return f"{self.username} - {self.get_perfil_display()}"
