import requests

# Replace with your FRED API key
api_key = "0eadee4ff6db19aa641e8648fd914476"

# Specify the series ID for plastic pipes
series_id = "PCU326122326122"

# Construct the API URL
api_url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"

# Make the API request
response = requests.get(api_url)
data = response.json()

# Extract relevant data points
observations = data["observations"]
for observation in observations:
    date = observation["date"]
    value = observation["value"]
    print(f"Date: {date}, Value: {value}")