from app import injector
from connexion import NoContent
from injector import inject
from services.data import CSVLoader
from services.watson import Watson
from services.elastic import ElasticSearchIndex
from collections import defaultdict
import pandas as pd
import uuid

from datetime import datetime
from tqdm import tqdm
import logging

log = logging.getLogger(__name__)
tqdm.pandas()

class Elastic(object):

    @inject
    def __init__(self, csv_loader_object: CSVLoader, watson_object: Watson, elastic_object: ElasticSearchIndex):
        self.csv_loader = csv_loader_object
        self.watson = watson_object
        self.elastic = elastic_object

    def index_all_hotel_reviews(self) -> list:
        """Index all of the hotel in the csv file.

            Returns:
            indexed_hotels (list): list of the indexed hotel
        """
        return self.index_hotel_reviews('')

    def index_hotel_reviews(self, hotel_name=None) -> list:
        """Index a specific hotel name

            Parameters:
            hotel_name (str): Hotel name

            Returns:
            indexed_hotels (list): list of the indexed hotel

        """
        hotels_data = self.csv_loader.get_hotel_tones(hotel_name, self.watson)
        indexed_hotels = []

        if len(hotels_data) > 0:
            for hotel, result in hotels_data.items():
                doc_id, hotel_payload = self.get_hotel_payload(hotel, result['data'])

                indexed_hotels.append({
                    "name": hotel,
                    "tones": hotel_payload['norm_tones']
                })

                _ = self.elastic.index(doc_id, hotel_payload)

        return indexed_hotels, 200

    def get_hotel_payload(self, hotel_name: str, hotel_data: pd.DataFrame) -> bool:
        """Construct each hotel document to be indexed in EalsticSearch.

            Parameters:
            hotel_name (str): Hotel name
            hotel_data (pd.DataFrame): Related meta-info and reviews to the hotel

            Returns:
            doc_id (str): unique ID of the hotel document
            hotel_record (dict): Hotel document to be indexed in ElasticSearch

        """
        # get existed indexed document, if exists
        ind_doc = self.elastic.get_hotel_document(hotel_name)
        # get realted reviews
        reviews = []
        review_texts = []
        doc_id = uuid.uuid1()

        # check for existed reviews (indexed before)
        if 'hits' in ind_doc and ind_doc['hits']['total']['value'] > 0:
            doc_id = ind_doc['hits']['hits'][0]['_id']

            if 'reviews' in ind_doc['hits']['hits'][0] and len(ind_doc['hits']['hits'][0]['reviews']) > 0:
                reviews = ind_doc['hits']['hits'][0]['reviews']
                for rv in ind_doc['hits']['hits'][0]['reviews']:
                    review_texts.append(rv['text'])
        review_texts = set(review_texts)

        # get hotel realted records in the dataframe
        hotel_df = self.csv_loader.dataframe[ self.csv_loader.dataframe['name'] == hotel_name ]
        # build the document body
        hotel_record = {
            "name": self.parse_save_value(hotel_df.iloc[0]['name'], "txt"),
            "city": self.parse_save_value(hotel_df.iloc[0]['city'], "txt"),
            "country": self.parse_save_value(hotel_df.iloc[0]['country'], "txt"),
            "location": {
                "lat":self.parse_save_value(hotel_df.iloc[0]['latitude'], 'float'),
                "lon":self.parse_save_value(hotel_df.iloc[0]['longitude'], 'float')
            },
            "postalCode": self.parse_save_value(hotel_df.iloc[0]['postalCode'], 'txt'),
            "reviews": reviews,
            "norm_tones": []
        }

        # check for new reviews
        for i in range(hotel_df.shape[0]):
            review_txt = self.parse_save_value(hotel_df.iloc[i]["reviews.text"], 'txt')
            # accept the new review
            if review_txt not in review_texts:
                hotel_record["reviews"].append({
                    "date": self.parse_save_value(hotel_df.iloc[i]["reviews.date"], 'date'),
                    "dateAdded": self.parse_save_value(hotel_df.iloc[i]["reviews.dateAdded"], 'date'),
                    "rating": self.parse_save_value(hotel_df.iloc[i]["reviews.rating"], 'int'),
                    "text": review_txt,
                    "title": self.parse_save_value(hotel_df.iloc[i]["reviews.title"], 'txt'),
                    "userCity": self.parse_save_value(hotel_df.iloc[i]["reviews.userCity"], 'txt'),
                    "username": self.parse_save_value(hotel_df.iloc[i]["reviews.username"], 'txt'),
                    "userProvince": self.parse_save_value(hotel_df.iloc[i]["reviews.userProvince"], 'txt'),
                    "tones": hotel_df.iloc[i]["tones"]
                })
        
        # calculate the normalized tones
        norm_tones = defaultdict(list)
        for rv in hotel_record["reviews"]:
            for tone in rv['tones']:
                norm_tones[tone['tone_id']].append(tone['score'])
        
        hotel_record["norm_tones"] = { tone_id: sum(scores)/len(scores) for tone_id, scores in norm_tones.items() }

        return doc_id, hotel_record

    def parse_save_value(self, value, val_type='na'):
        """Cast/Solve pandas values before indexing in the ElasticSearch

            Parameters:
            value (str/int/float/datetime): The value
            val_type (str): Type of the value

            Returns:
            value (str/int/float/datetime): The casted/solved value
        """
        if val_type == 'date':
            return pd.to_datetime(value) if not pd.isna(value) else datetime(1970,1,1,0,0)
        elif val_type == 'txt':
            return str(value) if not pd.isna(value) else "Other"
        elif val_type == "float":
            return float(value) if not pd.isna(value) else 0.0
        elif val_type == "int":
            return int(value) if not pd.isna(value) else 0
        return ""


elastic_instance = injector.get(Elastic)
