from flask import Flask, render_template, request
import requests
import urllib.parse

app = Flask(__name__)

# YOUR API KEY
API_KEY = "70b93231-3140-4185-88fe-1a9456f95d40" 

@app.route('/', methods=['GET', 'POST'])
def index():
    route_data = None
    error_message = None
    
    if request.method == 'POST':
        start_loc = request.form.get('start_loc')
        end_loc = request.form.get('end_loc')
        vehicle = request.form.get('vehicle')
        unit = request.form.get('unit')
        
        # 1. Geocode Start Location
        geo_url = "https://graphhopper.com/api/1/geocode?"
        start_url = geo_url + urllib.parse.urlencode({"q": start_loc, "limit": "1", "key": API_KEY})
        start_req = requests.get(start_url).json()
        
        # 2. Geocode End Location
        end_url = geo_url + urllib.parse.urlencode({"q": end_loc, "limit": "1", "key": API_KEY})
        end_req = requests.get(end_url).json()
        
        # 3. Check if locations were found
        if len(start_req["hits"]) == 0 or len(end_req["hits"]) == 0:
            error_message = "Could not find one of the locations. Please be more specific."
        else:
            s_lat = start_req["hits"][0]["point"]["lat"]
            s_lng = start_req["hits"][0]["point"]["lng"]
            e_lat = end_req["hits"][0]["point"]["lat"]
            e_lng = end_req["hits"][0]["point"]["lng"]
            
            # 4. Get Route
            route_url = "https://graphhopper.com/api/1/route?"
            op = f"&point={s_lat}%2C{s_lng}"
            dp = f"&point={e_lat}%2C{e_lng}"
            # Added points_encoded=false so we get raw coordinates for the map
            final_url = route_url + urllib.parse.urlencode({"key": API_KEY, "vehicle": vehicle, "points_encoded": "false"}) + op + dp
            route_req = requests.get(final_url).json()
            
            if "message" in route_req:
                error_message = route_req["message"]
            else:
                dist_meters = route_req["paths"][0]["distance"]
                time_ms = route_req["paths"][0]["time"]
                
                if unit == "metric":
                    dist_str = f"{dist_meters/1000:.1f} km"
                else:
                    dist_str = f"{dist_meters/1000/1.61:.1f} miles"
                    
                sec = int(time_ms / 1000 % 60)
                min = int(time_ms / 1000 / 60 % 60)
                hr = int(time_ms / 1000 / 60 / 60)
                time_str = f"{hr:02d}:{min:02d}:{sec:02d}"
                
                instructions = []
                for step in route_req["paths"][0]["instructions"]:
                    step_dist = step["distance"] / 1000 if unit == "metric" else step["distance"] / 1000 / 1.61
                    unit_label = "km" if unit == "metric" else "mi"
                    instructions.append({
                        "text": step["text"],
                        "dist": f"{step_dist:.1f} {unit_label}"
                    })
                
                # 5. Extract the raw coordinates for the map line
                # The API returns coordinates as [Longitude, Latitude]. We swap them to [Lat, Lng] for Leaflet.
                raw_points = route_req["paths"][0]["points"]["coordinates"]
                map_coords = [[point[1], point[0]] for point in raw_points]

                route_data = {
                    "start_name": start_req["hits"][0]["name"],
                    "end_name": end_req["hits"][0]["name"],
                    "distance": dist_str,
                    "time": time_str,
                    "instructions": instructions,
                    "map_coords": map_coords, # Pass this to JS
                    "start_coord": [s_lat, s_lng],
                    "end_coord": [e_lat, e_lng]
                }

    return render_template('index.html', route=route_data, error=error_message)

if __name__ == '__main__':
    app.run(debug=True)