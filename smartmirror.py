# smartmirror.py
# requirements
# requests, feedparser, traceback, Pillow

from tkinter import *
import time
import requests
import json
import traceback
import feedparser
from PIL import Image, ImageTk
from io import StringIO

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'MirrorMirror'

country_code = 'us'
weather_api_token = ''
with open('weather_key.txt', 'r') as f:
    weather_api_token = f.readline()
    
# maps open weather icons to
icon_lookup = {
	'clear': "assets/icons/clear.png",											# clear sky day
	'nt_clear': "assets/icons/nt_clear.png",								# clear sky night
	'partlycloudy': "assets/icons/partlycloudy.png",				# partly cloudy day
	'nt_partlycloudy': "assets/icons/nt_partlycloudy.png",	# partly cloudy day
	'mostlycloudy': "assets/icons/mostlycloudy.png",				# mostly cloudy day
	'nt_mostlycloudy': "assets/icons/nt_mostlycloudy.png",	# mostly cloudy night
	'cloudy': "assets/icons/cloudy.png",										# cloudy day
	'nt_cloudy': "assets/icons/nt_cloudy.png",							# cloudy night	
	'fog': "assets/icons/fog.png",													# foggy day
	'nt_fog': "assets/icons/nt_fog.png",										# foggy night	
	'tstorms': "assets/icons/tstorms.png",									# thunder storms day
	'nt_tstorms': "assets/icons/nt_tstorms.png",						# thunder storms night
	'rain': "assets/icons/rain.png",												# rain day
	'nt_rain': "assets/icons/nt_rain.png",									# rain night
}


class Clock(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg='black')
		# initialize time label
		self.time1 = ''
		self.timeLbl = Label(self, font=('Helvetica', 48), fg="white", bg="black")
		self.timeLbl.pack(side=TOP, anchor=E)
		# initialize day of week
		self.day_of_week1 = ''
		self.dayOWLbl = Label(self, text=self.day_of_week1, font=('Helvetica', 18), fg="white", bg="black")
		self.dayOWLbl.pack(side=TOP, anchor=E)
		# initialize date label
		self.date1 = ''
		self.dateLbl = Label(self, text=self.date1, font=('Helvetica', 18), fg="white", bg="black")
		self.dateLbl.pack(side=TOP, anchor=E)
		self.tick()

	def tick(self):
		time2 = time.strftime('%I:%M')
		day_of_week2 = time.strftime('%A')
		date2 = time.strftime("%b %d, %Y")
		# if time string has changed, update it
		if time2 != self.time1:
			self.time1 = time2
			self.timeLbl.config(text=time2)
		if day_of_week2 != self.day_of_week1:
			self.day_of_week1 = day_of_week2
			self.dayOWLbl.config(text=day_of_week2)
		if date2 != self.date1:
			self.date1 = date2
			self.dateLbl.config(text=date2)
		# calls itself every 200 milliseconds
		# to update the time display as needed
		# could use >200 ms, but display gets jerky
		self.timeLbl.after(200, self.tick)


