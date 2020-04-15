from datetime import datetime
import json
from tqdm import tqdm
from app import injector
from connexion import NoContent
from injector import inject
from services.data import CSVLoader
from services.watson import Watson
import logging

log = logging.getLogger(__name__)
tqdm.pandas()

class Review(object):

    @inject
    def __init__(self, csv_loader_object: CSVLoader, watson_object: Watson):
        self.csv_loader = csv_loader_object
        self.watson = watson_object

    def analyze_reviews_tones(self, hotel_name=None):
        """Get tones of a hotel reviews

            Parameters:
            hotel_name (str): Hotel name

            Returns:
            (dict): Hotel normalized tones
        """
        hotels_data = self.csv_loader.get_hotel_tones(hotel_name, self.watson)
        return {'name':hotel_name, 'tones': hotels_data[hotel_name]['norm_tones']}, 200

review_instance = injector.get(Review)
