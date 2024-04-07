from website.PredictiveModels import InjuryPrediction
from .models import Player, Injury
from datetime import date
import requests
import json

today = date.today()

def clean_and_predict(player_id,minutes,model):
    player_details = []
    
    #Calculate total minutes played in last month
    total_minutes = 0
    for minute in minutes: 
        total_minutes += int(minute)
        
    #Get player details
    player = Player.objects.filter(id=player_id).first()

    #Calculate player age
    date_of_birth = player.date_of_birth
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

    #Append player info to array
    player_details.extend([player.position, age, player.height, player.weight, get_region(player.country), total_minutes])

    #Get injury details and put into array
    injuries = Injury.objects.filter(player=player)

    #Check if the player has had any injuries
    if len(injuries) == 0: 
        #If player has had no injuries fill out rest of the details with default values and pass to predictive model
        player_details.extend([0,[],0])
        prediction_input = InjuryPrediction.MakePrediction(player_details,model)
        return prediction_input.prediction()
    
    else:
        injury_array = []
        injured = 0
        #Go through each injury and get the details
        for injury in injuries: 
            if injury.injury_end_date == None: 
                end_date = today
            else: 
                end_date = injury.injury_end_date

            injury_details = [injury.injury, injury.injury_start_date, end_date, injury.injury_age]
            injury_array.append(injury_details)

            #Check if this injury is a current injury, if it is then set injured to true
            if injury.injured:
                injured = 1
          
        #Sorting the injury array based on date, going from closest end date to farthest 
        injury_array = sorted(injury_array, key=lambda x: x[2], reverse=True)

        #Calculate days since last injured
        days_since_injured = (today - injury_array[0][2]).days
        player_details.append(days_since_injured)

        #Calculate length of injuries
        for injury in injury_array:
            injury_length = (injury[2] - injury[1]).days
            injury.append(injury_length)

        #Calculate days between injuries
        for i in range(len(injury_array)):
            if i == (len(injury_array)-1):
                days_between_injuries = 0
                injury_array[i].append(days_between_injuries)
                continue
            days_between_injuries = (injury_array[i][1] - injury_array[i+1][2]).days
            injury_array[i].append(days_between_injuries)
            
        #Replace dates with the days between injuries and length of injuries as this is what the model needs
        for injury in injury_array:
            injury[1] = injury[5]
            injury[2] = injury[4]
            injury.pop()
            injury.pop()
        
        player_details.extend([injury_array,injured])
        prediction_input = InjuryPrediction.MakePrediction(player_details,model)
        return prediction_input.prediction()

#This function takes the country and returns the countries region i.e. Western Europe, Northern African, etc.
def get_region(country):
        url = f"https://api.api-ninjas.com/v1/country?name={country}"
        response = requests.get(url, headers={'X-Api-Key': 'eco5fNw060OIGUTVv5Y8LA==WWjLCtwBHJYZt9Aw'})
        if response.status_code == requests.codes.ok:
            dictonary = json.loads(response.text)
            dictonary = dictonary[0]
            region = dictonary["region"]
            return region
        else:
            print("Error:", response.status_code, response.text)
