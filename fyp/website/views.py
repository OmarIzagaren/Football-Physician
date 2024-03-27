from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse, FileResponse
from django.urls import reverse
from django.core.files.uploadedfile import TemporaryUploadedFile

from datetime import date
import os
import tempfile
import base64
from .predictions import clean_and_predict
from .generatePDF import generate_pdf
from .forms import SignUpForm, PlayerForm, InjuryForm
from .models import Player, Injury
from roboflow import Roboflow


def home(request): 
    return render(request, 'home.html', {})

def login_user(request): 
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            messages.success(request, "Successfully logged in.")
            return redirect('home')
        else:
            messages.success(request, "Invalid user.")
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def logout_user(request): 
    logout(request)
    messages.success(request, "Successfully logged out.")
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
            messages.success(request, "Successfully registered.")
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
                messages.success(request, "Player successfully registered.")
                return redirect('home')
        errors_list = []
        if form.errors:
            for field in form:
                if field.errors: 
                    errors_list.append(field.errors)
        form.errors.clear()
        return render(request, 'player.html', {'form':form, 'errors_list':errors_list})
    else: 
        messages.success(request, "You have to log in to access this page.")
        return redirect('home')


def injury_details(request):
    title = 'Add Injury'
    if request.user.is_authenticated:
        try:
            form = InjuryForm(user=request.user)
            if request.method == 'POST':
                form = InjuryForm(request.POST, user=request.user)
                
                if form.is_valid():
                    form.save()
                    messages.success(request, "Injury successfully added.")
                    return redirect('home')
                
                errors_list = []
                if form.errors:
                    for field in form:
                        if field.errors: 
                            errors_list.append(field.errors)
                form.errors.clear()
                return render(request, 'add_injury.html', {'form':form, 'errors_list':errors_list, 'title': title})
        except ValidationError as e:
            error_message = str(e)
            error_message = error_message.replace("'",'')
            error_message = error_message.replace("[",'')
            error_message = error_message.replace("]",'')
            messages.error(request, error_message)
            return redirect('player')
    else: 
        messages.error(request, "You have to log in to access this page.")
        return redirect('home')

    return render(request, 'add_injury.html', {'form': form, 'title': title})

def player_view(request):
    if request.user.is_authenticated:
        players = Player.objects.filter(user=request.user)
        if players.count() == 0: 
            messages.error(request,'A player has to be created before you can access this page.')
            return redirect('player')
        return render(request, 'view_player.html', {'players': players})
    else: 
        messages.error(request, "Not logged in.")
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
        f'<th scope="col">Action</th>'
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

        edit_url = reverse('edit_injury', args=[injury.id])
        injuries_html += (
            f'<tr class="{row_class}">'
            f'<td>{injury.injury}</td>'
            f'<td>{injury.injury_start_date}</td>'
            f'<td>{end_date}</td>'
            f'<td>{injury.injury_age}</td>'
            f'<td><a href="{edit_url}" class="btn btn-outline-secondary btn-sm">Edit Injury</a></td>'
            f'</tr>'
        )
    
    if bool(injuries) == False:
        return HttpResponse("This player has no injuries.")

    return HttpResponse(injuries_html)

def edit_injury(request,injury_id):
    injury = Injury.objects.get(id=injury_id) 
    title = 'Edit Injury'
    if request.method == 'POST':
        form = InjuryForm(request.POST, instance=injury, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request,'Injury successfully edited.')
            return redirect('view_player')
        errors_list = []
        if form.errors:
            for field in form:
                if field.errors: 
                    errors_list.append(field.errors)
        form.errors.clear()
        return render(request, 'add_injury.html', {'form':form, 'errors_list':errors_list, 'title': title, 'injury_id': injury_id})
    else:
        form = InjuryForm(instance=injury, user=request.user)

    return render(request, 'add_injury.html', {'form': form, 'title': title, 'injury_id': injury_id})

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

def delete_player(request):
    player_id = request.POST.get('player_id')
    player_count = Player.objects.filter(user=request.user).count()
    delete_player = Player.objects.filter(id=player_id).first()
    delete_player.delete()
    if player_count == 1:
        redirect_url = reverse('home')
    else:
        redirect_url = reverse('view_player')
    messages.success(request, "Player successfully deleted.")
    return HttpResponse(redirect_url)

