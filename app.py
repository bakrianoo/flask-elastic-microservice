import os
import connexion
from injector import Module, singleton, provider, Injector
from services.data import CSVLoader
from services.watson import Watson
from services.elastic import ElasticSearchIndex, ElasticSearchFactory
from conf.elastic_mapper import hotel_mapping
from flask_cors import CORS
import pathlib
from dotenv import load_dotenv
load_dotenv()

class DataModule(Module):        
    @singleton
    @provider
    def provide_csv_config(self) -> CSVLoader:
        csv_path = os.getcwd()+'/resources/sample.csv' if 'CSV_PATH' not in os.environ else os.environ['CSV_PATH']
        return CSVLoader(csv_path)

    @singleton
    @provider
    def provide_watson_connection(self) -> Watson:
        api_key = "" if 'API_KEY' not in os.environ else os.environ['API_KEY']
        api_url = "https://api.us-east.tone-analyzer.watson.cloud.ibm.com/instances/b740e841-1f37-478e-b8ac-5cc8395fac22" if 'API_URL' not in os.environ else os.environ['API_URL']
        api_version = '2017-09-21' if 'API_VERSION' not in os.environ else os.environ['API_VERSION']
        return Watson(api_key, api_url, api_version)

    @singleton
    @provider
    def provide_elastic_connection(self) -> ElasticSearchIndex:
        host = "127.0.0.1" if 'ELASTIC_HOST' not in os.environ else os.environ['ELASTIC_HOST']
        port = 9200 if 'ELASTIC_PORT' not in os.environ else int(os.environ['ELASTIC_PORT'])
        index_name = 'hotels' if 'ELASTIC_INDEX_NAME' not in os.environ else os.environ['ELASTIC_INDEX_NAME']
        type_name = 'hotel' if 'ELASTIC_TYPE_NAME' not in os.environ else os.environ['ELASTIC_TYPE_NAME']
        elastic_factory = ElasticSearchFactory(host, port)
        return ElasticSearchIndex(elastic_factory, index_name, type_name, hotel_mapping)


injector = Injector([DataModule()])
app = connexion.App(__name__)
CORS(app.app, methods=['POST', 'PUT', 'DELETE'], allow_headers=['Content-Type'])
app_title = 'APP Title' if 'APP_TITLE' not in os.environ else os.environ['APP_TITLE']
app_port = 9090 if 'APP_PORT' not in os.environ else int(os.environ['APP_PORT'])

@app.route('/')
def home():
    return app_title, 200

if __name__ == '__main__':
    app.add_api('swagger/review.yaml', arguments={'title': app_title})
    app.run(port=app_port, server='gevent')
