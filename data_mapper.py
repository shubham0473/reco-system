import json
import networkx as nx
from dependency_parsing import find_features_advanced

def product_node_creator(meta_data_file_path,data_map):
    with open(meta_data_file_path) as f:
        
        
        for line in f:

            #Resetting variables
            product_id = ""
            product_salesrank = ""
            product_imurl = ""
            product_categories = ""
            product_title = ""
            product_related = ""
            product_price = ""
            

            #Data Parsing
            data = json.loads(line)
            
            product_id = data['asin']

            try:
              product_salesrank = data['salesRank']
            except Exception, e:
              product_salesrank = ""

            try: 
              product_imurl = data['imUrl']
            except Exception, e:
              product_imurl = ""

            try:
              product_categories = data['categories']
            except Exception, e:
              product_categories = ""

            try:
              product_title = data['title']
            except Exception, e:
              product_title = ""


            try:
              product_related = data['related']
            except Exception, e:
              product_related = ""

            try:
              product_price = data['price']
            except Exception, e:
              product_price = ""

            #Node creation
            data_map.add_node(product_id,node_type="product",product_salesrank=product_salesrank,product_imurl=product_imurl,product_categories=product_categories,product_title=product_title,product_related=product_related,product_price=product_price)

            
    return data_map

        


def user_node_creator(review_data_file_path,data_map):

    with open(review_data_file_path) as f2:
        
        
        for line in f2:

            #Resetting data
            reviewer_id = ""
            product_id_reviewed = ""
            reviewer_name = ""
            edge_helpful = ""
            edge_review_text = ""
            edge_overall = ""
            edge_summary = ""
            edge_review_time= ""
            edge_review_date = ""
            
  
            #Data Parsing
            data = json.loads(line)

            reviewer_id = data['reviewerID']
            product_id_reviewed = data['asin']

            try:
              reviewer_name = data['reviewerName']
            except Exception, e:
              reviewer_name = ""

            try:
              edge_helpful = data['helpful']
            except Exception, e:
              edge_helpful = ""

            try:
              edge_review_text = data['reviewText']
            except Exception, e:
              edge_review_text = ""

            try:
              edge_overall = data['overall']
            except Exception, e:
              edge_overall = ""

            try:
              edge_summary = data['summary']
            except Exception, e:
              edge_summary = ""

            try:
              edge_review_time = data['unixReviewTime']
            except Exception, e:
              edge_review_time = ""

            try:
              edge_review_date = data['reviewTime']
            except Exception, e:
              edge_review_date = ""


            data_map.add_node(reviewer_id,reviewer_name=reviewer_name,node_type="customer")
            data_map.add_edge(reviewer_id,product_id_reviewed,edge_helpful=edge_helpful,edge_review_text=edge_review_text,edge_overall=edge_overall,edge_summary=edge_summary,edge_review_time=edge_review_time,edge_review_date=edge_review_date)
              

    return data_map                
        

def json_writer(features,time_stamps,product_id,customer_id):

    with open('product_feature_data_local_06.json','r') as main_file:
                feed_data= json.load(main_file)

    if product_id not in feed_data:
        feed_data[product_id] = {}


    previous_data = feed_data[product_id]

    for feature in features:
        if feature not in previous_data:
            feed_data[product_id][feature] = {}
        if time_stamps[0] not in feed_data[product_id][feature]:
            feed_data[product_id][feature][time_stamps[0]] = 0
        feed_data[product_id][feature][time_stamps[0]] = feed_data[product_id][feature][time_stamps[0]] + 1

    with open('product_feature_data_local_06.json','w') as main_file:
        json.dump(feed_data,main_file)



    with open('customer_feature_data_local_06.json','r') as main_file:
                feed_data= json.load(main_file)

    if customer_id not in feed_data:
        feed_data[customer_id] = {}


    previous_data = feed_data[customer_id]

    for feature in features:
        if feature not in previous_data:
            feed_data[customer_id][feature] = {}
        if time_stamps[0] not in feed_data[customer_id][feature]:
            feed_data[customer_id][feature][time_stamps[0]] = 0
        feed_data[customer_id][feature][time_stamps[0]] = feed_data[customer_id][feature][time_stamps[0]] + 1
 
    with open('customer_feature_data_local_06.json','w') as main_file:
        json.dump(feed_data,main_file)
        
        
        
        





    
def get_product_reviews(data_map):

    for node in data_map.nodes(data=True):
        if (node[1]['node_type'] == 'product'):
            
            edge_list = list(data_map.edges(node[0]))
            if len(edge_list)>50:
                categories = node[1]['product_categories']
                class_words_list = categories[0]
                title = (node[1]['product_title']).split(" ")
                for item in title:
                    class_words_list.append(item.lower())

                product_unique_id = node[0]
               
                
                
                
                if(len(edge_list) != 0):
                    print "Generating Review List for "+node[1]['product_title']+"........."
                    for node_pair in edge_list:
                        print "Review-1"
                        review_list = []
                        time_stamps = []

                        
                        if data_map.node[node_pair[0]]['node_type'] == 'customer':
                            customer_unique_id = node_pair[0]
                        if data_map.node[node_pair[1]]['node_type'] == 'customer':
                            customer_unique_id = node_pair[1]
                        
                        
                        
                        review_list.append(data_map[node_pair[0]][node_pair[1]][0]['edge_review_text'])
                        time_stamps.append(data_map[node_pair[0]][node_pair[1]][0]['edge_review_time'])
                        feature_list = find_features_advanced(review_list,class_words_list)
                        if feature_list is not None:
                            if len(feature_list) > 0:
                                 json_writer(feature_list,time_stamps,product_unique_id,customer_unique_id)


if __name__ == "__main__":

    meta_data_file_path = 'meta_Beauty.json'
    review_data_file_path = 'reviews_Beauty_06(11).json'
    data_map = nx.MultiGraph()
    

    print "Creating nodes for products"
    data_map = product_node_creator(meta_data_file_path,data_map)
    print "Finished creating nodes for products"

    print "Creating nodes for users and mapping reviews to products"
    data_map = user_node_creator(review_data_file_path,data_map)
    print "Finished creating user nodes"


    get_product_reviews(data_map)



    