def delete_injury(request,id):
    delete_injury = Injury.objects.filter(id=id).first()
    delete_injury.delete()
    redirect_url = reverse('view_player')
    messages.success(request, "Injury successfully deleted.")
    return HttpResponse(redirect_url)

def predict_injury(request):
    very_low_risk_paragraphs = ["None specifically, but avoid overtraining and ensure proper form.", "Focus on maintaining flexibility, strength, and endurance. Include exercises like squats, lunges, hamstring curls, calf raises, and plyometrics for lower body strength. Incorporate agility drills and balance exercises to improve proprioception.", "Continue regular strength and conditioning programs. Ensure proper warm-up and cool-down routines. Focus on technique during all exercises."]
    low_risk_paragraphs = ["High-impact exercises without proper progression or supervision.", "Emphasize core strength, leg strength, and balance. Exercises may include planks, side planks, bridging, and stability ball exercises for core stability. Include exercises like squats, lunges, hamstring curls, calf raises, and plyometrics for lower body strength. ", "Monitor training load to avoid sudden increases in intensity or volume. Pay attention to recovery and include active recovery sessions."]
    moderate_risk_paragraphs = ["Plyometrics and high-impact exercises until strength and balance are adequately developed.", "Incorporate targeted strengthening and flexibility exercises focusing on the muscles around the knee and the leg. Include eccentric strengthening exercises for hamstrings and quadriceps, and proprioceptive exercises such as single-leg balances and wobble board exercises.", "Begin a supervised rehabilitation program if there are signs of muscle imbalance or weakness. Regularly consult with a physiotherapist for personalized advice."]
    high_risk_paragraphs = ["Any activity that involves twisting, jumping, or rapid changes of direction until cleared by a medical professional.", "Focus on low-impact conditioning exercises, such as cycling or swimming, and specific rehabilitative exercises prescribed by a physiotherapist. Emphasize exercises that improve joint stability, like isometric exercises for quadriceps and hamstrings.", "Strictly adhere to a rehabilitation program if recovering from a previous injury. Regular assessments by a healthcare professional to monitor progress."]
    very_high_risk_paragraphs = ["All competitive play, high-impact, and high-intensity training activities.", "Engage in controlled, low-impact exercises under the guidance of a healthcare professional. Rehabilitation exercises focusing on gentle strengthening, flexibility, and stability should be prioritized.", "Engage in exercises that specifically aim to correct imbalances or strengthen areas of weakness. This might involve targeted strength training, flexibility routines, and proprioceptive exercises to enhance joint stability and neuromuscular control."]
    extreme_risk_paragraphs = ["Any form of physical activity that has not been explicitly approved by a healthcare provider.", "Only perform exercises approved by medical and rehabilitation professionals, likely focusing on very gentle, non-weight bearing activities initially, such as pool therapy.", "Prioritize injury rehabilitation and consult regularly with a multidisciplinary team including doctors, physiotherapists, and possibly a sports psychologist to support mental well-being during recovery."]
    if request.user.is_authenticated:
        players = Player.objects.filter(user=request.user)
        if players.count() == 0: 
            messages.error(request,'A player has to be created before you can access this page.')
            return redirect('player')
        if request.method == 'POST':
            form = request.POST
            player_id = form.get('player')
            games = form.getlist('games[]')
            model = form.get('model')
            injury_risk_prediction = clean_and_predict(player_id, games, model)
            #print(injury_risk_prediction)
            if injury_risk_prediction == "Very Low Risk":
                paragraphs = very_low_risk_paragraphs

            elif injury_risk_prediction == "Low Risk":
                paragraphs = low_risk_paragraphs

            elif injury_risk_prediction == "Moderate Risk":
                paragraphs = moderate_risk_paragraphs

            elif injury_risk_prediction == "High Risk":
                paragraphs = high_risk_paragraphs

            elif injury_risk_prediction == "Very High Risk":
                paragraphs = very_high_risk_paragraphs

            elif injury_risk_prediction == "Extreme Risk":
                paragraphs = extreme_risk_paragraphs
            
            if form.get('generate_pdf') == 'yes':
                pdf_file,namefile = generate_pdf(player_id,injury_risk_prediction,paragraphs)
                return FileResponse(pdf_file,as_attachment=True,filename=namefile)

            return render(request, 'injury_prediction.html', {'model':model, 'player_id':player_id, 'players': players, 'form':form, 'games':games,'injury_risk_prediction': injury_risk_prediction, 'paragraphs': paragraphs})
    else: 
        messages.error(request, "You have to log in to access this page.")
        return redirect('home')
    return render(request, 'injury_prediction.html', {'players': players})


