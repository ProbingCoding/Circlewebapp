# Circle

### Video Demo: https://youtu.be/T7uSqnLAcjs

### A web-based application using JavaScript, Python, SQL, Flask, HTML/ CSS.

  Summary, features, and purpose. "Relation Media" - a no distraction spin on social media, with the focus on maintaining and nurturing your
  close circle of friends and family, your most meaningful relationships. Circle provides a communication platform outside of mainstream 
  social media, which is now very saturated with distracting and addictive entertainment. How then does Circle differ from simple texting and
  calling? Circle offers several functionalities developed to support and nurture your relationships. CANs (contact absence notifications) 
  are customisable reminders that your last communication with an added user is greater than x many weeks ago. Relationships can become very
  distant without your realisation. CANs are designed to support more frequent communication with friendly reminders. Calendar functionality
  is also integrated into Circle. Users can set calendar events with added users, promoting efforts towards relationships. Calendars also
  have reminder notifications built into the notification functionality. This feature is presented in a sticky note style; it is then as if
  users are literally organising their relationship efforts within the calendar page. Users' added contacts are separated by relation into
  friends or family to specifically promote family relation efforts, perhaps omitted by mainstream social media attentions. Users are then
  limited to 10 friend contacts and 10 family contacts as Circle is designed to nurture your closest, most meaningful relationships. This is
  something mainstream social media often does not focus attention towards. In fact, mainstream social media pushes care and attention 
  towards people you may have never even met before.


  My static files consist of CSS styling and Circle logo-related image files.

  My template files consist of 7 html files: a registration page, a login page, a homepage, a calendar page, a messages page, and a profile
  page. Registration and login files are very simple and very similar form submission pages, designed with UX in mind and Circle-related
  logos and design. The homepage file content consists of 3 sections: a description of the "beta development phase" of this app and a little
  about the purpose of the app, a "future ambitions" section detailing the intended future features and iOS app, and a feedback survey 
  section which will aid future developments. The messages file of course sets out the functionality for user messaging including message
  timestamps and unread message icons to highlight unopened/ unread messages. The calendar file is beautifully simple. It consists of a a 
  simple form for creating a calendar event with added users (title, time, contact). The back end then creates a sticky note with this data
  (aforementioned) and enables personal notes to add to the event and permanent movability of the sticky note. The reasoning behind this has
  been discussed. Finally, the profile file is the most detailed and interactable app page. First, the "Your Profile" section which
  details some standard user information and a "Delete Account" option (of course requiring verification). Next, the contacts section which
  is a rotatable circle holding interactable friend usernames and family usernames in opposites half of the rotatable circle. The idea is 
  that your contacts are in fact your circle. The next section, "curate circle", is empty until you click on a contact. Users are the 
  presented with some contact personalisation option, CAN customisation and displayed username customisation. Last, the "expand circle" 
  section, enabling user contact request submission, separated for family vs. friends.


  Helpers.py file. This file consists of several python functions, abstracting away some underlying code for the main app.py file.
  First, the timestamp formatter function plays an important role in UX, enabling timestamps for user activity and messaging to be displayed
  in a dynamic and readable form while simultaneously facilitating back-end processing of timestamps. The sis true of the date time formatter
  function, specifically tailoring for calendar event displays of dates and times. The contact recency checker function checks the most 
  recent timestamp with all user contacts every time the page refreshes/ the user logs in (the function is called from an app context 
  processor route in the app.py file). If the most recent contact with a user if greater than the given/ customised CAN period, the user 
  will receive the CAN notification to encourage contact. The last function in this file is the calendar notifier function. This is also 
  called from an app context processor route and will create a notification to remind users of a calendar event when said event is scheduled 
  within the coming 2 hours. This was, admittedly, a vague decision. I'm uncertain of the most useful timeframe for this function, but I 
  decided that 2 hours is enough notice such that a user can deal with any current tasks and find time to clear their calendar if they have 
  become busy/ forgotten the scheduled calendar event.


  Project.db file. My database consists of 9 tables: users, contacts, contact_requests, messages, notifications, feedback, calendar_events,
  deleted_calendar_events, and calendar_position_and_notation. Most notably, calendar_position_and_notation stores two rows of data for each
  calendar event, one for both of the users associated with the calendar event. This enables user independent customisation of calendar
  sticky note organisation (within the calendar page) and user independent notation for each event.


  Penultimately, the app.py file. This is the main back-end file and it handles the server-side logic and functionality of the app. It uses
  flask to define routes for different pages in the app; handle user requests (such as logging in and messaging); connect the database
  to store and retrieve data; manage server-side processes (such as user input validation, error handling, and updating notifications); and
  to send data to the front-end (for example calendar event input data) for client-side handling and display.


  Finally, a brief discussion on some design choices. First, the colour theme of black, gold, and silver represents the more classical values
  upon which the app is developed - meaningful family and relationship commitments. Overall, the design and app contents are reasonably 
  minimal, purposefully to project the easy-to-use and no-distraction approach to social media which Circle represents. And I suppose, 
  perhaps, the most notable design choice to discuss is the rotatable circle centred on the profile page. It's an engaging interactable 
  feature unique to this app, more engaging than generic scrolling lists.
