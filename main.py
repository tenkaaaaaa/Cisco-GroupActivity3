import requests
import urllib.parse
from colorama import Fore, Style, init
from tabulate import tabulate

# Initialize colorama for colored terminal output
init(autoreset=True)

route_url = "https://graphhopper.com/api/1/route?"
# REPLACE THIS WITH YOUR ACTUAL API KEY
key = "70b93231-3140-4185-88fe-1a9456f95d40" 

def check_api_key(api_key):
    if api_key == "YOUR_API_KEY_HERE" or api_key == "":
        print(Fore.RED + "⚠️ ERROR: You forgot to put your API Key in the code!")
        return False
    return True

def print_banner():
    # UNIQUE FEATURE: Custom ASCII Art Banner
    banner = f"""
{Fore.CYAN}  ____                       _     _   _                       
 / ___|_ __ ___   __ _ _ __ | |__ | | | | ___  _ __   ___  ___ 
| |  _| '__/ _ \ / _` | '_ \| '_ \| |_| |/ _ \| '_ \ / _ \/ __|
| |_| | | | (_) | (_| | |_) | | | |  _  | (_) | |_) |  __/\__ \\
 \____|_|  \___/ \__, | .__/|_| |_|_| |_|\___/| .__/ \___||___/
                 |___/|_|                    |_|               
{Style.RESET_ALL}"""
    print(banner)
    print(Fore.YELLOW + "      Welcome to the Ultimate Route Planner! 🗺️\n")

def geocoding(location, key):
    if location.lower() == "help":
        print(Fore.CYAN + "\n--- HELP MENU ---")
        print("1. Enter a city and state (e.g., 'Washington, D.C.')")
        print("2. Type 'q' or 'quit' at any prompt to exit.")
        return "help", "null", "null", "Help"

    while location == "":
        location = input(Fore.YELLOW + "Enter the location again: ")
        
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    
    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code
    
    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]
        
        if "country" in json_data["hits"][0]:
            country = json_data["hits"][0]["country"]
        else:
            country = ""
        if "state" in json_data["hits"][0]:
            state = json_data["hits"][0]["state"]
        else:
            state = ""
            
        if len(state) != 0 and len(country) != 0:
            new_loc = name + ", " + state + ", " + country
        elif len(state) != 0:
            new_loc = name + ", " + state
        else:
            new_loc = name
            
        print(Fore.CYAN + "📍 Geocoding API URL for " + new_loc + " (Location Type: " + value + ")\n" + url)
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        if json_status != 200:
            print(Fore.RED + "❌ Geocode API status: " + str(json_status) + "\nError message: " + json_data["message"])
            
    return json_status, lat, lng, new_loc

# --- START OF APPLICATION ---
if not check_api_key(key):
    exit()

print_banner()

while True:
    print(Fore.MAGENTA + "\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("🚗 car, 🚲 bike, 🚶 foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    
    print(Fore.BLUE + "Which unit system would you like to use?")
    unit_choice = input("Enter 'm' for Metric (km) or 'i' for Imperial (miles): ").lower()
    is_metric = True if unit_choice == 'm' else False
    
    profile = ["car", "bike", "foot"]
    vehicle = input(Fore.YELLOW + "Enter a vehicle profile from the list above: ")
    if vehicle == "quit" or vehicle == "q":
        break
    elif vehicle in profile:
        vehicle = vehicle
    else:
        vehicle = "car"
        print(Fore.RED + "⚠️ No valid vehicle profile was entered. Using the car profile.")
        
    v_emoji = "🚗" if vehicle == "car" else ("🚲" if vehicle == "bike" else "🚶")

    loc1 = input(Fore.YELLOW + "Starting Location: ")
    if loc1 == "quit" or loc1 == "q":
        break
    orig = geocoding(loc1, key)
    if orig[0] == "help":
        continue
    
    loc2 = input(Fore.YELLOW + "Destination: ")
    if loc2 == "quit" or loc2 == "q":
        break
    dest = geocoding(loc2, key)
    if dest[0] == "help":
        continue
    
    print(Fore.WHITE + "=================================================")
    
    if orig[0] == 200 and dest[0] == 200:
        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])
        
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp
        paths_status = requests.get(paths_url).status_code
        paths_data = requests.get(paths_url).json()
        
        print(Fore.CYAN + "✅ Routing API Status: " + str(paths_status))
        
        if paths_status == 200:
            dist_meters = paths_data["paths"][0]["distance"]
            time_ms = paths_data["paths"][0]["time"]
            
            if is_metric:
                dist_str = f"{dist_meters/1000:.1f} km"
                round_trip = f"{(dist_meters*2)/1000:.1f} km"
            else:
                dist_str = f"{dist_meters/1000/1.61:.1f} miles"
                round_trip = f"{(dist_meters*2)/1000/1.61:.1f} miles"
                
            sec = int(time_ms / 1000 % 60)
            min = int(time_ms / 1000 / 60 % 60)
            hr = int(time_ms / 1000 / 60 / 60)
            
            # UNIQUE FEATURE: Route Summary
            print(Fore.GREEN + f"\n{v_emoji} Route Summary:")
            print(Fore.GREEN + f"Your trip from {orig[3]} to {dest[3]} by {vehicle} will take approximately {hr} hours and {min} minutes.")
            print(Fore.GREEN + f"📏 One-way Distance: {dist_str}")
            print(Fore.GREEN + f"🔄 Round-Trip Estimate: {round_trip}")
            print(Fore.GREEN + "⏱️ Trip Duration: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
            print(Fore.WHITE + "=================================================")
            
            table_data = []
            for each in range(len(paths_data["paths"][0]["instructions"])):
                path = paths_data["paths"][0]["instructions"][each]["text"]
                step_dist = paths_data["paths"][0]["instructions"][each]["distance"]
                
                if is_metric:
                    step_str = f"{step_dist/1000:.1f} km"
                else:
                    step_str = f"{step_dist/1000/1.61:.1f} miles"
                    
                table_data.append([path, step_str])
            
            print(tabulate(table_data, headers=["Instruction", "Distance"], tablefmt="grid"))
            print(Fore.WHITE + "=================================================")
            
        else:
            print(Fore.RED + "❌ Error message: " + paths_data["message"])
            print(Fore.WHITE + "=================================================")