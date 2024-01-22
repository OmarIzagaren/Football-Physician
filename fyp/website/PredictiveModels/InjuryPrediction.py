import joblib
import math
import numpy as np
import pandas as pd 

loadedrf = joblib.load("./website/PredictiveModels/random_forest_3.joblib")
#Age,Height,Weight,dsli,gpm,avgMins,median_dbi,avg_loi,mode_is,avg_aoi,noi,injured,Attack,Defender,Goalkeeper,midfield,Caribbean,Central America,Eastern Africa,Eastern Asia,Eastern Europe,Middle Africa,Northern Africa,Northern America,Northern Europe,South America,Southern Africa,Southern Europe,Western Africa,Western Asia,Western Europe
injuriesDictionary ={'ankle problems': 3, 'broken kneecap': 8, 'patellar tendon rupture': 7, 'knee injury': 7, 'cruciate ligament tear': 10, 'patellar tendon dislocation': 6, 'cruciate ligament strain': 6, 'patellar tendinopathy syndrome': 5, 'knee collateral ligament tear': 8, 'ligament tear': 7, 'outer ligament tear': 6, 'knee medial ligament tear': 7, 'internal ligament strain': 5, 'cruciate ligament injury': 7, 'torn lateral knee ligament': 7, 'inner ligament tear in ankle joint': 5, 'outer ligament problems': 4, 'ankle ligament tear': 5, 'leg injury': 2, 'achilles tendon rupture': 6, 'ligament stretching': 3, 'broken ankle': 6, 'collateral ligament tear': 9, 'internal ligament tear': 7, 'ankle injury':4 , 'tendon tear': 5, 'inner ankle ligament tear': 5, 'broken leg': 8.5, 'syndesmotic ligament tear': 4, 'inflammation in the ankle joint': 4, 'torn ligaments in the tarsus': 6, 'torn ligaments': 7, 'partial damage to the cruciate ligament': 6, 'edema in the knee': 2, 'double ligament tear': 7, 'ligament injury': 5, 'inner knee ligament tear': 8, 'inflammation of ligaments in the knee': 6, 'collateral ankle ligament tear': 5, 'injury to the ankle': 4, 'patellar tendon tear': 5, 'bruise on ankle': 2, 'ankle sprain': 4, 'inner ligament stretch of the knee': 4, 'capsular tear of ankle joint': 4.5, 'inflammation of the biceps tendon in the thigh': 3, 'collateral ligament injury': 6, 'overstretching of the syndesmotic ligament': 1, 'knee collateral ligament strain': 4, 'torn knee ligaments': 7.5, ' achilles tendon contusion': 2,'achilles tendon irritation': 1, 'ankle surgery': 6, 'tendon irritation': 2, 'tendon rupture': 5, 'torn lateral ankle ligament': 5, 'cyst in the knee': 3, 'partial patellar tendon tear': 4.5, 'inflammation in the knee': 3.5, 'torn ankle ligaments': 5, 'inner ligament injury': 5, 'bruised knee': 1, 'cruciate ligament surgery': 10, 'tendonitis': 2, 'patellar tendon irritation': 1.5, 'longitudinal tendon tear': 5, 'knee surgery': 8.5, 'dislocation fracture of the ankle joint': 7, 'achilles tendon surgery': 4, 'achilles tendon problems': 2, 'knee problems': 5, 'dislocation of the kneecap': 7, 'peroneus tendon injury': 3, 'bruise on the ankle joint': 2, 'knee bruise': 1, 'syndesmosis ligament tear': 3, 'lower leg fracture': 5, 'patellar tendon problems': 3.5}