class Weather(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg='black')
		self.temperature = ''
		self.location = ''
		self.currently = ''
		self.icon = ''
		self.highTemp = ''
		self.lowTemp = '' 
		
		self.degreeFrm = Frame(self, bg="black")
		self.degreeFrm.pack(side=TOP, anchor=W)
		
		self.temperatureLbl = Label(self.degreeFrm, font=('Helvetica', 94), fg="white", bg="black")
		self.temperatureLbl.pack(side=LEFT, anchor=N)
		self.highLowFrm = Frame(self.degreeFrm, bg="black")
		self.highLowFrm.pack(side=LEFT, anchor=W)
		self.lowTempLbl = Label(self.highLowFrm, font=('Helvetica', 20), fg="white", bg="black")
		self.lowTempLbl.pack(side=BOTTOM, anchor=W)
		self.highTempLbl = Label(self.highLowFrm, font=('Helvetica', 20), fg="white", bg="black")
		self.highTempLbl.pack(side=BOTTOM, anchor=W)
		self.iconLbl = Label(self.degreeFrm, bg="black")
		self.iconLbl.pack(side=LEFT, anchor=W, padx=20)
		
		self.infoFrm = Frame(self, bg="black")
		self.infoFrm.pack(side=TOP, anchor=W)
		self.currLocFrm = Frame(self.infoFrm, bg="black")
		self.currLocFrm.pack(side=LEFT, anchor=W)
		self.currentlyLbl = Label(self.currLocFrm, font=('Helvetica', 28), fg="white", bg="black")
		self.currentlyLbl.pack(side=TOP, anchor=W)
		self.locationLbl = Label(self.currLocFrm, font=('Helvetica', 18), fg="white", bg="black")
		self.locationLbl.pack(side=TOP, anchor=W)
		self.get_weather()
		
	def get_ip(self):
		try:
			ip_url = "http://jsonip.com/"
			req = requests.get(ip_url)
			ip_json = json.loads(req.text)
			return ip_json['ip']
		except Exception as e:
			traceback.print_exc()
			return "Error: %s. Cannot get ip." % e


	def get_weather(self):
		try:
			# get location
			location_req_url = "http://freegeoip.net/json/%s" % self.get_ip()
			r = requests.get(location_req_url)
			location_obj = json.loads(r.text)
			
			lat = location_obj['latitude']
			lon = location_obj['longitude']

			location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])

			# get weather
			weather_req_url = "http://api.wunderground.com/api/%s/conditions/q/VA/Alexandria.json" % (weather_api_token)
			r = requests.get(weather_req_url)
			weather_obj = json.loads(r.text)

			forecast_req_url = 'http://api.wunderground.com/api/%s/forecast/q/VA/Blacksburg.json' % (weather_api_token)
			r = requests.get(forecast_req_url)
			forecast_obj = json.loads(r.text)
			
			high = forecast_obj['forecast']['simpleforecast']['forecastday'][0]['high']
			low = forecast_obj['forecast']['simpleforecast']['forecastday'][0]['low']
			temps = {'low': low, 'high': high}
			

			degree_sign= u'\N{DEGREE SIGN}'
			
			temperature2 = "%s%s" % (str(int(weather_obj['current_observation']['temp_c'])), degree_sign)
			currently2 = weather_obj['current_observation']['weather']
			
			highTemp2 =  "H: %s%s" % (str(int(temps['high']['celsius'])), degree_sign)
			lowTemp2 = "L: %s%s" % (str(int(temps['low']['celsius'])), degree_sign)
			
			icon_id = weather_obj['current_observation']['icon']
			icon2 = None

			if icon_id in icon_lookup:
				icon2 = icon_lookup[icon_id]

			if icon2 is not None:
				if self.icon != icon2:
					self.icon = icon2
					
					image = Image.open(icon2)
					image = image.resize((100, 100), Image.ANTIALIAS)
					image = image.convert('L')
					photo = ImageTk.PhotoImage(image)
					
					self.iconLbl.config(image=photo)
					self.iconLbl.image = photo
			else:
				# remove image
				self.iconLbl.config(image='')

			if self.currently != currently2:
				self.currently = currently2
				self.currentlyLbl.config(text=currently2)
			if self.temperature != temperature2:
				self.temperature = temperature2
				self.temperatureLbl.config(text=temperature2)
			if self.highTemp != highTemp2:
				self.highTemp = highTemp2
				self.highTempLbl.config(text=highTemp2)
			if self.lowTemp != lowTemp2:
				self.lowTemp = lowTemp2
				self.lowTempLbl.config(text=lowTemp2)
			if self.location != location2:
				if location2 == ", ":
					self.location = "Cannot Pinpoint Location"
					self.locationLbl.config(text="Cannot Pinpoint Location")
				else:
					self.location = location2
					self.locationLbl.config(text=location2)
		except Exception as e:
			traceback.print_exc()
			print ("Error: %s. Cannot get weather." % e)

		self.after(600000, self.get_weather)

	@staticmethod
	def convert_kelvin_to_fahrenheit(kelvin_temp):
		return 1.8 * (kelvin_temp - 273) + 32


class News(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, *args, **kwargs)
		self.config(bg='black')
		self.title = 'Headlines'
		self.newsLbl = Label(self, text=self.title, font=('Helvetica', 28), fg="white", bg="black")
		self.newsLbl.pack(side=TOP, anchor=W)
		self.headlinesContainer = Frame(self, bg="black")
		self.headlinesContainer.pack(side=TOP)
		self.get_headlines()

	def get_headlines(self):
		try:
			# remove all children
			for widget in self.headlinesContainer.winfo_children():
				widget.destroy()
			if country_code == None:
				headlines_url = "https://news.google.com/news?ned=us&output=rss"
			else:
				headlines_url = "https://news.google.com/news?ned=%s&output=rss" % country_code
				
			feed = feedparser.parse(headlines_url)

			for post in feed.entries[0:5]:
				headline = NewsHeadline(self.headlinesContainer, post.title)
				headline.pack(side=TOP, anchor=W)

		except Exception as e:
			traceback.print_exc()
			print ("Error: %s. Cannot get news." % e)

		self.after(600000, self.get_headlines)


