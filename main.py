""" File contains main function for fetching images from turtlesat applcation"""

import requests
import json
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from datetime import datetime
import os
from io import BytesIO
from PIL import Image

global recordType # global variable

def get_markers(type):
    # get today's date
    # send request to api that feeds map data
    # get id for each marker on map
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://www.turtlesat.org.au/api/Turtle/siteevent?format=json&toadAdminAssessment=true&startDateOnOrAfter=2010-01-01&startDateOnOrBefore={today}&onlyPublicData=true&siteEventTypes={type}"
    res = requests.get(url)
    return [t['id'] for t in res.json()['markers']]


def get_turtle(turtle_id):
    # send request to api for each individual id
    # check if image is in response
    # if yes, return url and include accessToken, else none
    
    type = recordType # global variable
    
    base = 'https://www.turtlesat.org.au'
    turtle_url = f"https://www.turtlesat.org.au/api/13/{type}/siteevent/{turtle_id}/content?format=json"
    turtle_data = requests.get(turtle_url).json()
    if 'markerGalleryPhoto' in turtle_data:
        token = turtle_data['markerGalleryPhoto']['accessTokenForUnapproved']
        return base + turtle_data['markerGalleryPhoto']['imageUrl'] + f'?accessToken={token}' + f'&turtle_id={turtle_id}' + f'&type={type}'


def scrape_turtlesat(type):
    # main scraper script
    # get ids to feed to api to get individual marker image
    # fetch images concurrently by mapping get_turtle() function to marker_ids
    # return urls that are not none
    marker_ids = get_markers(type)
    with ThreadPoolExecutor(max_workers=5) as executor:
        scraped_urls = list(tqdm(executor.map(get_turtle, marker_ids), total=len(
            marker_ids), desc=f'Scraping Images type : {type}'))
    image_urls = [url for url in scraped_urls if url]
    print(f'Images Found: {str(len(image_urls))}')
    return image_urls

if __name__ == '__main__':
    types = [1,2,5,6]
    for type in types:
        recordType = type # global variable
        print(f"Record type {type}")
        image_urls = scrape_turtlesat(type)
        with open(f'./image_urls_{type}.txt', 'w') as filehandle:
            json.dump(image_urls, filehandle)
            
