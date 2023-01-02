**!! This repo is under development !!**
# GMYI
GMYI can collect infected user's system data and analyze it for displaying pop-up ads on the desktop.
## TO-DO's
- [X] Convert every data collection function to Pandas DataFrame
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
./Scripts/Activate.ps1 #OR other scripts based on your shell
pip install -r ./requirements.txt
python -311 ./main.py 
```
## Test Cases And General Information About GMYI's Current State
This software only works on Windows PC's. It is not meant to be on other OS'es. 
And there is no malicious function that GMYI contains!! You can control all the steps that you want take. 

Current GMYI can get these information from Windows machine:
* Operating System (version, release, boot time)
* CPU information (Model, Max Clock Speed, etc.)
* Memory information (Total Capacity, Usage, etc.)
* External or Internal Disk information (Device name, Capacity, usage, total read/write, etc.)
* Network Information (Interfaces and their addresses, Up and running info, etc.)
* GPU information (Model, Load, temperature, Memory, etc.)
* System Language
* USB Info (Flash drives or USB ports information)
* Installed Programs and their versions
* Current CPU Usage (Core Percentages)
* Processes (Which programs running currently and how many resources are they consuming)

Most important parts are last two ones: Processes and CPU usage.

For using GMYI, you can use executable file or setup Python enviroment that explained [here.](https://github.com/ymozer/GMYI#test-cases-and-general-information-about-gmyis-current-state) 
Help page (`-h or --help` parameters) explains how to use GMYI. (Also contains cool logo ;) )
All you need to do make sure you are working on Python version 3.11 or above and run:
`python main.py` == `python main.py --help` == `python main.py -h`
OR
`main.exe -h`

When using `-w` ( or `--all_write`) and `-l` (or `--loop`) parameters, you MUST specify file format (txt, json, csv):
`python ./main.py -l json` or which of the third formats you want...

Differances between `-w` and `-l` is this: `-w` executes once and aborts. But `-l` runs continously until user interrupts (CTRL^C). With using these parameters, GMYI will create directories called "Results" and "Processes"."Results" will keep all the data collection function output files, including CPU usage. Proceses on the other hand, as the name suggests, only keep processes data.  

File export and software loop is the most important part of our software. Bugs and missing functionalities from these parts is crucial. So please report any missing parts or bugs.

## Flowchart
![Flowchart](/Media/GMYI_flowchart.png)
