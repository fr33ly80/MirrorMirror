# -*- coding: utf-8 -*-
"""
Created on Sat Dec 24 11:46:15 2016

@author: brend
"""

import threading
import speech_recognition as sr
import nltk
import queue

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
		try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
			self.cmd = recognizer.recognize_google(audio)
			#print("Google Speech Recognition thinks you said " + self.cmd)
			self.interpret_speech()
		except sr.UnknownValueError:
			self.cmd = 'SR Error'
		except sr.RequestError as e:
			self.cmd = 'SR Error: ' + e
			#print("Could not request results from Google Speech Recognition service; {0}".format(e))

	def stop_listening(self):
		self.stop_listening()

	def interpret_speech(self):
		print('interpreter called')
		self.cmd_lib = [
                        [['change', 'temperature'], 'self.change_temp_units()']
                        ,[['show', 'commands'], 'self.print_cmd_lib()']
                        ]        
		tokens = nltk.word_tokenize(self.cmd.lower())
		if tokens.count('mirror') >= 2:
			print('keyword heard')
			for command in self.cmd_lib:
				for cmdword in command[0]: 
					if cmdword in tokens:
						pass
					else: 
						break
				print('cmd_detected')
				self.cmdQueue.put(command[1])
				return
			
			self.cmdQueue.put('Interpret Error')