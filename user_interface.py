import json
from dependency_parsing import *
import numpy as np
from flask import Flask
app = Flask(__name__)



def cold_start(date,rec_num,rating_weight):
    with open("trending_features_dev_series.json",'r') as main_file:
                        time_series = json.load(main_file)

    daily_counts_1 = []
    cold_model_1 = []
    daily_counts = []
    cold_model = []
    
    
    for feature in time_series:
            daily_counts_1.append(time_series[feature][date])
            cold_model_1.append(feature)
                
   

    top_trends = np.argsort(daily_counts_1)[-50:]
    for index in top_trends:
        daily_counts.append(daily_counts_1[index])
        cold_model.append(cold_model_1[index])





    normalized_daily_counts = []
    for element in daily_counts:
        normalized_daily_counts.append(float(element))


        


    with open("side_backup.json",'r') as main_file:
                        product_counts = json.load(main_file)

    product_scores = []
    product_names = []
    top_recomms = []
    top_ratings = []
    top_images = []
    product_ratings = []
    product_images = []

    for product in product_counts:
        product_score = 0
        trend_feature_count = 1

      
        for i in range(len(normalized_daily_counts)):
               if cold_model[i] in product_counts[product]:
                trend_feature_count = trend_feature_count+float(product_counts[product][cold_model[i]])
               
        for i in range(len(normalized_daily_counts)):
               if cold_model[i] in product_counts[product]:
                product_score = product_score+(normalized_daily_counts[i]*float(float(product_counts[product][cold_model[i]])/float(trend_feature_count)))
               else:
                product_score = product_score+(normalized_daily_counts[i]*float(0))
            
                
        product_scores.append(product_score)
        product_names.append(product)
        product_ratings.append(product_counts[product]['product_rating_given'])
        product_images.append(product_counts[product]['product_imurl'])
        

    for i in range(len(product_scores)):
       product_scores[i] = product_scores[i] + (product_ratings[i]*rating_weight)
        


    top_recomms_index = np.argsort(product_scores)[-rec_num:]
    for index in top_recomms_index:
        top_recomms.append(product_names[index])
        top_ratings.append(product_scores[index])
        top_images.append(product_images[index])

        
    return top_recomms,top_ratings,top_images

    



def get_seasonal_factors(date):
    
    with open("trending_features_dev_series.json",'r') as main_file:
                        time_series = json.load(main_file)

    daily_counts_1 = []
    cold_model_1 = []
    daily_counts = []
    cold_model = []
    
    
    for feature in time_series:
            daily_counts_1.append(time_series[feature][date])
            cold_model_1.append(feature)
                
   

    top_trends = np.argsort(daily_counts_1)[-20:]
    for index in top_trends:
        daily_counts.append(daily_counts_1[index])
        cold_model.append(cold_model_1[index])


    return cold_model

        
    




    
def get_recommendations(only_user_model,date,rec_num,rating_weight,user_weightage,seasonal_weightage):

    user_model_seasonal_counts = []

    with open("trending_features_dev_series.json",'r') as main_file:
                        time_series = json.load(main_file)


    seasonal_factors = get_seasonal_factors(date)
    user_model = list(only_user_model)
    user_model.extend(seasonal_factors)

   
    for feature in user_model:
        if feature in time_series:
            if feature in only_user_model:
                  user_model_seasonal_counts.append(user_weightage+time_series[feature][date])
            else:
                user_model_seasonal_counts.append(seasonal_weightage+time_series[feature][date])
  
        else:
            user_model_seasonal_counts.append(1)


    normalized_seasonal_counts = []
    for element in user_model_seasonal_counts:
        normalized_seasonal_counts.append(float(element))

   
    with open("side_backup.json",'r') as main_file:
                        product_counts = json.load(main_file)

    product_scores = []
    product_names = []
    top_recomms = []
    top_ratings = []
    product_ratings = []
    top_images = []
    product_images = []

    for product in product_counts:
        product_score = 0
        trend_feature_count = 1

        if product != 'DecoBros 8-Inch Two-Sided Swivel Wall Mount Mirror with 7x Magnification, 13.5-Inch Extension, Nickel':
            for i in range(len(normalized_seasonal_counts)):
                if user_model[i] in product_counts[product]:
                    trend_feature_count = trend_feature_count+float(product_counts[product][user_model[i]])
                

            for i in range(len(normalized_seasonal_counts)):
                if user_model[i] in product_counts[product]:
                    product_score = product_score+(normalized_seasonal_counts[i]* (float(product_counts[product][user_model[i]])/float(trend_feature_count)))
                else:
                    product_score = product_score+(normalized_seasonal_counts[i]*float(0))
                    
            product_scores.append(product_score)
            product_names.append(product)
            product_ratings.append(product_counts[product]['product_rating_given'])
            product_images.append(product_counts[product]['product_imurl'])


    for i in range(len(product_scores)):
        product_scores[i] = product_scores[i] + (product_ratings[i]*rating_weight)
        


    top_recomms_index = np.argsort(product_scores)[-rec_num:]
    for index in top_recomms_index:
        top_recomms.append(product_names[index])
        top_ratings.append(product_scores[index])
        top_images.append(product_images[index])

    
    return top_recomms,top_ratings,top_images
    
 
