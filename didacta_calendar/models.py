from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

def validate_rut(value):
    """
    Custom validator for Chilean RUT.
    Validates format and length.
    """
    # Remove whitespace
    value = str(value).strip()
    
    # Check length
    if len(value) != 9:
        raise ValidationError('El RUT debe tener exactamente 9 caracteres')
        
    # Verify it contains only numbers and k
    if not (value[:-1].isdigit() and (value[-1].isdigit() or value[-1].lower() == 'k')):
        raise ValidationError('El RUT debe contener solo números y k como dígito verificador')

class CustomUser(AbstractUser):
    """Custom user model with RUT as username and specific profile"""
    
    class Profile(models.TextChoices):
        ADMINISTRATOR = 'ADM', 'Administrador'
        TEACHER = 'PRF', 'Profesor'
        MIXED = 'MIX', 'Mixto'

    # Override username to use RUT
    username = models.CharField(
        'RUT',
        max_length=9,
        unique=True,
        validators=[validate_rut],
        help_text='RUT de 9 caracteres sin puntos ni guión (ej: 123456789)',
        error_messages={
            'unique': 'Ya existe un usuario con este RUT.',
        }
    )
    
    # Make email required
    email = models.EmailField(
        'correo electrónico',
        unique=True,
        error_messages={
            'unique': 'Ya existe un usuario con este correo electrónico.',
        }
    )

    profile = models.CharField(
        'perfil',
        max_length=3,
        choices=Profile.choices,
        default=Profile.TEACHER,
        help_text='Tipo de perfil del usuario'
    )

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        ordering = ['username']

    def get_profile_display_name(self):
        """Get readable profile name"""
        return dict(self.Profile.choices)[self.profile]

    def __str__(self):
        """String representation of the user"""
        return f"{self.username} - {self.get_full_name() or 'Sin nombre'} - {self.get_profile_display_name()}"

    def clean(self):
        """Additional model validations"""
        super().clean()
        
        # Convert RUT to uppercase if it has K
        if self.username and self.username[-1].lower() == 'k':
            self.username = self.username[:-1] + 'K'
            
    def save(self, *args, **kwargs):
        """Override save method to ensure data cleaning"""
        self.clean()
        super().save(*args, **kwargs)
