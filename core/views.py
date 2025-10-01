
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Evento, Usuario
from .forms import EventoForm, CustomUserCreationForm, CustomAuthenticationForm
import calendar
from datetime import date, timedelta, datetime

def is_admin(user):
    return user.is_superuser

@login_required
def calendario_view(request, year=None, month=None, day=None):
    today = date.today()
    
    # Si no se especifica año, usar el año actual
    year = int(year) if year else today.year
    
    # Vista Diaria
    if day is not None:
        month = int(month) if month else today.month
        day = int(day)
        selected_date = date(year, month, day)
        
        # Obtener eventos que ocurren en esta fecha específica
        # Incluye eventos que inician, terminan o se extienden durante este día
        eventos_dia = Evento.objects.filter(
            usuario=request.user,
            fecha_inicio__date__lte=selected_date,  # Inicia en o antes de esta fecha
            fecha_fin__date__gte=selected_date      # Termina en o después de esta fecha
        ).order_by("fecha_inicio")
        
        return render(request, "core/calendario_diario.html", {
            "selected_date": selected_date,
            "eventos": eventos_dia,
            "is_admin": request.user.is_superuser
        })

    # Vista Mensual
    elif month is not None:
        month = int(month)
        cal = calendar.Calendar()
        month_days = cal.monthdatescalendar(year, month)
        
        # Obtener eventos que ocurren durante este mes
        # Incluye eventos que inician, terminan o se extienden durante este mes
        primer_dia_mes = datetime(year, month, 1).date()
        if month == 12:
            ultimo_dia_mes = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            ultimo_dia_mes = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        eventos_mes = Evento.objects.filter(
            usuario=request.user,
            fecha_inicio__date__lte=ultimo_dia_mes,  # Inicia en o antes del último día del mes
            fecha_fin__date__gte=primer_dia_mes      # Termina en o después del primer día del mes
        ).order_by("fecha_inicio")
        
        return render(request, "core/calendario_mensual.html", {
            "year": year,
            "month": month,
            "month_days": month_days,
            "eventos": eventos_mes,
            "is_admin": request.user.is_superuser
        })

    # Vista Anual (cuando year está especificado pero month y day no)
    # O vista por defecto (cuando accede a /calendario/ sin parámetros - mostrará el año actual)
    else:
        # Nombres de meses en español
        nombres_meses = [
            '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        
        # Crear una lista de todos los meses del año con sus eventos
        meses_con_eventos = []
        total_eventos = 0
        mes_mas_activo = ""
        max_eventos_mes = 0
        meses_con_eventos_count = 0
        
        for mes in range(1, 13):
            nombre_mes = nombres_meses[mes]
            
            # Calcular el primer y último día del mes
            primer_dia_mes = datetime(year, mes, 1).date()
            if mes == 12:
                ultimo_dia_mes = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                ultimo_dia_mes = datetime(year, mes + 1, 1).date() - timedelta(days=1)
            
            # Obtener eventos que ocurren durante este mes
            # Incluye eventos que inician, terminan o se extienden durante este mes
            eventos_mes = Evento.objects.filter(
                usuario=request.user,
                fecha_inicio__date__lte=ultimo_dia_mes,  # Inicia en o antes del último día del mes
                fecha_fin__date__gte=primer_dia_mes      # Termina en o después del primer día del mes
            ).order_by("fecha_inicio")
            
            cantidad_eventos = eventos_mes.count()
            total_eventos += cantidad_eventos
            
            if cantidad_eventos > 0:
                meses_con_eventos_count += 1
                
            if cantidad_eventos > max_eventos_mes:
                max_eventos_mes = cantidad_eventos
                mes_mas_activo = nombre_mes
            
            meses_con_eventos.append({
                'numero': mes,
                'nombre': nombre_mes,
                'eventos': eventos_mes,
                'cantidad': cantidad_eventos
            })
        
        return render(request, "core/calendario_anual.html", {
            "year": year,
            "meses_con_eventos": meses_con_eventos,
            "total_eventos": total_eventos,
            "mes_mas_activo": mes_mas_activo,
            "max_eventos_mes": max_eventos_mes,
            "meses_con_eventos_count": meses_con_eventos_count,
            "is_admin": request.user.is_superuser
        })

@login_required
def calendario_semanal_view(request, year=None, week=None):
    today = date.today()
    year = int(year) if year else today.year
    
    # Si week es 'current', usar la semana actual
    if week == 'current' or week is None:
        week = today.isocalendar()[1]
    else:
        week = int(week)
    
    # Calcular el primer día de la semana
    first_day_of_year = date(year, 1, 1)
    # Encontrar el primer lunes del año
    days_since_monday = first_day_of_year.weekday()
    first_monday = first_day_of_year - timedelta(days=days_since_monday)
    
    # Calcular la fecha de inicio de la semana especificada
    start_of_week = first_monday + timedelta(weeks=week - 1)
    end_of_week = start_of_week + timedelta(days=6)
    
    # Crear lista de días de la semana
    week_days = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        
        # Obtener eventos que ocurren en este día específico
        # Incluye eventos que inician, terminan o se extienden durante este día
        eventos_dia = Evento.objects.filter(
            usuario=request.user,
            fecha_inicio__date__lte=day,  # Inicia en o antes de esta fecha
            fecha_fin__date__gte=day      # Termina en o después de esta fecha
        ).order_by("fecha_inicio")
        
        week_days.append({
            'date': day,
            'eventos': eventos_dia
        })
    
    # Calcular semana anterior y siguiente
    prev_week = week - 1 if week > 1 else 52
    prev_year = year if week > 1 else year - 1
    next_week = week + 1 if week < 52 else 1
    next_year = year if week < 52 else year + 1
    
    return render(request, "core/calendario_semanal.html", {
        "year": year,
        "week": week,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "week_days": week_days,
        "prev_year": prev_year,
        "prev_week": prev_week,
        "next_year": next_year,
        "next_week": next_week,
        "is_admin": request.user.is_superuser
    })

@login_required
@user_passes_test(is_admin)
def evento_crear(request):
    if request.method == "POST":
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.usuario = request.user
            evento.save()
            messages.success(request, "Evento creado exitosamente.")
            return redirect("calendario")
    else:
        form = EventoForm()
    return render(request, "core/evento_form.html", {"form": form, "action": "Crear"})

@login_required
@user_passes_test(is_admin)
def evento_editar(request, pk):
    evento = get_object_or_404(Evento, pk=pk, usuario=request.user)
    if request.method == "POST":
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento actualizado exitosamente.")
            return redirect("calendario")
    else:
        form = EventoForm(instance=evento)
    return render(request, "core/evento_form.html", {"form": form, "action": "Editar"})

@login_required
@user_passes_test(is_admin)
def evento_eliminar(request, pk):
    evento = get_object_or_404(Evento, pk=pk, usuario=request.user)
    if request.method == "POST":
        evento.delete()
        messages.success(request, "Evento eliminado exitosamente.")
        return redirect("calendario")
    return render(request, "core/evento_confirm_delete.html", {"evento": evento})

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registro exitoso.")
            return redirect("calendario")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, "core/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            rut = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, rut=rut, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Has iniciado sesión como {rut}.")
                
                # Redirigir a la página que intentaba acceder originalmente
                next_url = request.POST.get('next') or request.GET.get('next') or request.session.get('next_url')
                if next_url and next_url != '/calendario/login/':
                    # Limpiar la sesión si existe
                    if 'next_url' in request.session:
                        del request.session['next_url']
                    return redirect(next_url)
                
                # Si no hay URL de destino, ir al calendario
                return redirect("calendario")
            else:
                messages.error(request, "RUT o contraseña inválidos.")
        else:
            messages.error(request, "RUT o contraseña inválidos.")
    else:
        form = CustomAuthenticationForm()
        
        # Si viene de una redirección por falta de autenticación
        next_url = request.GET.get('next')
        if next_url:
            request.session['next_url'] = next_url
            messages.warning(request, "Debes iniciar sesión para acceder a esa página.")
    
    # Pasar el parámetro next al template
    context = {
        "form": form,
        "next": request.GET.get('next', '')
    }
    return render(request, "core/login.html", context)

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión exitosamente.")
    return redirect("login")

