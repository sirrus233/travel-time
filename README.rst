Travel Time
-----------
This app was originally designed to help me figure out when to leave the office at a time when I had a particularly variable 
commute. It continually polls live traffic data and reports on the current travel time between work and home. This can be
useful when set to pop up around the end of the work day.

Requirements
============
TravelTime installs with Poetry and requires a Google Maps API key with permissions to query the Directions API.

Installation
============
Clone the repository and run ``poetry install``.

Configuration
============
TravelTime needs some configuration to work properly. In the ``config/config.json`` file, you should pre-populate the empty strings
for your work and home address, as well as fill in your Google Maps API key. You can also optionally adjust your preferred
working hours. The changes will be picked up the next time the app starts.

When outside of working hours, the TravelTime app will stop actually telling time, and simply tell you to GO HOME!
