from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from .forms import SignUpForm, PlayerForm
from django.contrib.auth.models import User


def home(request): 
    return render(request, 'home.html', {})


def login_user(request): 
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            messages.success(request, "Logged in")
            return redirect('home')
        else:
            messages.success(request, "Invalid user")
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def logout_user(request): 
    logout(request)
    messages.success(request, "Logged out")
    return redirect('home')

def register_user(request): 
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            login(request,user)
            messages.success(request, "Successfully registered")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form':form})
    if form.errors:
        errors_list = []
        for field in form:
            if field.errors: 
                errors_list.append(field.errors)
        form.errors.clear()
    return render(request, 'register.html', {'form':form, 'errors_list':errors_list})

def player_details(request):
    if request.user.is_authenticated:
        form = PlayerForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                add_player = form.save(commit=False)
                add_player.user = request.user
                add_player.save()
                messages.success(request, "Successfully registered")
                return redirect('home')
        errors_list = []
        if form.errors:
            for field in form:
                if field.errors: 
                    errors_list.append(field.errors)
        #form.errors.clear()
        return render(request, 'player.html', {'form':form, 'errors_list':errors_list})
    else: 
        messages.success(request, "NOt logged in")
        return redirect('home')