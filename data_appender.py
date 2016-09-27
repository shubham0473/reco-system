import networkx as nx
import json

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
        

def get_counts(data_map,features,feature_counts):
    print len(data_map.edges())
    count = 0
    for edge in data_map.edges(data=True):
        count = count+1
        print count
        review_text = str(edge[2]['edge_review_text']).lower()

        review_text = review_text.replace("."," ")
        review_text = review_text.replace(","," ")
        review_text = review_text.replace("!"," ")
        review_text = review_text.replace("?"," ")

        split_sentence = review_text.split()
        
        timestamp = str(edge[2]['edge_review_time'])

        common = set(split_sentence).intersection(features)
        for feature in common:
            if feature in features:
                if feature not in feature_counts:
                    feature_counts[feature] = {}

                if timestamp not in feature_counts[feature]:
                    feature_counts[feature][timestamp] = split_sentence.count(feature)
                else:
                    feature_counts[feature][timestamp] = int(feature_counts[feature][timestamp]) + split_sentence.count(feature)

                
            
    return feature_counts
        
        

def product_feature_counter(data_map,feature_list):

    product_counts = {}
    
    for node in data_map.nodes(data=True):
        if (node[1]['node_type'] == 'product'):
            product_name = node[1]['product_title']
            product_id = node[1]['product_id']
            product_sr = node[1]['product_salesrank']
            
            product_counts[product_name] = {}
            product_counts[product_name]['product_id'] = product_id
            product_counts[product_name]['product_sr'] = product_sr
            
          
            edge_list = list(data_map.edges(node[0]))
            review_text = " "
            for node_pair in edge_list:
                review_text = review_text + data_map[node_pair[0]][node_pair[1]][0]['edge_review_text'].lower()

            review_text = review_text.replace("."," ")
            review_text = review_text.replace(","," ")
            review_text = review_text.replace("!"," ")
            review_text = review_text.replace("?"," ")

            split_sentence = review_text.split()


            for feature in feature_list:
                product_counts[product_name][feature] = split_sentence.count(feature)

    with open('product_model_backup.json','w') as main_file:
                json.dump(product_counts,main_file)

    return product_counts
                
                
                
                
            

            
            
    

    
    

def data_appendage(features):

    meta_data_file_path = 'meta_Beauty.json'
    review_data_file_path = 'reviews_Beauty_06(11).json'
    data_map = nx.MultiGraph()
    

    print "Creating nodes for products"
    data_map = product_node_creator(meta_data_file_path,data_map)
    print "Finished creating nodes for products"

    print "Creating nodes for users and mapping reviews to products"
    data_map = user_node_creator(review_data_file_path,data_map)
    print "Finished creating user nodes"

    feature_counts = {}
    feature_counts = get_counts(data_map,features,feature_counts)
    return feature_counts




def feature_counter(feature_list):

    meta_data_file_path = 'meta_Beauty.json'
    review_data_file_path = 'reviews_Beauty_06(11).json'
    data_map = nx.MultiGraph()
    

    print "Creating nodes for products"
    data_map = product_node_creator(meta_data_file_path,data_map)
    print "Finished creating nodes for products"

    print "Creating nodes for users and mapping reviews to products"
    data_map = user_node_creator(review_data_file_path,data_map)
    print "Finished creating user nodes"

    feature_counts = {}
    feature_counts = product_feature_counter(data_map,feature_list)
    return feature_counts

    
    

