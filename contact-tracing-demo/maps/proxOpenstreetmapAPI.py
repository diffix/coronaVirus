import json
import xml.etree.ElementTree as ET
from pprint import pprint

import numpy

places = {
    # 'home': ['building apartments','building bungalow',
    #          'building dormitory','building	house','building residential',
    #          'building static_caravan', 'addr:housenumber *'],
    'school': ['amenity	college','amenity kindergarten','amenity language_school','amenity music_school',
               'amenity school','amenity university','building kindergarten','building school','building university'],
    'office': ['amenity	bank','amenity clinic','amenity	dentist','amenity doctors','amenity	pharmacy','amenity	veterinary',
               'amenity	police','amenity post_office','building	office','office	*'],
    'sport': ['building	grandstand','building pavilion','building riding_hall','building sports_hall','building	stadium',
              'leisure stadium','leisure sports_centre','leisure swimming_pool','sport *'],
    'super': ['building	supermarket', 'shop supermarket'],
    'store': ['building	retail','shop *'],
    'restaurant': ['amenity	bar','amenity bbq','amenity	biergarten','amenity biergarten','amenity cafe',
                   'amenity	fast_food','amenity	food_court','amenity pub','amenity restaurant',]
}
for p,l in places.items():
    for ix, z in enumerate(l):
        l[ix] = z.replace('\t', ' ')

resultData = {}
chosenIds = []
totalSeenIds = []

# get map box coordinate for downloading map files from openstreetview
def getLocationBiasMatrix(numStep=4):
    boundingBox = {
        "top-left": {'x': 49.454434, 'y': 7.726833},
        'bottom-right': {'x': 49.423043, 'y': 7.808753}
    }
    # end is exclusive in ranges
    x_step = (boundingBox['top-left']['x'] - boundingBox['bottom-right']['x']) / numStep
    x_range: list = numpy.arange(boundingBox['bottom-right']['x'], boundingBox['top-left']['x'], x_step) \
        .tolist() + [boundingBox['top-left']['x']]
    y_step = (boundingBox['bottom-right']['y'] - boundingBox['top-left']['y']) / numStep
    y_range: list = numpy.arange(boundingBox['top-left']['y'], boundingBox['bottom-right']['y'], y_step) \
        .tolist() + [boundingBox['bottom-right']['y']]
    # for y in y_range:
    #     for x in x_range:
    #         yield x, y
    #
    # mat = []
    # for y in y_range:
    #     mat.append([[x,y] for x in x_range])
    # return mat
    x_range = [round(x,4) for x in x_range]
    y_range = [round(y,4) for y in y_range]
    return x_range, y_range

def distinctById(__elm1):
    global totalSeenIds
    return (__elm1.get('id') is not None)\
           and (__elm1.get('id') not in totalSeenIds)


def checkIfElmHasNameTag(__elm8):
    return len([tag1 for tag1 in __elm8.findall('tag') if tag1.get('k') == 'name']) > 0

def checkIfElmHasAmenityTag(__elm9):
    return len([tag2 for tag2 in __elm9.findall('tag') if 'amenity' in tag2.get('k')]) > 0

def checkIfElmHasAddrTag(__elm10):
    return len([tag3 for tag3 in __elm10.findall('tag') if 'addr' in tag3.get('k')]) > 0

def prepareJsonNode(__elm2, __node2, __place_type1, __lat1=None, __lon1=None):
    __tags1 = __elm2.findall('tag')
    amenity_tag1 = next((t for t in __tags1 if t.get('k') == 'amenity'), None)
    shop_tag2 = next((t for t in __tags1 if t.get('k') == 'shop'), None)
    __obj1 = dict()
    __obj1['name'] = next((tag4.get('v') for tag4 in __tags1 if tag4.get('k') == 'name'),
                         f'{__place_type1}-{__elm2.get("id")}')
    if __place_type1 == 'other':
        __obj1['name'] = f'{__place_type1}-{__elm2.get("id")}'
        __obj1['tags'] = ', '.join([f'{__t10.get("k")}={__t10.get("v")}' for __t10 in __tags1])
    if __node2 is not None:
        __obj1['lat'] = __node2.get('lat')
        __obj1['lon'] = __node2.get('lon')
    else:
        __obj1['lat'] = __elm2.get('lat')
        __obj1['lon'] = __elm2.get('lon')
    __obj1['id'] = __elm2.get('id')
    __obj1['nd'] = len(__elm2.findall('nd'))
    if amenity_tag1 is not None:
        __obj1['amenity'] = amenity_tag1.get('v')
    if shop_tag2 is not None:
        __obj1['shop'] = shop_tag2.get('v')
    address_tag3 = [t for t in __tags1 if 'addr' in t.get('k')]
    for _t in address_tag3:
        __obj1[_t.get('k')] = _t.get('v')
    return __obj1