class NewsHeadline(Frame):
	def __init__(self, parent, event_name=""):
		Frame.__init__(self, parent, bg='black')

		image = Image.open("assets/Newspaper.png")
		image = image.resize((25, 25), Image.ANTIALIAS)
		image = image.convert('RGB')
		photo = ImageTk.PhotoImage(image)

		self.iconLbl = Label(self, bg='black', image=photo)
		self.iconLbl.image = photo
		self.iconLbl.pack(side=LEFT, anchor=N)

		self.eventName = event_name
		self.eventNameLbl = Label(self, text=self.eventName, font=('Helvetica', 18), fg="white", bg="black")
		self.eventNameLbl.pack(side=LEFT, anchor=N)


class Calendar(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg='black')
		self.title = 'Calendar Events'
		self.calendarLbl = Label(self, text=self.title, font=('Helvetica', 28), fg="white", bg="black")
		self.calendarLbl.pack(side=TOP, anchor=E)
		self.calendarEventContainer = Frame(self, bg='black')
		self.calendarEventContainer.pack(side=TOP, anchor=E)
		self.get_events()

	def get_credentials(self):
		"""Gets valid user credentials from storage.

		If nothing has been stored, or if the stored credentials are invalid,
		the OAuth2 flow is completed to obtain the new credentials.

		Returns:
		    Credentials, the obtained credential.
		"""
		home_dir = os.path.expanduser('~')
		credential_dir = os.path.join(home_dir, '.credentials')
		if not os.path.exists(credential_dir):
				os.makedirs(credential_dir)
		credential_path = os.path.join(credential_dir,
		                               'calendar-python-quickstart.json')

		store = Storage(credential_path)
		credentials = store.get()
		if not credentials or credentials.invalid:
			flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
			flow.user_agent = APPLICATION_NAME
			credentials = tools.run_flow(flow, store, flags)
			print('Storing credentials to ' + credential_path)
		return credentials

	def get_events(self):
		credentials = self.get_credentials()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http)

		now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
		eventsResult = service.events().list(
		    calendarId='primary', timeMin=now, maxResults=5, singleEvents=True,
		    orderBy='startTime').execute()
		events = eventsResult.get('items', [])

		# remove all children
		for widget in self.calendarEventContainer.winfo_children():
			widget.destroy()

		if not events:
			print('No upcoming events found.')
		for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))
			calendar_event = CalendarEvent(self.calendarEventContainer, 
																			event_name=event['summary'], 
																			event_time=start)
			calendar_event.pack(side=TOP, anchor=E)

		self.after(30000, self.get_events)


class CalendarEvent(Frame):
	def __init__(self, parent, event_name="Event 1", event_time='None'):
		Frame.__init__(self, parent, bg='black')
		self.eventName = event_time + ' ' + event_name
		self.eventNameLbl = Label(self, text=self.eventName, font=('Helvetica', 18), fg="white", bg="black")
		self.eventNameLbl.pack(side=TOP, anchor=E)


class FullscreenWindow:

	def __init__(self):
		self.tk = Tk()
		self.tk.configure(background='black')
		self.topFrame = Frame(self.tk, background = 'black')
		self.bottomFrame = Frame(self.tk, background = 'black')
		self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
		self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
		self.state = False
		self.tk.bind("<Return>", self.toggle_fullscreen)
		self.tk.bind("<Escape>", self.end_fullscreen)
		# clock
		self.clock = Clock(self.topFrame)
		self.clock.pack(side=RIGHT, anchor=N, padx=100, pady=60)
		# weather
		self.weather = Weather(self.topFrame)
		self.weather.pack(side=LEFT, anchor=N, padx=100, pady=60)
		# news
		self.news = News(self.bottomFrame)
		self.news.pack(side=LEFT, anchor=S, padx=100, pady=60)
		# calender - removing for now
		self.calender = Calendar(self.bottomFrame)
		self.calender.pack(side = RIGHT, anchor=S, padx=100, pady=60)
		
	def toggle_fullscreen(self, event=None):
		self.state = not self.state  # Just toggling the boolean
		self.tk.attributes("-fullscreen", self.state)
		return "break"

	def end_fullscreen(self, event=None):
		self.state = False
		self.tk.attributes("-fullscreen", False)
		return "break"

if __name__ == '__main__':
	w = FullscreenWindow()
	w.tk.mainloop()
