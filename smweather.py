# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 18:17:00 2016

@author: brend
"""

from tkinter import *
import traceback
import requests
import json
from PIL import Image, ImageTk
import sys

weather_api_token = ''
with open('weatherkey.txt', 'r') as f:
    weather_api_token = f.readline()

# maps weather underground icons to ids
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


class Weather(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg='black')
		self.temperature = ''
		self.units = 'celsius'
		self.tunits = 'temp_c'
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
		#self.get_weather()
		
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

			location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])

			# get weather
			weather_req_url = "http://api.wunderground.com/api/%s/conditions/q/%s/%s.json" % (weather_api_token, location_obj['region_code'], location_obj['city'])
			r = requests.get(weather_req_url)
			weather_obj = json.loads(r.text)

			forecast_req_url = "http://api.wunderground.com/api/%s/forecast/q/%s/%s.json" % (weather_api_token, location_obj['region_code'], location_obj['city'])
			r = requests.get(forecast_req_url)
			forecast_obj = json.loads(r.text)
			
			high = forecast_obj['forecast']['simpleforecast']['forecastday'][0]['high']
			low = forecast_obj['forecast']['simpleforecast']['forecastday'][0]['low']
			temps = {'low': low, 'high': high}
			

			degree_sign= u'\N{DEGREE SIGN}'
			
			temperature2 = "%s%s" % (str(int(weather_obj['current_observation'][self.tunits])), degree_sign)
			currently2 = weather_obj['current_observation']['weather']
			
			highTemp2 =  "H: %s%s" % (str(int(temps['high'][self.units])), degree_sign)
			lowTemp2 = "L: %s%s" % (str(int(temps['low'][self.units])), degree_sign)
			
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

		#self.after(600000, self.get_weather)

	@staticmethod
	def convert_kelvin_to_fahrenheit(kelvin_temp):
		return 1.8 * (kelvin_temp - 273) + 32