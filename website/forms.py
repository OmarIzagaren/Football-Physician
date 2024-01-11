from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Player, Injury
from django import forms
from .information import positions,countries,injuries
from datetime import date, timedelta

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
    first_name = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'	

    def clean_email(self):
        email = self.cleaned_data.get("email")
        email_count = User.objects.filter(email=email).count()
        if email_count > 0:
            raise forms.ValidationError("A user with that email already exists.")
        return email


position_array = [
    ("", "Select Position"),
    ("Goalkeeper", "Goalkeeper"),
    ("Defender", "Defender"),
    ("Midfielder", "Midfielder"),
    ("Attacker", "Attacker"),
]
class PlayerForm(forms.ModelForm):
    first_name = forms.CharField(required=True, label="", max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(required=True,label="", max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))
    position = forms.CharField(required=True,label="", widget=forms.Select(choices=positions,attrs={'class':'form-control', 'placeholder':'Position'}))
    date_of_birth = forms.DateField(required=True,label="", widget=forms.DateInput(attrs={'class':'form-control','type':'date', 'placeholder':'Date of Birth'}))
    height = forms.CharField(required=True,label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Height'}))
    weight = forms.CharField(required=True,label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Weight'}))
    country = forms.CharField(required=True,label="", widget=forms.Select(choices=countries,attrs={'class':'form-control', 'placeholder':'Country'}))

    class Meta: 
        model = Player
        exclude = ("user", )
    
    def __init__(self, *args, **kwargs):
        super(PlayerForm, self).__init__(*args, **kwargs)
        # Set the max attribute for date_of_birth field
        self.fields['date_of_birth'].widget.attrs['max'] = str(date.today() - timedelta(days=365.25 * 16))
        self.fields['date_of_birth'].help_text = '<span class="form-text text-muted"><small>A player must be aged 16 or over.</small></span>'

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get("date_of_birth")
        if date.today() < date_of_birth:
            raise forms.ValidationError("Date of Birth can not be in the future.")
        return date_of_birth


class InjuryForm(forms.ModelForm):
    player = forms.ModelChoiceField(queryset=Player.objects.none(),required=True,label="",widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Player'}))
    injury = forms.CharField(required=True,label="", max_length=50, widget=forms.Select(choices=injuries,attrs={'class':'form-control', 'placeholder':'Injury'}))
    injury_start_date = forms.DateField(required=True,label="", widget=forms.DateInput(attrs={'class':'form-control','type':'date', 'placeholder':'Injury Start Date'}))
    injury_end_date = forms.DateField(required=False,label="", widget=forms.DateInput(attrs={'class':'form-control','type':'date' ,'placeholder':'Injury End Date'}))
    injury_age = 0
    injured = forms.BooleanField(required=False)

    class Meta: 
        model = Injury
        fields = ('player','injury','injury_start_date','injury_end_date','injury_age','injured')
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        players = Player.objects.filter(user=user)
        self.fields['injury_start_date'].widget.attrs['max'] = str(date.today())
        self.fields['injury_end_date'].widget.attrs['max'] = str(date.today())

        if players.count() == 0:
            raise forms.ValidationError("No player information exists for this account, you must create a player.")
        elif players.count() == 1:
            self.fields['player'].queryset = players 
            self.fields['player'].initial = players.first()
            self.one_player = False
            print("Hello")
        else:
            self.fields['player'].queryset = players
            self.one_player = True
    
    def clean(self):
        cleaned_data = super().clean()
        injured = cleaned_data.get("injured")
        print(injured)
        if injured:
            cleaned_data['injury_end_date'] = None
        else: 
            if not cleaned_data['injury_end_date']: 
                self.add_error('injury_end_date', "The injury end date field is required.")

        injury_start_date = cleaned_data.get("injury_start_date")
        injury_end_date = cleaned_data.get("injury_end_date")

        try:
            if injury_start_date > injury_end_date:
                self.add_error('injury_end_date', "The injury start date cannot be after the injury end date.")
        except:
            pass

        player = cleaned_data.get("player")

        if player and injury_start_date:
            injury_age = injury_start_date.year - player.date_of_birth.year - ((injury_start_date.month, injury_start_date.day) < (player.date_of_birth.month, player.date_of_birth.day))
            print(injury_age)
            self.fields['injury_age'] = injury_age
            cleaned_data['injury_age'] = injury_age

        print(cleaned_data)
        return cleaned_data

