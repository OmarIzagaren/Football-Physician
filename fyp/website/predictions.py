from website.PredictiveModels import InjuryPrediction
from .models import Player, Injury
from datetime import date

today = date.today()

def clean_and_predict(player_id,minutes):
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
    player_details.extend([player.position, age, player.height, player.weight, player.country, total_minutes])

    #Get injury details and put into array
    injuries = Injury.objects.filter(player=player)

    #Check if the player has had any injuries
    if len(injuries) == 0: 
        #If player has had no injuries fill out rest of the details with default values and pass to predictive model
        player_details.extend([0,[],0])
        prediction_input = InjuryPrediction.MakePrediction(player_details)
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
          
        #Sorting the injury array based on date, going from closest start date to farthest 
        injury_array = sorted(injury_array, key=lambda x: x[1], reverse=True)
        print(injury_array)

        #Put injuries into start date order, from closest date to furthest 

        #Calculate days since last injured

        #Calculate days between injuries
    
        #Calculate length of injuries

    

