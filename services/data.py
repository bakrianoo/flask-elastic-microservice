import pandas as pd
from os import path
from collections import defaultdict
from services.watson import Watson

class CSVLoader(object):
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.dataframe = None

    def load(self, hotel_name='') -> pd.DataFrame:
        """Load the reviews of all of the hotels or a specific hotel  

            Parameters:
            hotel_name (str): Hotel name (If empty, all hotels will be loaded)

            Returns:
            dataframe (pd.DataFrame): Dataframe contains the hotel records
        """
        if path.exists(self.csv_path):
            dataframe = pd.read_csv(self.csv_path)
            dataframe = dataframe[ dataframe['categories'] =='Hotels' ]
            # load targeted hotel data if passed
            if hotel_name != '':
                dataframe = dataframe[dataframe['name'] == hotel_name]
            return dataframe
        return pd.DataFrame({})
    
    def get_hotel_tones(self, hotel_name, watson: Watson) -> dict:
        """Get the hotel tones using Watson API

            Parameters:
            hotel_name (str): Hotel name (If empty, all hotels will be loaded)
            watson (Watson): Watson API connection

            Returns:
            hotels_data (dict): normalized tones of an hotel.
        """
        self.dataframe = self.load(hotel_name)
        hotels_data = {}
        
        if not self.dataframe.empty:
            # fetch tones scored using Watson API
            self.dataframe['tones'] = self.dataframe['reviews.text'].progress_apply(watson.get_text_tone)

            # in case of multiple hotels, we need to parse each one seperately
            for hotel in self.dataframe['name'].unique():
                # calculate normalized scores
                hotel_dataframe = self.dataframe[ self.dataframe['name']==hotel ]
                tones = defaultdict(list)

                for i in range(hotel_dataframe.shape[0]):
                    if 'tones' in hotel_dataframe.iloc[i]:
                        for tone in hotel_dataframe.iloc[i]['tones']:
                            tones[tone['tone_id']].append(tone['score'])
                
                normalized_tones = { tone_id: sum(scores)/len(scores) for tone_id, scores in tones.items() }
                hotels_data[hotel] ={
                    'data': hotel_dataframe,
                    'norm_tones': normalized_tones
                }
        
        return hotels_data
        

    