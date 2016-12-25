from tkinter import *
import os
import datetime
import httplib2

# Google Calendar API imports
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'MirrorMirror'


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

		self.after(600000, self.get_events)


class CalendarEvent(Frame):
	def __init__(self, parent, event_name="Event 1", event_time='None'):
		Frame.__init__(self, parent, bg='black')
		self.eventName = event_time + ' ' + event_name
		self.eventNameLbl = Label(self, text=self.eventName, font=('Helvetica', 18), fg="white", bg="black")
		self.eventNameLbl.pack(side=TOP, anchor=E)
