from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from .forms import SignUpForm, PlayerForm, InjuryForm
from django.core.exceptions import ValidationError
from .models import Player, Injury
from django.http import HttpResponse
from datetime import date
from .predictions import clean_and_predict
import requests
from roboflow import Roboflow




def home(request): 
    print("test")
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
                add_player.user_id = request.user.id
                add_player.save()
                messages.success(request, "Successfully registered")
                return redirect('home')
        errors_list = []
        if form.errors:
            for field in form:
                if field.errors: 
                    errors_list.append(field.errors)
        form.errors.clear()
        return render(request, 'player.html', {'form':form, 'errors_list':errors_list})
    else: 
        messages.success(request, "Not logged in")
        return redirect('home')


def injury_details(request):
    if request.user.is_authenticated:
        try:
            form = InjuryForm(user=request.user)
            if request.method == 'POST':
                form = InjuryForm(request.user, request.POST)
                
                if form.is_valid():
                    form.save()
                    messages.success(request, "Successfully Added")
                    return redirect('home')
                
                errors_list = []
                if form.errors:
                    for field in form:
                        if field.errors: 
                            errors_list.append(field.errors)
                form.errors.clear()
                return render(request, 'add_injury.html', {'form':form, 'errors_list':errors_list})
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('player')
    else: 
        messages.error(request, "Not logged in")
        return redirect('home')


    return render(request, 'add_injury.html', {'form': form})

def player_view(request):
    if request.user.is_authenticated:
        players = Player.objects.filter(user=request.user)
        return render(request, 'view_player.html', {'players': players})
    else: 
        messages.error(request, "Not logged in")
        return redirect('home')

def get_player_injuries(request):
    selected_player = request.GET.get('selected_player', None)
    
    injuries = Injury.objects.filter(player=selected_player).order_by('-injury_start_date')
    injuries_html = (
        f'<thead>'
        f'<tr>'
        f'<th scope="col">Injury</th>'
        f'<th scope="col">Date Injured</th>'
        f'<th scope="col">Date Recovered</th>'
        f'<th scope="col">Age of Injury</th>'
        f'</tr>'
        f'</thead>'
    )
    
    for injury in injuries:
        end_date = injury.injury_end_date
        if end_date is None:
            end_date = date.today()
            row_class = 'table-danger' 
        else: 
            row_class = ""

        injuries_html += (
            f'<tr class="{row_class}">'
            f'<td>{injury.injury}</td>'
            f'<td>{injury.injury_start_date}</td>'
            f'<td>{end_date}</td>'
            f'<td>{injury.injury_age}</td>'
            f'</tr>'
        )
    
    if bool(injuries) == False:
        return HttpResponse("This player has no injuries.")

    return HttpResponse(injuries_html)

def get_player_details(request):
    selected_player = request.GET.get('selected_player', None)
    player_details = Player.objects.filter(id=selected_player).first()
    details_html = ''
    details_html += (
        f'<tr>'
        f'<th>Full Name:</th>'
        f'<td>{player_details.first_name} {player_details.last_name}</td>'
        f'</tr>'
        f'<tr>'
        f'<th>Position:</th>'
        f'<td>{player_details.position}</td>'
        f'</tr>'
        f'<tr>'
        f'<th>Date of Birth:</th>'
        f'<td>{player_details.date_of_birth}</td>'
        f'</tr>'
        f'<tr>'
        f'<th>Height(cm):</th>'
        f'<td>{player_details.height}</td>'
        f'</tr>'
        f'<tr>'
        f'<th>Weight(kg):</th>'
        f'<td>{player_details.weight}</td>'
        f'</tr>'
        f'<tr>'
        f'<th>Country:</th>'
        f'<td>{player_details.country}</td>'
        f'</tr>'
        f'</br>'
    )
    return HttpResponse(details_html)

def predict_injury(request):
    if request.user.is_authenticated:
        players = Player.objects.filter(user=request.user)
        if request.method == 'POST':
            form = request.POST
            player_id = form.get('player')
            games = form.getlist('games[]')
            model = form.get('model')
            injury_risk_prediction = clean_and_predict(player_id, games, model)
            #print(injury_risk_prediction)
            return render(request, 'injury_prediction.html', {'model':model, 'player_id':player_id, 'players': players, 'form':form, 'games':games,'injury_risk_prediction': injury_risk_prediction})
    else: 
        messages.error(request, "Not logged in")
        return redirect('home')
    return render(request, 'injury_prediction.html', {'players': players})

from django.core.files.uploadedfile import TemporaryUploadedFile
import os
import tempfile
import base64

def detect_acl(request):
    if request.user.is_authenticated: 
        if request.method == 'POST' and request.FILES['image']:
            image_file = request.FILES['image']
            temp_file = tempfile.NamedTemporaryFile(delete=False)

            try:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)

                temp_file_path = temp_file.name  # Get the temporary file path
                temp_file.seek(0)  # Ensure that the file cursor is at the beginning of the file

                rf = Roboflow(api_key="UNYXpfLbL0acg3VBqsJ4")
                project = rf.workspace().project("classification-of-acl-injuriesv-v9dlc")
                model = project.version(6).model
                mri_prediction = model.predict(temp_file_path, confidence=50, overlap=30).json()
                try:
                    injury_class = mri_prediction['predictions'][0]['class']
                    if injury_class == "healthy":
                        injury_class = "Healthy ACL"
                    elif injury_class == "partially_injured":
                        injury_class = "Partially Injured ACL"
                    else:
                        injury_class = "Completely Ruptured ACL"
                except: 
                    injury_class = "Invalid image"


                temp_file.seek(0)  # Ensure the file cursor is at the beginning
                base64_img = base64.b64encode(temp_file.read()).decode('utf-8')
                image_url = f'data:image/jpeg;base64,{base64_img}'

            finally:
                temp_file.close()  # Close the temporary file
                os.unlink(temp_file_path)  # Delete the temporary file
            
            return render(request, 'injury_scan_acl.html', {'image':image_url,'img_name':image_file, 'injury':injury_class})
    else: 
        messages.error(request, "Not logged in")
        return redirect('home')

    return render(request, 'injury_scan_acl.html', {})
