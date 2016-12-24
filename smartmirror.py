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


country_code = 'us'
weather_api_token = '92de97ca4c23964c'

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
			weather_req_url = "http://api.wunderground.com/api/%s/conditions/q/VA/Blacksburg.json" % (weather_api_token)
			r = requests.get(weather_req_url)
			weather_obj = json.loads(r.text)

			forecast_req_url = 'http://api.wunderground.com/api/92de97ca4c23964c/forecast/q/VA/Blacksburg.json'
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

			print(icon_id)

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

	def get_events(self):
		#TODO: implement this method
		# referenc https://developers.google.com/google-apps/calendar/quickstart/python

		# remove all children
		for widget in self.calendarEventContainer.winfo_children():
			widget.destroy()

		calendar_event = CalendarEvent(self.calendarEventContainer)
		calendar_event.pack(side=TOP, anchor=E)
		pass


class CalendarEvent(Frame):
	def __init__(self, parent, event_name="Event 1"):
		Frame.__init__(self, parent, bg='black')
		self.eventName = event_name
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
