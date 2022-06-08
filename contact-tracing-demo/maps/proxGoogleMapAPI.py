import copy
import json
import time

import numpy
import requests
from PyInquirer import style_from_dict, Token, prompt
from pprint import pprint
from proxPlaces import PlaceInfo

def _filterResultData(obj, *fields):
    res = {}
    for f in fields:
        if f == 'lat':
            res['lat'] = obj['geometry']['location']['lat']
        elif f == 'lon':
            res['lon'] = obj['geometry']['location']['lng']
        elif f == 'address':
            res[f] = obj['formatted_address']
        else:
            res[f] = obj[f]
    return res


class GoogleMapAPIClient:
    def __init__(self):
        self.baseUrl =  "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.parameters = {
            "query": "",
            "type":""
        }
        self.key = "AIzaSyBrUX3jzZNPB-sJIwMGgH0oI-wh3C9Atb8"
        self. output = []
        self.boundingBox = {
            "top-left": {'x': 49.454434, 'y': 7.726833},
            'bottom-right': {'x': 49.423043, 'y': 7.808753}
        }

    def buildQuery(self, **kwargs):
        self.parameters = kwargs
        return self

    @property
    def url(self):
        return f"{self.baseUrl}?{'&'.join([f'{param}={value}' for param, value in self.parameters.items()])}&key={self.key}"

    def _boundingBoxContainsPoint(self, obj):
        x = float(obj['lat'])
        y = float(obj['lon'])
        return self.boundingBox['top-left']['x'] >= x >= self.boundingBox['bottom-right']['x'] and \
               self.boundingBox['top-left']['y'] <= y <= self.boundingBox['bottom-right']['y']

    def fetch(self, fields='name,lat,lon,address'):
        output = []
        pagetoken = ""
        flagFetch = True
        _invalid_request_count = 0
        while flagFetch:
            res = requests.get(self.url + pagetoken).json()
            if res["status"] == "OK":
                output.extend(
                    [_filterResultData(item, *fields.split(',')) for item in res['results']]
                )
                if 'next_page_token' in res and res['next_page_token'] is not None:
                    print("fetching...")
                    pagetoken = "&pagetoken=" + res['next_page_token']
                    time.sleep(1)
                else:
                    flagFetch = False
            elif res["status"] == "INVALID_REQUEST":
                _invalid_request_count += 1
                if _invalid_request_count >= 3:
                    print(f'request failed. error message: more than 3 INVALID_REQUEST')
                print("fetching...")
                time.sleep(1)
            else:
                ex = res["error_message"] if 'error_message' in res else ''
                print(f'request failed. error message: {ex}')
        print(f'before filter: {len(self.output)}')
        output_filtered = list(filter(lambda x: self._boundingBoxContainsPoint(x), output))
        print(f'after filter: {len(self.output)}')
        self.output = output_filtered
        return output_filtered

    def writeToFile(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.output, f, ensure_ascii=False, indent=4)

    def getLocationBiasMatrix(self,numStep = 3):
        # end is exclusive in ranges
        x_step = (self.boundingBox['top-left']['x'] - self.boundingBox['bottom-right']['x']) / numStep
        x_range: list = numpy.arange(self.boundingBox['bottom-right']['x'], self.boundingBox['top-left']['x'], x_step)\
                .tolist()
        y_step = (self.boundingBox['bottom-right']['y'] - self.boundingBox['top-left']['y']) / numStep
        y_range: list = numpy.arange(self.boundingBox['top-left']['y'], self.boundingBox['bottom-right']['y'], y_step) \
            .tolist()
        for y in y_range:
            for x in x_range:
                yield x, y

def _confirm(msg):
    _a = prompt([{'type': 'confirm', 'name':'answer', 'message': msg}])
    return _a['answer']

