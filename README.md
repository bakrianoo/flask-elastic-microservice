# Flask ElasticSearch Micro-Service
This repo is a demo of how to design a micro-service for `ElasticSearch`. It also demonstrate how to interact with external API service like IBM Watson `IBM Watson Tone-Analyzer`
`Microservices Flask API application`

# Description
a Flask API with two different components/services:

- Hotel Review Tone Analyzer using IBM Watson Tone-Analyzer service.
- Index Hotel Reviews into an ElasticSearch service.

# How to Install/Run

- Install Python >= 3.6 (*3.6* or *3.7*)
- ``` pip install -r requirements.txt ```
- ``` cp env.example .env ```
- Edit `.env` to set your preferences
- Run ElasticSearch Service
- Place your csv data file in the `resources` directory
- ``` python app.py ```

# Elastic Mapping Configuration

Edit `conf/elastic_mapper.py` to edit the mapping architecture.

# API Documentation

You can access a live Swagger panel to review all of the APIs.
`http://localhost:9090/v1.0/ui/`

# API URLs

Example: 

- `http://localhost:9090/v1.0/review_tone_analyzer/Ramada Inn`

### Index/Update (Elastic) and Analyze a Specific Hotel Reviews Tones

`http://localhost:9090/v1.0/index_hotel/{hotel_name}`

Example: 

- `http://localhost:9090/v1.0/index_hotel/Ramada Inn`

### Index/Update (Elastic) and Analyze all of Hotels Reviews Tones

`http://localhost:9090/v1.0/index_hotel`

Example: 

- `http://localhost:9090/v1.0/index_hotel`


### Analyze a Hotel Reviews Tones using Watson API

`http://localhost:9090/v1.0/review_tone_analyzer/{hotel_name}`
