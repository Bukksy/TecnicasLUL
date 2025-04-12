from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  
            return redirect('inicio')  
        else:
            messages.error(request, "Usuario o contraseña incorrectos") 

        return redirect('login')

    return render(request, 'login.html')

@login_required
def inicio(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'inicio.html')

def logout_view(request):
    logout(request)
    return redirect('login')
