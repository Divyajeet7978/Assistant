from asyncio import subprocess
import pyttsx3
import subprocess
import datetime
import pywhatkit
import speech_recognition as say
import wikipedia
import webbrowser
from pywhatkit.remotekit import start_server
import flask
from datetime import datetime
import requests
engine =pyttsx3.init()
rate = engine.getProperty('rate')
voices =engine.getProperty('voices')
engine.setProperty('rate', rate-40)
print(voices[0].id)
engine.setProperty('voice',voices[0].id)
edge_path="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe %s" 
#runs a command prompt to fetch username and decode the byte output to UTF-8 
userName = subprocess.check_output("echo %USERNAME%", shell = True).decode("UTF-8") 
#Windows, for god knows whatever reason, is incapable of setting its home folder's name longer than 5 characters
userNameTrimmed = userName[0:5]
spotifyPath = "C://Users//" + userNameTrimmed + "//AppData//Roaming//Spotify//Spotify.exe"
def speak(audio):
    engine.say(audio)
    engine.runAndWait()
def wishMe():
        hour=int(datetime.now().hour)
        if hour>=0 and hour<12 :
            speak("good morning sir!")
        elif hour>=12 and hour<18:
            speak("Good Afternoon sir!")
        else:
            speak("Good Evening sir!")  
        speak("How can i help you today") 
def listen():
    r= say.Recognizer()
    with say.Microphone() as source:
        print("Listening")
        r.energy_threshold=200
        r.pause_threshold=1
        r.phrase_threshold=0.5
        audio= r.listen(source)
    try:
        print("Recognizing")
        query= r.recognize_google(audio,language='en-in')
        print(f"{query}\n")
    except Exception as e:
        print("say that again please")
        return "None"    
    return query
def time_format_for_location(utc_with_tz):
    local_time = datetime.utcfromtimestamp(utc_with_tz)
    return local_time.time()
def fetchWeather():
    r = say.Recognizer()
    with say.Microphone() as source:
        speak("What is the name of the city you want to know the weather of")
        r.energy_threshold = 200
        r.pause_threshold = 1
        r.phrase_threshold = 0.5
        audio = r.listen(source)
    try:
        cityName = r.recognize_google(audio, language = "en-in")
        print(f"{query}\n")
    except:
        print("Didn't catch that. Say that again")
        return "None"
    
    api_key = "c2c5dff269708e2c299a250cf1baccbf"
    # API url
    weather_url = 'http://api.openweathermap.org/data/2.5/weather?q=' + cityName + '&appid='+api_key
    # Get the response from fetched url
    response = requests.get(weather_url)
    # changing response from json to python readable 
    weather_info = response.json()
    #as per API documentation, if the cod is 200, it means that weather data was successfully fetched
    if weather_info['cod'] == 200:
        kelvin = 273 # value of kelvin
#-----------Storing the fetched values of weather of a city
        temp = int(weather_info['main']['temp'] - kelvin) #converting default kelvin value to Celcius
        feels_like_temp = int(weather_info['main']['feels_like'] - kelvin)
        pressure = weather_info['main']['pressure']
        humidity = weather_info['main']['humidity']
        wind_speed = weather_info['wind']['speed'] * 3.6
        sunrise = weather_info['sys']['sunrise']
        sunset = weather_info['sys']['sunset']
        timezone = weather_info['timezone']
        cloudy = weather_info['clouds']['all']
        description = weather_info['weather'][0]['description']
        sunrise_time = time_format_for_location(sunrise + timezone)
        sunset_time = time_format_for_location(sunset + timezone)
        #assigning Values to our weather varaible, to display as output
        
        weather = f"\nWeather of: {cityName}\nTemperature (Celsius): {temp}°\nFeels like in (Celsius): {feels_like_temp}°\nPressure: {pressure} hPa\nHumidity: {humidity}%\nSunrise at {sunrise_time} and Sunset at {sunset_time}\nCloud: {cloudy}%\nInfo: {description}"
    else:
        weather = f"\n\tWeather for '{cityName}' not found!\n\tKindly Enter valid City Name !!"
    
    speak(weather)
if __name__=="__main__":
    wishMe()
    while True:
        query = listen().lower()
        if'wikipedia' in query:
            speak('searching through wikipedia')
            query = query.replace("wikipedia","")
            results = wikipedia.summary(query, line=1)
            speak("According to wikipedia")
            print(results)
            speak(results)     
        elif'open youtube' in query:
            webbrowser.get(edge_path).open("youtube.com")
        elif'open google' in query:
            webbrowser.get(edge_path).open("google.com")
        elif'open spotify' in query:
            subprocess.call(spotifyPath)
        elif 'send message' in query:
            pywhatkit.sendwhatmsg("+918455038028","hey",21,00)
            print("sent successfully")
        elif 'goodbye' in query:
            speak("goodbye my friend")
        elif 'weather' in query:
            fetchWeather()
        elif 'exit' or 'exit program' or 'quit' in query:
            speak("Have a nice day!")
            break