def remove_stop_words(features):

    stop_list = [line.rstrip('\n') for line in open('stopwords.txt')]
    new_features = []
    for feature in features:
                if feature not in stop_list:
                        if feature.isalpha():
                                new_features.append(feature)
    return new_features
                                



def build_user_model(user_review_file):
    
    with open(user_review_file,'r') as main_file:
        user_dictionary = {}
        user_features = []
        
        
        for line in main_file:
            review_text = []
            review = json.loads(line)
            review_text.append(review['reviewtext'].lower())
            category = review['category'].lower()
            productname = review['productname'].lower()
            category_list = category.split()
            productname_list = productname.split()
            category_list.append(productname_list)
            
            user_dictionary = find_features_advanced(review_text,category_list)

            for key in user_dictionary:
                 user_features.append(key) 
                
    
    return remove_stop_words(set(user_features))
        

def fetch_reccs():
    '''user_review_file = "input.json"
    print "Generating Your User Model"
    user_model = build_user_model(user_review_file)'''
    
    

    ## Defining Variables
    user_model = ['perfume','scent','cream','smell','sunscreen','fragrance', 'price', 'fan','wrinkles','colors','wrinkles']
    print "The extracted features from your reviews are:"
    print user_model

    
    rec_num = 10
    rating_weight = 2.0
    user_weightage = 1.5
    seasonal_weightage = 0.5
    print "Day 320 of the year"
    date = '160'

    
    ## Cold Start - Show the daily trends
    cold_recommendations,cold_ratings,cold_images = cold_start(date,rec_num,rating_weight)
    print "Recommendations for new users are"
    count = 0
    for i in range(rec_num-1,-1,-1):
        count = count+1
        print str(count)+". "+cold_recommendations[i] + " (Score: "+str(cold_ratings[i])+")"
        
    print "\n\n\n\n"
    ##Personal Daily Recommendations
    my_recommendations, my_ratings,my_images = get_recommendations(user_model,date,rec_num,rating_weight,user_weightage,seasonal_weightage)
    print my_images
    
    print "My Personalized Recommendations are"
    count = 0
    for i in range(rec_num-1,-1,-1):
        count = count+1
        print str(count)+". "+my_recommendations[i] + " (Score: "+str(my_ratings[i])+")"


    return cold_recommendations,cold_images,my_recommendations,my_images


def html_writer():

    c_r,c_i,m_r,m_i = fetch_reccs()
    html_file ='<html> <head> <style> #Holder{width: 100%; height: 100%; background-color:#ffffff; } #Holder1{width: 80%; height: 45%; background-color:#f8cb28; margin: auto; color: white; } #Holder2{width: 80%; height: 45%; background-color:#0a5074; margin: auto; color: red; } #Holder3{width: 100%; height: 10%; background-color:white; } #Trending{width: 80%; height: 100%; background-color:#0a5074; margin: auto; padding: 10px; overflow: scroll; color: white; } #Personal{width: 80%; height: 100%; background-color:#f8cb28; margin: auto; padding: 10px; overflow: scroll; color: red; } .image_holder{color:#ffffff; margin: 20px 20px; overflow: hidden; } .image_holder img{vertical-align: middle; } </style> </head> <body> <div id="Holder"> <div id="Holder1"> <div id="Trending"> Trending Products <div class="image_holder"> <img src='+c_i[9]+'></img>'+c_r[9]+'</div> <div class="image_holder"> <img src='+c_i[8]+'></img>'+c_r[8]+'</div> <div class="image_holder"> <img src='+c_i[7]+'></img>'+c_r[7]+'</div> <div class="image_holder"> <img src='+c_i[6]+'></img>'+c_r[6]+'</div> <div class="image_holder"> <<img src='+c_i[5]+'></img>'+c_r[5]+'</div> <div class="image_holder"> <img src='+c_i[4]+'></img>'+c_r[4]+'</div> <div class="image_holder"> <img src='+c_i[3]+'></img>'+c_r[3]+'</div> <div class="image_holder"> <img src='+c_i[2]+'></img>'+c_r[2]+'</div> <div class="image_holder"> <img src='+c_i[1]+'></img>'+c_r[1]+'</div> <div class="image_holder"> <img src='+c_i[0]+'></img>'+c_r[0]+'</div> </div> </div> <div id="Holder3"> </div> <div id="Holder2"> <div id="Personal"> Personal Recommendations <div class="image_holder"> <img src='+m_i[9]+'></img>'+m_r[9]+'</div> <div class="image_holder"> <<img src='+m_i[8]+'></img>'+m_r[8]+'</div> <div class="image_holder"> <img src='+m_i[7]+'></img>'+m_r[7]+'</div> <div class="image_holder"> <img src='+m_i[6]+'></img>'+m_r[6]+'</div> <div class="image_holder"> <img src='+m_i[5]+'></img>'+m_r[5]+'</div> <div class="image_holder"> <img src='+m_i[4]+'></img>'+m_r[4]+'</div> <div class="image_holder"> <img src='+m_i[3]+'></img>'+m_r[3]+'</div> <div class="image_holder"> <img src='+m_i[2]+'></img>'+m_r[2]+'</div> <div class="image_holder"> <img src='+m_i[1]+'></img>'+m_r[1]+'</div> <div class="image_holder"> <img src='+m_i[0]+'></img>'+m_r[0]+'</div> </div> </div> </div> </body>'
    with open("index.html",'w') as main_file:
        main_file.write(html_file)


html_writer()
