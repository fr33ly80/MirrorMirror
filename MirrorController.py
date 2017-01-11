# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 12:12:12 2016

@author: brend
"""

import queue
import threading
import time

class Controller(threading.Thread):
	def __init__(self, msgQueue):
		threading.Thread.__init__(self)
		self.daemon = True
		self.msgQueue = msgQueue
		self.i= 0
		self.tick()
		self.update_news()
		self.update_weather()
		self.update_calendar()
		
	def tick(self):
		self.msgQueue.put('self.clock.tick()')
		
	def update_weather(self):
		self.msgQueue.put('self.weather.get_weather()')
		
	def update_news(self):
		self.msgQueue.put('self.news.get_headlines()')
		
	def update_calendar(self):
		self.msgQueue.put('self.calendar.get_events()')
		
	
	def run(self):
		while(1):
			time.sleep(0.5)
			self.i += 0.5
			self.tick()
			if self.i%600 == 0:
				self.update_news()
			elif self.i%400 == 0:
				self.update_calendar()
			elif self.i%200 == 0:
				self.update_weather()

if __name__ == '__main__':
	msgQueue = queue.Queue()
	controller = Controller(msgQueue)
	controller.start()
