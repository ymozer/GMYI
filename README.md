**!! This repo is under development !!**
# GMYI
GMYI can collect infected user's system data and analyze it for displaying pop-up ads on the desktop.
## TO-DO's
- [ ] Convert every data collection function to Pandas DataFrame
- [x] Command line flags for running certain functions.
- [ ] Get browser data (Edge, Chrome, Chromium, Firefox, Opera)
  - [ ] Cookies
  - [ ] Passwords ??
  - [ ] History   
- [ ] Test GMYI on other systems.
- [x] USB devices information function
- [ ] Screenshot/Recording ability as well as access to microphone and camera.
- [ ] Keylogger ability
- [x] Make requirement.txt.
- [x] Make an executable.
- [ ] Make a database that will store infected system's information.
- [ ] Make a webserver for receiving information from infected systems.
- [ ] Analyze "user types" according to collected data.
- [ ] Implement the pop-up window on desktop for displaying personalized advertisement.
- [ ] Reverse shell to infected Windows computer.
- [ ] Obfuscation
- [ ] ...

## How to Spread/Run GMYI ??
GMYI can sit on some website that can downloaded and executed by rubber ducky script.
* Rubber Ducky
* Social Engineering (e-mail)
* ??

## Development
Python version >= 3.11

```bash
python -m venv .
pip install -r ./requirements.txt
```

## Flowchart
![Flowchart](/Media/GMYI_flowchart.png)
