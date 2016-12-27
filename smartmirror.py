from tkinter import *
from smclock import *
from smweather import *
from smnews import *
from smcalendar import *
from MirrorListener import *

import queue
import threading

cmdQueue = queue.Queue()

class FullscreenWindow:

	def __init__(self, cmdQueue):
		self.tk = Tk()
		self.tk.configure(background='black')
		self.topFrame = Frame(self.tk, background = 'black')
		self.bottomFrame = Frame(self.tk, background = 'black')
		self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
		self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
		self.state = False
		self.tk.bind("<Return>", self.toggle_fullscreen)
		self.tk.bind("<Escape>", self.end_fullscreen)
		self.cmdQueue = cmdQueue
		# clock
		self.clock = Clock(self.topFrame)
		self.clock.pack(side=RIGHT, anchor=N, padx=100, pady=60)
      
      # weather
		self.weather = Weather(self.topFrame)
		self.weather.pack(side=LEFT, anchor=N, padx=100, pady=60)
      
      # news
		self.news = News(self.bottomFrame)
		self.news.pack(side=LEFT, anchor=S, padx=100, pady=60)
      
      # calender
		self.calender = Calendar(self.bottomFrame)
		self.calender.pack(side = RIGHT, anchor=S, padx=100, pady=60)
		self.checkQueue()
		
	def toggle_fullscreen(self, event=None):
		self.state = not self.state  # Just toggling the boolean
		self.tk.attributes("-fullscreen", self.state)
		return "break"
  
	def end_fullscreen(self, event=None):
		self.state = False
		self.tk.attributes("-fullscreen", False)
		return "break"
  
	def checkQueue(self):
		if not self.cmdQueue.empty():
			cmd = self.cmdQueue.get()
			try:
				exec(cmd)
			except:
				print('Couldnt run cmd')
				print(cmd)
				pass
			self.cmdQueue.task_done()
		self.tk.after(200, self.checkQueue)
  
	def change_temp_units(self):
		if self.weather.tunits == 'temp_c':
			self.weather.units = 'fahrenheit'
			self.weather.tunits = 'temp_f'
		else:
			self.weather.units = 'celsius'
			self.weather.tunits = 'temp_c'
			
		self.weather.get_weather()

if __name__ == '__main__':
    listener = mirror_earror(cmdQueue)
    listener.daemon = True
    listener.start()
    w = FullscreenWindow(cmdQueue)
    w.tk.mainloop()