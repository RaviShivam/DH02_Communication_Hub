# Communication Hub for Delft Hyperloop 2018
All code used during the mission can be found in the following files: <br>
* `messengers_ch.py`: This contains all the messengers capable of communicating with the mission control, SpaceX and the Hercules board. It also contains the loggers capable of logging at various frequencies.
* `main.py`: This file is the main module which links all the messengers from `messengers_ch.py`. This is the file that will be run during the mission.
* `mission_configs.py`: Contains all contant configuration of the mission including the necessary pins, packets, ip adress etc. This the only file that is allowed to be adjusted (for any minor changes) after complete functional testing of the code. 
