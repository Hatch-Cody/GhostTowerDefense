import json

def wave_data():
    with open('waves.json', 'r') as wave_file:
        wave_data = json.load(wave_file)
    return wave_data