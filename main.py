"""
=============================================================================
Project: Project Activity 3 - Social Coding (Option 1)
Application Name: Smart Route Planner CLI
Team Members: [Insert Names Here]
Date: October 2026

Description: 
This Python application enhances the Lab 4.9.2 code by integrating the GraphHopper 
Geocoding and Routing APIs. It provides a command-line interface for users to 
get turn-by-turn directions. We have added UI enhancements (colors, ASCII art), 
data formatting (tables), and unique features (cost estimation, route warnings, 
and random travel quotes) to differentiate our project.

Prerequisites:
Before running this code, ensure the following libraries are installed:
    pip install requests colorama tabulate
You will also need a valid GraphHopper API key.
=============================================================================
"""

import requests
import urllib.parse
from colorama import Fore, Style, init
from tabulate import tabulate
import random

# Initialize colorama
init(autoreset=True)

# ==========================================
# UNICODE EMOJI DICTIONARY
# Using unicode escape sequences instead of hard-typed emojis for cleaner code.
# ==========================================
EMOJIS = {
    "warning": "\u26A0",       
    "error": "\u274C",         
    "success": "\u2705",       
    "pin": "\U0001F4CD",       
    "map": "\U0001F5FA",       
    "quote": "\U0001F4A1",     
    "car": "\U0001F697",       
    "bike": "\U0001F6B2",      
    "walk": "\U0001F6B6",     
    "ruler": "\U0001F4CF",     
    "refresh": "\U0001F504",   
    "timer": "\u23F1",         
    "money": "\U0001F4B0"      
}

# GraphHopper Routing API endpoint
route_url = "https://graphhopper.com/api/1/route?"

# ==========================================
# CONFIGURATION: API KEY
# Replace the string below with your actual GraphHopper API key.
# ==========================================
key = "YOUR_API_KEY_HERE" 

# ==========================================
# UNIQUE FEATURE: Random Travel Quotes
# ==========================================
travel_quotes = [
    "The journey is the reward. - Chinese Proverb",
    "Not all those who wander are lost. - J.R.R. Tolkien",
    "Traveling - it leaves you speechless, then turns you into a storyteller. - Ibn Battuta",
    "Life is short and the world is wide. - Unknown"
]

def check_api_key(api_key):
    """
    Validates that the user has replaced the placeholder API key.
    """
    if api_key == "YOUR_API_KEY_HERE" or api_key == "":
        print(Fore.RED + f"{EMOJIS['warning']} ERROR: You forgot to put your API Key in the code!")
        print(Fore.RED + "Please replace 'YOUR_API_KEY_HERE' with your actual key.")
        return False
    return True

def print_banner():
    """
    Prints a custom ASCII art banner to make the CLI application look modern.
    """
    banner = f"""
{Fore.CYAN}  ____                       _     _   _                       
 / ___|_ __ ___   __ _ _ __ | |__ | | | | ___  _ __   ___  ___ 
| |  _| '__/ _ \ / _` | '_ \| '_ \| |_| |/ _ \| '_ \ / _ \/ __|
| |_| | | | (_) | (_| | |_) | | | |  _  | (_) | |_) |  __/\__ \\
 \____|_|  \___/ \__, | .__/|_| |_|_| |_|\___/| .__/ \___||___/
                 |___/|_|                    |_|               
{Style.RESET_ALL}"""
    print(banner)
    print(Fore.YELLOW + f"      Welcome to the Ultimate Route Planner! {EMOJIS['map']}\n")

def geocoding(location, key):
    """
    Takes a string location and uses the GraphHopper Geocoding API 
    to convert it into latitude and longitude coordinates.
    """
    if location.lower() == "help":
        print(Fore.CYAN + "\n--- HELP MENU ---")
        print("1. Enter a city and state (e.g., 'Washington, D.C.')")
        print("2. Type 'q' or 'quit' at any prompt to exit.")
        print("3. Type 'help' to see this message again.\n")
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
        
        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")
            
        if len(state) != 0 and len(country) != 0:
            new_loc = name + ", " + state + ", " + country
        elif len(state) != 0:
            new_loc = name + ", " + state
        else:
            new_loc = name
            
        print(Fore.CYAN + f"{EMOJIS['pin']} Geocoding API URL for " + new_loc + " (Location Type: " + value + ")\n" + url)
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        if json_status != 200:
            print(Fore.RED + f"{EMOJIS['error']} Geocode API status: " + str(json_status) + "\nError message: " + json_data.get("message", "Unknown error"))
            
    return json_status, lat, lng, new_loc


# ==========================================
# MAIN APPLICATION LOOP
# ==========================================
if not check_api_key(key):
    exit()

print_banner()

while True:
    print(Fore.LIGHTBLACK_EX + f"\n{EMOJIS['quote']} Quote of the day: {random.choice(travel_quotes)}")

    print(Fore.MAGENTA + "\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print(f"{EMOJIS['car']} car, {EMOJIS['bike']} bike, {EMOJIS['walk']} foot")
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
        print(Fore.RED + f"{EMOJIS['warning']} No valid vehicle profile was entered. Using the car profile.")
        
    v_emoji = EMOJIS["car"] if vehicle == "car" else (EMOJIS["bike"] if vehicle == "bike" else EMOJIS["walk"])

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
        
        print(Fore.CYAN + f"{EMOJIS['success']} Routing API Status: " + str(paths_status))
        
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
            
            print(Fore.GREEN + f"\n{v_emoji} Route Summary:")
            print(Fore.GREEN + f"Your trip from {orig[3]} to {dest[3]} by {vehicle} will take approximately {hr} hours and {min} minutes.")
            print(Fore.GREEN + f"{EMOJIS['ruler']} One-way Distance: {dist_str}")
            print(Fore.GREEN + f"{EMOJIS['refresh']} Round-Trip Estimate: {round_trip}")
            print(Fore.GREEN + f"{EMOJIS['timer']} Trip Duration: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
            
            if vehicle == "car":
                fuel_cost_per_mile = 0.15
                total_cost = (dist_meters / 1000 / 1.61) * fuel_cost_per_mile
                print(Fore.YELLOW + f"{EMOJIS['money']} Estimated Fuel Cost: ${total_cost:.2f} (Based on $0.15/mile)")
                
            instructions_text = " ".join([step["text"] for step in paths_data["paths"][0]["instructions"]]).lower()
            if "highway" in instructions_text or "interstate" in instructions_text or "parkway" in instructions_text:
                print(Fore.RED + f"{EMOJIS['warning']} Route Warning: This route includes major highways/interstates. Drive safely!")
            if "toll" in instructions_text:
                print(Fore.RED + f"{EMOJIS['warning']} Route Warning: This route may include toll roads.")
                
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
            print(Fore.RED + f"{EMOJIS['error']} Error message: " + paths_data.get("message", "Unknown routing error"))
            print(Fore.WHITE + "=================================================")