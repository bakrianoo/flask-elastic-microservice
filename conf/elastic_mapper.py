hotel_mapping = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 2,
        "analysis": {
            "analyzer": {
                "edge_analyzer": {
                    "tokenizer": "edge_tokenizer"
                },
                "std_analyzer": {
                    "type": "standard"
                }
            },
            "tokenizer": {
                "edge_tokenizer": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 10,
                    "token_chars": [
                        "letter",
                        "digit"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "name": {"type": "keyword"},
            "city": {"type": "keyword"},
            "country": {"type": "keyword"},
            "location": {"type":"geo_point"},
            "postalCode": {"type": "keyword"},
            "province": {"type": "keyword"},
            "reviews": {
                "type": "nested", 
                "properties": {
                    "date": {"type": "date"},
                    "dateAdded": {"type": "date"},
                    "rating": {"type": "integer"},
                    "text": {"type": "text", "analyzer": "edge_analyzer"},
                    "title": {"type": "text", "analyzer": "std_analyzer"},
                    "userCity": {"type": "keyword"},
                    "username": {"type": "keyword"},
                    "userProvince": {"type": "keyword"},
                    "tones":{
                        "type": "nested",
                        "properties": {
                            "tone_id": {"type": "keyword"},
                            "score": {"type": "float"}
                        }
                    },
                }
            },
            "norm_tones": {
                "type": "nested", 
                "properties": {
                    "tone_id": {"type": "keyword"},
                    "score": {"type": "float"}
                }
            },
        }
    }
}