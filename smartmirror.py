from tkinter import *
from smclock import *
from smweather import *
from smnews import *
from smcalendar import *
from MirrorListener import *
from MirrorController import *

import queue

cmdQueue = queue.Queue()
msgQueue = queue.Queue()

class FullscreenWindow:

	def __init__(self, cmdQueue, msgQueue):
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
		self.msgQueue = msgQueue
		# clock
		self.clock = Clock(self.topFrame)
		self.clock.pack(side=RIGHT, anchor=N, padx=100, pady=60)
      
      # weather
		self.weather = Weather(self.topFrame)
		self.weather.pack(side=LEFT, anchor=N, padx=100, pady=60)
      
      # news
		self.news = News(self.bottomFrame)
		#self.news.pack(side=LEFT, anchor=S, padx=100, pady=60)
      
      # calendar
		self.calendar = Calendar(self.bottomFrame)
		self.calendar.pack(side = RIGHT, anchor=S, padx=100, pady=60)
		
		# SR Sprite
		self.sr_sprite = mirrorSprite(self.topFrame)
		self.sr_sprite.pack(side=TOP, anchor=N)
		
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
		'''
		if not self.cmdQueue.empty():
			cmd = self.cmdQueue.get()
			if cmd == 'recognized':
				print('recognized')
				self.sr_sprite.set_color('blue')
				#self.sr_sprite.start_flashing()
			elif cmd == 'understood':
				print('understood')
				self.sr_sprite.set_color()
				#self.sr_sprite.start_flashing()
			elif cmd == 'Interpret Error':
				print('Interp Error')
				self.sr_sprite.set_color()
				#self.sr_sprite.start_flashing()
				#self.tk.after(1500, self.sr_sprite.set_color)
			else:
				try:
					exec(cmd)
					#self.sr_sprite.stop_flashing()
				except:
					print('Exec Error')
					#self.sr_sprite.set_color('red')
					#self.sr_sprite.start_flashing()
					#self.tk.after(1500, self.sr_sprite.stop_flashing)
					self.sr_sprite.set_color()
			self.cmdQueue.task_done()
		'''
		if not self.msgQueue.empty():
			msg = self.msgQueue.get()
			try:
				#print(msg)
				exec(msg)
			except Exception as e:
				print (str(e))
				print ('error in msg queue execution')
			self.msgQueue.task_done()
			
		self.tk.after(100, self.checkQueue)
  
	def change_temp_units(self):
		if self.weather.tunits == 'temp_c':
			self.weather.units = 'fahrenheit'
			self.weather.tunits = 'temp_f'
		else:
			self.weather.units = 'celsius'
			self.weather.tunits = 'temp_c'
			
		self.weather.get_weather()

if __name__ == '__main__':
	#listener = mirror_earror(cmdQueue)
	#listener.daemon = True
	#listener.start()
	controller = Controller(msgQueue)
	controller.start()	
	w = FullscreenWindow(cmdQueue, msgQueue)
	w.tk.mainloop()