def detect_acl(request):
    healthy_paragraphs = ["Not applicable.", "Not applicable.", "Emphasize exercises that support ACL health, such as hamstring and quadriceps strengthening, plyometrics for dynamic stability, and balance exercises to improve proprioception. Core strengthening is also crucial for maintaining proper alignment and reducing the risk of ACL strain. Training proper landing and pivoting techniques can also prevent undue stress on the ACL."]
    partial_paragraphs = ["Recovery times can vary significantly based on the severity of the sprain (Grade 1 or Grade 2), ranging from 2 weeks to 3 months. Grade 1 sprains might require a shorter recovery period, while Grade 2 sprains, indicating more significant damage, necessitate a longer recovery with careful rehabilitation.", "Initial treatment involves rest, ice, compression, and elevation (RICE) to manage swelling and pain. As the acute phase resolves, rehabilitation focuses on restoring full range of motion, followed by gradual strengthening exercises tailored to support the ACL and prevent future injuries. Balance and proprioceptive exercises are crucial for restoring knee stability.", "After recovery, it's important to continue with exercises that enhance knee stability and strength, focusing on the hamstrings, quadriceps, and core muscles. Incorporate agility training and practice proper techniques in sports-specific movements to protect the ACL."]
    ruptured_paragraphs = ["A complete ACL tear often requires surgical reconstruction for individuals looking to return to high levels of physical activity. Recovery and return to sport can typically take 6 to 12 months, depending on factors such as the success of the surgery, the individual’s commitment to rehabilitation, and the body’s healing response.", "Post-surgery, the focus is on reducing swelling, regaining knee range of motion, and progressively strengthening the muscles around the knee and the core. This process involves several phases, from non-weight bearing exercises to advanced strengthening and eventually, sport-specific drills. Physical therapy plays a critical role in guiding this progression safely and effectively.", "Long-term prevention strategies include maintaining a strong and flexible musculature around the knee, focusing on balance and proprioceptive exercises to improve neuromuscular control, and continuing to practice proper movement techniques. Gradual reintegration into sports with a focus on technique and possibly using a knee brace as advised by healthcare professionals can also help prevent re-injury."]
    if request.user.is_authenticated: 
        if request.method == 'POST' and request.FILES['image']:
            image_file = request.FILES['image']
            temp_file = tempfile.NamedTemporaryFile(delete=False)

            try:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)

                temp_file_path = temp_file.name 
                temp_file.seek(0) 

                rf = Roboflow(api_key="UNYXpfLbL0acg3VBqsJ4")
                project = rf.workspace().project("acl-injury-severity-classifier")
                model = project.version(1).model
                mri_prediction = model.predict(temp_file_path, confidence=50, overlap=30).json()

                try:
                    injury_class = mri_prediction['predictions'][0]['class']
                    if injury_class == "healthy":
                        injury_class = "Healthy ACL"
                        paragraphs = healthy_paragraphs

                    elif injury_class == "partially_injured":
                        injury_class = "Partially Injured ACL"
                        paragraphs = partial_paragraphs

                    else:
                        injury_class = "Completely Ruptured ACL"
                        paragraphs = ruptured_paragraphs
                except: 
                    injury_class = "Invalid image"
                    paragraphs = ["","",""]


                temp_file.seek(0) 
                base64_img = base64.b64encode(temp_file.read()).decode('utf-8')
                image_url = f'data:image/jpeg;base64,{base64_img}'

            finally:
                temp_file.close() 
                os.unlink(temp_file_path)
            
            return render(request, 'injury_scan_acl.html', {'image':image_url,'img_name':image_file, 'injury':injury_class, 'paragraphs':paragraphs})
    else: 
        messages.error(request, "You have to log in to access this page.")
        return redirect('home')

    return render(request, 'injury_scan_acl.html', {})