def checkIfNotExist(__nodeJSONOrElm1):
    global chosenIds
    return (__nodeJSONOrElm1 is not None) and \
           (__nodeJSONOrElm1.get('id') is not None) and \
           (__nodeJSONOrElm1.get('id') not in chosenIds)

def appendToResultDataIfNotExist(__place_type2, __nodeJSON1):
    global chosenIds
    if checkIfNotExist(__nodeJSON1):
        createPlaceTypeInResultDataIfNotExist(__place_type2)
        resultData[__place_type2].append(__nodeJSON1)
        chosenIds.append(__nodeJSON1['id'])
        return __nodeJSON1

def createPlaceTypeInResultDataIfNotExist(__place_type3):
    global resultData
    if __place_type3 not in resultData.keys():
        resultData[__place_type3] = []

def processTagsAgainstPlaces(__tags2):
    for __place_type3, __place_tags3 in sorted(places.items(),key=lambda x: x[0], reverse=True):
        for t in __place_tags3:
            __k = t.split()[0]
            __v = t.split()[1]
            __node_tags = []
            if __v == '*':
                __node_tags.extend([tag for tag in __tags2 if tag.get('k') == __k])
            else:
                __node_tags.extend([tag for tag in __tags2 if tag.get('k') == __k and tag.get('v') == __v])
            if len(__node_tags) > 0:
                return True, __place_type3
    return False, ''

def tryToCategorizeAsHome(__elm6):
    return (checkIfElmHasAddrTag(__elm10=__elm6)
            and
            (not checkIfElmHasAmenityTag(__elm9=__elm6))
            and
            (not checkIfElmHasNameTag(__elm8=__elm6))
            )

def tryToCategorizeAsOther(__elm7):
    return (len(__elm7.findall('tag')) > 0
            and
            (
                len([__t11 for __t11 in __elm7.findall('tag') if __t11.get('k') == 'building']) > 0
                or
                checkIfElmHasAddrTag(__elm7)
            )
            and
            len([__t11 for __t11 in __elm7.findall('tag') if __t11.get('k') == 'amenity' and __t11.get('v') == 'vending_machine']) <= 0
            )

def processElement(__elm5, __node5=None):
    __tags5 = __elm5.findall('tag')
    shouldBeAdded, __place_type5 = processTagsAgainstPlaces(__tags5)
    if shouldBeAdded:
        __nodeJSON5 = prepareJsonNode(__elm2=__elm5, __node2=__node5, __place_type1=__place_type5)
        appendToResultDataIfNotExist(__place_type2=__place_type5, __nodeJSON1=__nodeJSON5)
        return True
    elif tryToCategorizeAsHome(__elm5):
        # categorize as home (in case no amenity and name tag)
        __nodeJSON6 = prepareJsonNode(__elm2=__elm5, __node2=__node5, __place_type1='home')
        appendToResultDataIfNotExist(__place_type2='home', __nodeJSON1=__nodeJSON6)
        return True
    elif tryToCategorizeAsOther(__elm5):
        # categorize as other (at least has a tag)
        __nodeJSON7 = prepareJsonNode(__elm2=__elm5, __node2=__node5, __place_type1='other')
        appendToResultDataIfNotExist(__place_type2='other', __nodeJSON1=__nodeJSON7)
        return True
    else:
        return False



# main program

for i in range(1, 17):
    print(f'processing map{i}.osm ...')
    root = ET.parse(f'map{i}.osm').getroot()
    for elm in root:
        if elm.get('lat') and elm.get('lon'):
            hasAdded = processElement(elm)
        else:
            nd = next((n for n in elm.findall('nd')), dict(ref='---'))
            its_node = next((n for n in root.findall('node') if n.get('id') == nd.get('ref')), None)
            if its_node is not None:
                hasAdded = processElement(elm, its_node)

    totalSeenIds.extend([elm.get('id') for elm in root if elm.get('id')])


with open('openstreetmap_location_data.json', 'w', encoding='utf-8') as f:
    json.dump(resultData, f, ensure_ascii=False, indent=4)

print()

for r,l in resultData.items():
    print(r, len(l))
print()
print('number of chosen ids:', len(chosenIds))
print('number of total seen ids:', len(totalSeenIds))



# restaurant 298
# office 261
# store 697
# sport 149
# home 12179
# school 177
# other 4109
# super 29
#
# number of chosen ids: 17899
# number of total seen ids: 162225