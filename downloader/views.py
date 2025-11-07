import os
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponse
from django.conf import settings
from .forms import SignUpForm, DownloadForm
from .models import UserProfile, Plan, DownloadRecord
from .tasks import download_task
from django.contrib import messages
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
def index(request):
    plans = Plan.objects.all()
    return render(request, 'downloader/index.html', {'plans': plans})
def signup(request):
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
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = DownloadForm()
    records = DownloadRecord.objects.filter(user=request.user).order_by('-created_at')[:20]
    return render(request, 'downloader/dashboard.html', {'profile': profile, 'form': form, 'records': records})
@login_required
def download_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = DownloadForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url'].strip()
            # En web limitamos a max 3 canciones por playlist
            task = download_task.delay(request.user.id, url)
            messages.success(request, "Tu descarga se está procesando en segundo plano. Revisa tu historial en el Dashboard.")
            return redirect('dashboard')
    return redirect('dashboard')
