import json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

class Watson(object):
    def __init__(self, api_key: str, api_url: str, api_version: str):
        self.api_key = api_key
        self.api_url = api_url
        self.api_version = api_version
        self.tone_analyzer = None

    def load(self) -> ToneAnalyzerV3:
        """Initiate a connection to Watson API

        Returns:
        tone_analyzer (ToneAnalyzerV3): Watson Tone Analyzer Connection
        """
        authenticator = IAMAuthenticator(self.api_key)
        self.tone_analyzer = ToneAnalyzerV3(
                version=self.api_version,
                authenticator=authenticator
            )
        self.tone_analyzer.set_service_url(self.api_url)
        return self.tone_analyzer

    def get_text_tone(self, text: str) -> object:
        """get a tone results for a review using Watson API

        Parameters:
        text (str): Input Text

        Returns:
        (object): Tone results
        """
        tone_scores = self.load().tone(
            {'text':text},
            content_type='application/json').get_result()
        return tone_scores['document_tone']['tones'] if 'document_tone' in tone_scores else {}
        
    