def proxGoogleMapAPIDriver():
    # home
    placeTypes = {
        # 'school':{
        #     'type': ['school','secondary_school', 'primary_school', 'university'],
        #     'query': ''
        # },
        # 'sport': {
        #     'type': ['gym','bowling_alley','stadium'],
        #     'query': ''
        # },
        # 'super':{
        #     'type': ['grocery_or_supermarket', 'supermarket'],
        #     'query': ''
        # },
        # 'store':{
        #     'type': ['bicycle_store','book_store','car_dealer','car_rental','clothing_store',
        #              'convenience_store','department_store','drugstore','electronics_store','furniture_store',
        #              'hardware_store','home_goods_store','jewelry_store','store','shopping_mall','shoe_store',
        #              'pet_store', 'movie_rental','liquor_store'],
        #     'query': ''
        # },
        # 'restaurant':{
        #     'type': ['meal_takeaway','cafe','restaurant','bar','bakery'],
        #     'query': ''
        # },
        'office': {
            'type': ['accounting','airport','lawyer','local_government_office','locksmith','bank',
                     'beauty_salon','meal_delivery','moving_company','painter','car_repair',
                     'car_wash','pharmacy','physiotherapist','plumber','police','post_office',
                     'city_hall','real_estate_agency','courthouse','dentist','doctor','electrician',
                     'embassy','fire_station','florist','taxi_stand','hair_care','hospital','travel_agency',
                     'insurance_agency','veterinary_care','zoo','laundry','lodging'],
            'query': ''
        }
    }
    _client_ = GoogleMapAPIClient()
    result = {i: [] for i in placeTypes.keys()}
    remaining_placeTypes = list(placeTypes.keys())
    try:
        for place, api_params in placeTypes.items():
            print(f"\n          ======( place type: {place} )======\n")
            for lat,lon in _client_.getLocationBiasMatrix():
                for t in api_params['type']:
                    result[place].extend(_client_.buildQuery(query=api_params['query'],type=t,
                                                             location=f'{lat},{lon}', radius=50000)
                                                 .fetch('name,lat,lon,address,place_id'))

            result[place] = list({v['place_id']: v for v in result[place]}.values())
            print(f'###( total unique {place} fetched: {len(result[place])} )###')
            remaining_placeTypes.remove(place)
        # remove place_id
        for _K, _l in result.items():
            for _obj in _l:
                _obj.pop('place_id')
        with open('location_data.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print('processed finished successfully. file saved.')
    except (KeyboardInterrupt, Exception) as ex:
        print('\n%%%%%%%%%% exception:', str(ex))
        print('remaining placeTypes:',remaining_placeTypes)
        for _K, _l in result.items():
            for _obj in _l:
                    _obj.pop('place_id')
        with open('location_data_until_error.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print('temp file saved under location_data_until_error.json')

def fetchedDataStats():
    with open('googlemap_location_data.json','r',encoding='utf-8') as f:
        data = json.load(f)
    for p in PlaceInfo.getPlaceNames():
        if p in data:
            print(p,len(data[p]))

def CLI():
    style = style_from_dict({
        Token.Separator: '#cc5454',
        Token.QuestionMark: '#673ab7 bold',
        Token.Selected: '#cc5454',  # default
        Token.Pointer: '#673ab7 bold',
        Token.Instruction: '',  # default
        Token.Answer: '#f44336 bold',
        Token.Question: '',
    })
    q1 = [
        {
            'type': 'input',
            'name': 'query',
            'message': 'Enter search query:',
            'filter': lambda x: '+'.join(x.split())
        },
        {
            'type': 'input',
            'name': 'type',
            'message': 'Enter place type (optional): [bank, bar, restaurant, ...]',
        },
        {
            'type': 'input',
            'name': 'fields',
            'message': 'What fields should be fetched (comma separated list, default: place_id,name,location,formatted_address)',
            'default': 'place_id,name,location,formatted_address'
        },
    ]
    a1 = prompt(q1, style=style)
    client = GoogleMapAPIClient()
    client.parameters = {param: value for param, value in a1.items() if value != ''}
    client.fetch(fields=a1['fields'])
    print(f"total {len(client.output)} records fetched.")
    q2 = [
        {
            'type': 'confirm',
            'name': 'shouldShow',
            'message': f'{numResults} fetched. Do you want to print? ',
            'default': False
        }
    ]
    a2 = prompt(q2, style=style)
    if a2['shouldShow']:
        pprint(client.output)
    q3 = [
        {
            'type': 'confirm',
            'name': 'shouldWrite',
            'message': f'Do you want to write to file? ',
            'default': False
        },
        {
            'type': 'input',
            'name': 'outFileName',
            'message': f'Enter a name for output file: (default: place_api_output.json)',
            'default': 'place_api_output.json',
            'when': lambda a: a['shouldWrite']
        }
    ]
    a3 = prompt(q3, style=style)
    if a3['shouldWrite']:
        client.writeToFile(filename=a3['outFileName'])
    print("\ndone.\n")

if __name__ == '__main__':
    # CLI()
    # proxGoogleMapAPIDriver()
    # g = GoogleMapAPIClient()
    # g.getLocationBiasMatrix()
    fetchedDataStats()