# avelarcobranca/views.py
from django.shortcuts import redirect

def root_view(request):
    if request.user.is_authenticated:
        return redirect('colaboradores:home')  # Redireciona para a home se estiver logado
    else:
        return redirect('colaboradores:login')  # Redireciona para o login se não estiver logado