class MakePrediction:
    def __init__(self,input_array):
        self.input_array = input_array
        self.clean_input()
    
    def calculate_injury_averages(self,injury_data):
        # No injuries, return a default score (e.g., 0)
        if not injury_data:
            return 0,0,0,0,0

        # Puts the relevant injury information into corresponding arrays and variables 
        dbi_array = []
        array_injury = []
        total_loi = 0
        total_age = 0
        for injury in injury_data:
            injury_type ,days_since_last_injury, length_of_injury, age_at_injury = injury[0:]
            dbi_array.append(days_since_last_injury)       
            array_injury.append(injury_type.lower())
            total_loi += int(length_of_injury)
            total_age += int(age_at_injury)

        # Make a dictionary of the inputted injuries with the corresponding score
        player_injury_dict = {x:injuriesDictionary[x] for x in array_injury}
        
        # Calculate the median days between injuries
        if len(injury_data) == 1:
            median_dbi = dbi_array[0]
        elif len(injury_data)%2 == 0:
            median_dbi = ((sorted(dbi_array)[int(len(injury_data)/2)]) + (sorted(dbi_array)[math.ceil((len(injury_data)/2)-1)]))/2
        else:
            median_dbi = sorted(dbi_array)[math.ceil(len(injury_data)/2)-1]

        # Calculate the most common injury for the input, if multiple takes the most severe of the most common
        mode_array = (sorted(player_injury_dict.items(), key=lambda item: item[1]))
        most_commmon = mode_array[0][0]
        current = mode_array[0]
        currentLargest = 0
        currentCount = 1
        for i in range(1,len(mode_array)):
            if mode_array[i] == current:
                currentCount += 1
                continue
            current = mode_array[i]
            if currentCount >= currentLargest:
                if i == len(mode_array)-1:
                    most_commmon = mode_array[i][0]
                    continue
                most_commmon = mode_array[i-1][0]
                currentCount = currentLargest
                currentCount = 1
                continue 
            currentCount = 1
        
        
        return median_dbi, (total_loi/len(injury_data)), injuriesDictionary.get(most_commmon.lower()), (total_age/len(injury_data)), len(injury_data)

    # One hot encoding the positions so that the model can process it
    def one_hot_encode_position(self,input_position):
        positions_list=['Attack','Defender','Goalkeeper','midfield']
        position_ohe = []
        for position in positions_list:
            if input_position in position:
                position_ohe.append(True)
                continue
            position_ohe.append(False)
        return position_ohe

    # One hot encoding the regions so that the model can process it
    def one_hot_encode_region(self,input_region):
        regions_list=['Caribbean','Central America','Eastern Africa','Eastern Asia','Eastern Europe','Middle Africa','Northern Africa','Northern America','Northern Europe','South America','Southern Africa','Southern Europe','Western Africa','Western Asia','Western Europe']
        region_ohe = []
        region_found = False
        for region in regions_list:
            if input_region == region:
                region_found = True
                region_ohe.append(True)
                continue
            region_ohe.append(False)
        if not(region_found):
            region_ohe[7] = True
        return region_ohe
    
    def clean_input(self):
        clean_array =[]
        clean_array=[self.input_array[1],self.input_array[2],self.input_array[3],self.input_array[6],self.input_array[5]]
        #print(clean_array)

        median_dbi,avg_loi,mode_is,avg_aoi,noi = self.calculate_injury_averages(self.input_array[7])
        clean_array.extend([median_dbi,avg_loi,mode_is,avg_aoi,noi,self.input_array[8]])

        clean_array.extend(self.one_hot_encode_position(self.input_array[0]))

        clean_array.extend(self.one_hot_encode_region(self.input_array[4]))
        #print(clean_array)
        self.input_array = clean_array
    
    def prediction(self):
        #print(self.input_array)
        self.input_array[3] = np.log(self.input_array[3] +1)
        self.input_array[4] = np.log(self.input_array[4] +1)
        self.input_array[6] = np.log(self.input_array[6] +1)
        #self.input_array[5] = np.log(self.input_array[5] +1)
        self.input_array[7] = np.log(self.input_array[7] +1)
        self.input_array[8] = np.log(self.input_array[8] +1)
        self.input_array[9] = np.log(self.input_array[9] +1)
        self.input_array[5] = np.log(self.input_array[5] +1)

        final_array = pd.DataFrame([self.input_array])
        final_array.columns = ['Age','Height','Weight','dsli','mins','median_dbi','avg_loi','mode_is','avg_aoi','noi','injured','Attack','Defender','Goalkeeper','midfield','Caribbean','Central America','Eastern Africa','Eastern Asia','Eastern Europe','Middle Africa','Northern Africa','Northern America','Northern Europe','South America','Southern Africa','Southern Europe','Western Africa','Western Asia','Western Europe']
        #print([final_array])
        final_percentage = loadedrf.predict(final_array)

        if final_percentage <= 10:
            return "Very Low Risk"
        
        elif 10 < final_percentage <= 30:
            return "Low Risk"
        
        elif 30 < final_percentage <= 50:
            return "Moderate Risk"
        
        elif 50 < final_percentage <= 70:
            return "High Risk"
        
        elif 70 < final_percentage <= 90:
            return "Very High Risk"
        
        elif 90 < final_percentage:
            return "Extreme Risk"

array = ['Defender',25,188,78,'Western Europe',[4, 90],500,[['Cruciate ligament tear', 20, 180, 26],['Ankle injury', 1920, 72, 26], ['Inner knee ligament tear', 0, 59, 26]],0]

#input = MakePrediction(array)
#print(input.prediction())