import json
from datetime import datetime
from data_appender import *
from nltk.stem import WordNetLemmatizer
import matplotlib.pyplot as plt
from new_farima import *



def preprocessing():
        
        features = {}
        features_mod = {}
        feature_list = []

        for files in range(1,6,1):
                print files
                features,features_mod = time_serie_formation(str(files)+".json",features,features_mod)


        for feature in features:
                feature_list.append(feature)

                
                
        print "Removing Stop Words"
        filtered_list = []
        filtered_list = remove_stop_words(feature_list)

        raw_feature_counts = data_appendage(filtered_list)

        with open('raw_count_temp.json','w') as main_file:
                json.dump(raw_feature_counts,main_file)

        return raw_feature_counts
        


def yearly_data():
        with open('Final Datas/main_raw_count.json','r') as main_file:
                feature_counts = json.load(main_file)              
        features = {}
        print "Lemmatizing and Normalizing"
        features = lemma_raw_time_serie_formation(feature_counts,features)
        only_features = []
        for feature in features:
                only_features.append(feature)

        return features,only_features



def remove_stop_words(features):

        stop_list = [line.rstrip('\r\n') for line in open('stopwords.txt')]
        count = 0
        new_features = []
        for feature in features:
                count = count+1
                if feature not in stop_list:
                        if feature.isalpha():
                                new_features.append(feature)

        return new_features

        


        
def time_serie_formation(filename,features,features_mod):
        with open(filename,'r') as main_file:
                        feed_data= json.load(main_file)

        for items in feed_data:

                item_feature_data = feed_data[items]
                
                for feature in item_feature_data:
                    if feature.lower() not in features:
                        features[feature.lower()] = {}
                        features_mod[feature.lower()] = {}
         
                    timestamps = feed_data[items][feature]

                    for timestamp in timestamps:
                        
                        if datetime.fromtimestamp(float(timestamp)).timetuple().tm_yday not in features[feature.lower()]:
                            features[feature.lower()][datetime.fromtimestamp(float(timestamp)).timetuple().tm_yday] = feed_data[items][feature][timestamp]
                        else:
                            features[feature.lower()][datetime.fromtimestamp(float(timestamp)).timetuple().tm_yday] = int(features[feature.lower()][datetime.fromtimestamp(float(timestamp)).timetuple().tm_yday])+int(feed_data[items][feature][timestamp])


                        if timestamp not in features_mod[feature.lower()]:
                            features_mod[feature.lower()][timestamp] = feed_data[items][feature][timestamp]
                        else:
                            features_mod[feature.lower()][timestamp] = int(features_mod[feature.lower()][timestamp])+int(feed_data[items][feature][timestamp])
                        


               


        return features,features_mod



def lemma_raw_time_serie_formation(feature_counts,day_wise_feature_counts):
        
        wnl = WordNetLemmatizer()
        for feature in feature_counts:
            feature_lemma = wnl.lemmatize(feature, 'n')
            if feature_lemma not in day_wise_feature_counts:
                day_wise_feature_counts[feature_lemma] = {}
 
            timestamps = feature_counts[feature]

            for timestamp in timestamps:
                
                if datetime.fromtimestamp(float(timestamp)).timetuple().tm_yday not in day_wise_feature_counts[feature_lemma]:
                    day_wise_feature_counts[feature_lemma][datetime.fromtimestamp(float(timestamp)).timetuple().tm_yday] = feature_counts[feature][timestamp]
                else:
                    day_wise_feature_counts[feature_lemma][datetime.fromtimestamp(float(timestamp)).timetuple().tm_yday] = int(day_wise_feature_counts[feature_lemma][datetime.fromtimestamp(float(timestamp)).timetuple().tm_yday])+int(feature_counts[feature][timestamp])
        return time_series_normalizer(day_wise_feature_counts)



def time_series_normalizer(counts):

        for feature in counts:
                for i in range(1,367,1):
                        if i not in counts[feature]:
                                counts[feature][i] = 0

        return counts
                                
        

def plotter(features,feature):
        days = [i for i in range(1,367,1)]
        counts = []
        for i in range(1,367,1):
         counts.append(features[feature][i])
        plt.plot(days,counts)
        plt.show()
        
        


def product_feature_counts():

        feature_list = [line.rstrip('\n') for line in open('features_extracted.txt')]
        product_feature_count_data = feature_counter(feature_list)

        with open('product_model.json','w') as main_file:
                json.dump(product_feature_count_data,main_file)

                
        return product_feature_count_data
        


def trending_topics(features):

        averages = []
        average_features = []

        for key in features:
                if key != 'product' and key != 'products':
                        temp = 0
                        for i in range(1,367):
                                temp = temp + features[key][i]

                        average = temp/366.0

                        if average > 20:
                                averages.append(average)
                                average_features.append(key)

        return average_features,averages
        
def average_series():
        with open('trending_features_series.json','r') as main_file:
                time_series = json.load(main_file)
        new_series = {}
        for key in time_series:
                sum_1 = 0
                for i in range(1,367):
                        sum_1 = sum_1 + time_series[key][str(i)]

                average = float(sum_1)/366.0
                new_series[key] = {}
                for i in range(1,367):
                        value = time_series[key][str(i)]
                        
                        new_series[key][i] = float(value-average)/float(average)
        

        with open('trending_features_dev_series.json','w') as main_file:
                 json.dump(new_series,main_file)    
        
#preprocessing()
#features,only_features = yearly_data()
#fine_features,fine_values = trending_topics(features)
average_series()
#product_model = product_feature_counts()




        

