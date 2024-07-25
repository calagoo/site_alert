""" Using PRTG API to get the list of sensors and their status """
import os
import sys
import json
import threading
import urllib3
import requests

os.system('cls' if os.name == 'nt' else 'clear')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Sensor:
    """ Sensor class """
    def __init__(self, group, status):
        self.group = group
        self.status = status
    


def get_api_data():
    """ Get the list of sensors and their status from PRTG API """
    # PRTG API Token

    username = input("Input Username: ") ## CHANGE
    password = input("Input Password: ") ## CHANGE

    url = "https://www.silkecom.net:8080/api/table.json?content=sensors&count=1000&username=" \
        + username + "&password=" + password

    # Send request to PRTG API
    # verify=False to ignore SSL certificate. ######### CHANGE AFTER TESTING #########
    response = requests.get(url, timeout=10, verify=False)

    if response.status_code != 200:
        print("Error:", response.status_code)
        sys.exit(1)
    
    # Save the response to a file

    with open("response_table.json", "w", encoding="UTF-8") as file:
        json.dump(response.json(), file)

def get_table_status():
    """ Get the status of each sensor """

    # Open the file containing the API response
    with open("response_table.json", "r", encoding="UTF-8") as file:
        data = json.load(file)

    # Get the list of sensors
    prtg_version = data["prtg-version"] # unused
    treesize = data["treesize"] # unused
    sensors = data["sensors"]
    sensor_list = []
    group_status = {}
    for sensor in sensors:
        group = sensor["group"]
        # Hardcoding to add a value to the group name - hopefully this doesn't backfire...
        if group.startswith("Crystal"):
            group = "0-" + group    
        status = sensor["status"]

        if group not in group_status:
            group_status[group] = []
        group_status[group].append(status)

    for status, group in zip(group_status.values(), group_status.keys()):
        for s in status:
            if s == "Up":
                group_status[group] = "Up"
            elif s == "Unusual":
                group_status[group] = "Unusual"
            elif s == "Paused":
                group_status[group] = "Paused"
            elif s == "Down":
                group_status[group] = "Down"
            else:
                group_status[group] = f"Unknown: {s}"
        
        sensor_list.append(Sensor(group, group_status[group]))

    print(f"Sensors Fetched: {len(sensor_list)}")
    print(f"Unusual Sensors: {len([s for s in sensor_list if s.status != 'Up'])}")

    # Sort Sensor_list by int at the beginning of the group name
    sensor_list.sort(key=lambda x: int(x.group.split("-")[0]))
    # get longest group name
    max_group = max(len(sensor.group) for sensor in sensor_list) + 1

    for s in sensor_list:
        print(f"{s.group:<{max_group}}|  {s.status}")

def main():
    """ Main function """
    
    # threading.Timer(5, main).start()
    print("Fetching Data...")
    
    # get_api_data() # Requests the API
    get_table_status()

if __name__ == "__main__":
    main()