import os
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponse
from django.conf import settings # Necesario para usar settings
from .forms import SignUpForm, DownloadForm
from .models import UserProfile, Plan, DownloadRecord
# from .tasks import download_task  # Asumo que tienes un archivo tasks.py para Celery
from django.contrib import messages
import stripe
# Inicializa Stripe con la clave secreta de las settings
stripe.api_key = settings.STRIPE_SECRET_KEY


# Define una función dummy para download_task si no tienes Celery configurado
# Si tienes Celery funcionando, elimina esto:
def download_task(user_id, url):
    """Dummy task para simular el encolado de Celery."""
    print(f"Tarea simulada encolada para Usuario {user_id}: {url}")


def index(request):
    """
    Página de inicio. Muestra el formulario de descarga si el usuario está autenticado.
    """
    plans = Plan.objects.all()
    # 🌟 CORRECCIÓN DEL ERROR 500: Se obtiene la variable de settings y se pasa al contexto.
    prepackaged_exe_url = getattr(settings, 'PREPACKAGED_EXE_URL', '#')
    
    context = {'plans': plans, 'prepackaged_exe_url': prepackaged_exe_url}
    
    # Si el usuario está autenticado, inicializa y añade el formulario de descarga al contexto.
    if request.user.is_authenticated:
        context['download_form'] = DownloadForm()
        
    return render(request, 'downloader/index.html', context)


def signup(request):
    """
    Vista de registro de usuario.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'downloader/signup.html', {'form': form})


@login_required
def dashboard(request):
    """
    Muestra el dashboard del usuario con su perfil, cuota y últimas descargas.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    # Se inicializa el formulario aquí también para el dashboard
    form = DownloadForm()
    # Limita el historial a 20 registros
    records = DownloadRecord.objects.filter(user=request.user).order_by('-created_at')[:20]
    return render(request, 'downloader/dashboard.html', {'profile': profile, 'form': form, 'records': records})


@login_required
def download_view(request):
    """
    Procesa la solicitud de descarga y encola la tarea Celery.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = DownloadForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url'].strip()
            
            # Encola la tarea Celery para la descarga en segundo plano
            download_task(request.user.id, url) # Usando la función dummy o la real de Celery
            
            messages.success(request, "Tu descarga se está procesando en segundo plano. Revisa tu historial en el Dashboard.")
            return redirect('dashboard')
            
    # Si no es POST o el formulario es inválido, redirige al dashboard
    return redirect('dashboard')
