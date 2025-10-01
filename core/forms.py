
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Evento, Usuario

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ["titulo", "descripcion", "fecha_inicio", "fecha_fin"]
        widgets = {
            "fecha_inicio": forms.DateTimeInput(attrs={
                "type": "datetime-local",
                "class": "form-control"
            }),
            "fecha_fin": forms.DateTimeInput(attrs={
                "type": "datetime-local",
                "class": "form-control"
            }),
            "titulo": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control"
            }),
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("rut",)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rut"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="RUT", max_length=12)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password"].widget.attrs.update({"class": "form-control"})

