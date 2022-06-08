import json

from flask import Flask, render_template

app = Flask(__name__, static_url_path='', template_folder='.')


@app.route('/')
def index():
    # return app.send_static_file('map.html')
    return render_template("./map.html")

@app.route('/locationData')
def locationData():
    with open('openstreetmap_location_data.json','r') as f:
        data = json.load(f)
    return data




if __name__ == '__main__':
    app.run(port='5353')
