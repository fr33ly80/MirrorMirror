# -*- coding: utf-8 -*-
"""
Created on Sat Dec 24 11:46:15 2016

@author: brend
"""

import threading
import speech_recognition as sr
import wit
import nltk
from tkinter import *
from PIL import Image, ImageTk

WIT_AI_KEY = ''
with open('wit_key.txt', 'r') as f:
    WIT_AI_KEY = f.readline()

class mirror_earror(threading.Thread):
	def __init__(self, cmdQueue):
		threading.Thread.__init__(self)
		self.daemon = True
		self.r = sr.Recognizer()
		self.m = sr.Microphone()
		self.cmdQueue = cmdQueue
		with self.m as source:
			self.r.adjust_for_ambient_noise(source) # we only need to calibrate once, before we start listening
		self.stop_listening = self.r.listen_in_background(self.m, self.callback)
        # start listening in the background (note that we don't have to do this inside a `with` statement)
        # `stop_listening` is now a function that, when called, stops background listening

    # this is called from the background thread
	def callback(self, recognizer, audio):
        # received audio data, now we'll recognize it using Google Speech Recognition
		#try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
		self.cmd = recognizer.recognize_wit(audio, key=WIT_AI_KEY)
			#print("Google Speech Recognition thinks you said " + self.cmd)
		self.interpret_speech()
		#except sr.UnknownValueError:
		#	self.cmd = 'SR Error'
		#except sr.RequestError as e:
		#	self.cmd = 'SR Error: ' + str(e)
		#	#print("Could not request results from Google Speech Recognition service; {0}".format(e))

	def stop_listening(self):
		self.stop_listening()

	def interpret_speech(self):
		#print('interpreter called')
		tokens = []
		self.cmd_lib = [
                        [['change', 'temperature'], 'self.change_temp_units()']
                        ,[['show', 'commands'], 'self.print_cmd_lib()']
                        ]        
		tokens = nltk.word_tokenize(self.cmd.lower())
		if tokens.count('mirror') >= 2:
			print('keyword found')
			self.cmdQueue.put('recognized')
			for command in self.cmd_lib:
				match = 1
				for cmdword in command[0]: 
					if cmdword in tokens:
						pass
					else: 
						match = 0
						break
				if match == 1:
					print('cmd found')
					self.cmdQueue.put('understood')
					self.cmdQueue.put(command[1])
					return
			
			self.cmdQueue.put('Interpret Error')
			return

class mirrorSprite(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg='black')
		self.bluesprite = Image.open("assets/icons/sound_blue.png")
		self.bluesprite = self.bluesprite.resize((50, 50), Image.ANTIALIAS)
		self.bluesprite = self.bluesprite.convert('L')
		
		self.redsprite = Image.open("assets/icons/sound_red.png")
		self.redsprite = self.redsprite.resize((50, 50), Image.ANTIALIAS)
		self.redsprite = self.redsprite.convert('L')
		
		self.greensprite = Image.open("assets/icons/sound_green.png")
		self.greensprite = self.greensprite.resize((50, 50), Image.ANTIALIAS)
		self.greensprite = self.greensprite.convert('L')
		
		self.blacksprite = Image.open("assets/icons/sound_black.png")
		self.blacksprite = self.blacksprite.resize((50, 50), Image.ANTIALIAS)
		self.blacksprite = self.blacksprite.convert('L')
		
		self.sprite = ImageTk.PhotoImage(self.blacksprite )
		self.iconLbl = Label(parent, bg='black')
		self.iconLbl.pack(side=TOP, anchor=CENTER)
		self.iconLbl.config(image=self.sprite)
		self.iconLbl.image = self.sprite
		
		self.flashing = 0
		self.color = 'blue'
	
	def _change_color(self, color='black'):
		if color == 'blue':
			self.sprite = ImageTk.PhotoImage(self.bluesprite)
			self.iconLbl.config(image=self.sprite)
			self.iconLbl.image = self.sprite
		elif color == 'red':
			self.sprite = ImageTk.PhotoImage(self.redprite)
			self.iconLbl.config(image=self.sprite)
			self.iconLbl.image = self.sprite
		elif color == 'green':
			self.sprite = ImageTk.PhotoImage(self.greensprite)
			self.iconLbl.config(image=self.sprite)
			self.iconLbl.image = self.sprite
		else:
			self.sprite = ImageTk.PhotoImage(self.blacksprite)
			self.iconLbl.config(image=self.sprite)
			self.iconLbl.image = self.sprite
	
	def _flash(self):
		while self.flashing == 1:
			self._change_color(self.color)
			self.after(200, self._change_color)
			self.after(200, self._flash)
	
	def start_flashing(self):
		self.flashing = 1
		self._flash()	
	
	def stop_flashing(self):
		self.flashing = 0
		self._change_color(self.color)
		
	def set_color(self, color='black'):
		self.color = color
		self._change_color(self.color)
	
	