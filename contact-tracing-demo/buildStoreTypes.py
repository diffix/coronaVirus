import json
import os


def loadAddresses(pathToAddresses):
    with open(pathToAddresses) as f:
        return json.load(f)


labels = dict()


def countLabel(label):
    if label not in labels:
        labels[label] = 0
    labels[label] += 1


numNewStoreTypes = 20
addressPath = os.path.join('maps', 'openstreetmap_location_data.json')

addresses = loadAddresses(addressPath)
print(f"Loading addresses ...")
total = 0
for pn, lst in addresses.items():
    print(f"   {len(lst)} addresses of type {pn}")
    total += len(lst)
print(f"... for a total of {total} final addresses.")

if 'store' not in addresses:
    raise ValueError("store not in addresses")

stores = addresses['store']
print(f"Obtained {len(stores)} stores from {total} addresses.")
for store in stores:
    if 'shop' in store:
        countLabel(store['shop'])
    if 'amenity' in store:
        countLabel(store['amenity'])

labelLst = [(lb, c) for lb, c in labels.items()]
labelLst.sort(key=lambda i: i[1], reverse=True)
print(f"Found {len(labelLst)} distinct labels for stores:")
for lb, c in labelLst:
    print(f"   {lb}: {c}")

newStoreTypes = [['store', 0]]
for i in range(numNewStoreTypes):
    lb, c = labelLst.pop(0)
    if lb == 'vacant':
        newStoreTypes[0][1] += c
        lb, c = labelLst.pop(0)
    newStoreTypes.append([lb, c])
for _, c in labelLst:
    newStoreTypes[0][1] += c

print(f"Copy the following code into PlaceInfo:\n--------------------\n")
print(f"storeTypes = {{")
for storeType in newStoreTypes:
    print(f"    '{storeType[0]}': {storeType[1]},")
print(f"}}")
