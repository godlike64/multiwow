# multiwow
A WoW multibox tool for Linux &amp; Xorg.

This is a Python tool I developed in order to be able to multibox WoW on Linux, out of my desire not to go back to Windows (10 years and counting!). It is not yet complete, but it is in a state where it can be used.

I have been using it for a 2-char setup, but there is nothing preventing the code from working on a 3-or-more multibox setup already.

## Requirements

- Requires both the *xdotool* and *xwininfo* commands as external dependencies.
- Requires Python 3 (tested and developed with 3.6+).
- Requires the *pynput* Python package.
- It likely does not (and will not) work under Wayland.
- Requires WoW to be running under wine in a virtual desktop mode, not normal mode.

The last point is essential. The program will not run properly if WoW is not run in this way. The virtual desktop mode consists essentially of calling wine like so:

~~~
$ /path/to/wine explorer /desktop="name","WxH" 
~~~

where "name" is the virtual desktop name, and "WxH"is the resolution.

## Getting started

At the moment the script must be run from the project directory, in a suitable virtualenv with all requirements installed, e.g.:

~~~
$ git clone https://github.com/godlike64/multiwow.git
$ cd multiwow
$ virtualenv -p python3.6 ~/venv/
$ source ~/venv/bin/activate
$ pip install -r requirements.txt
~~~

Running and installing the program will get prettier once I finish all the packaging and things left to do.

Note that unfortunately I cannot help with issues installing the requirements, especially *xdotool* and *xwininfo*, as well as setup issues unrelated to the tool (such as running in Xorg instead of Wayland), or help getting WoW up and running. I am assuming you are a grown up and have already set everything up :).

## Usage

As previously explained, running and installing the program will eventually be friendlier. For the moment, it can be run via:

~~~
$ cd multiwow/src
$ PYTHONPATH="." ./bin/multi-wow.py
~~~

A default configuration file is created at ~/.config/multiwow.conf. There are two sections, each with their own settings:

- Keys: configures keystrokes for different actions.
    - start broadcast: start sending all keyboard/mouse events to slave windows.
    - stop broadcast: stop sending all keyboard/mouse events to slave windows
    - stop program: stop this program cleanly.
    - next window: focus on the next WoW window (like Alt+Tab, but only for the detected WoW windows).
- Commands: configures commands and parameters necessary for identifying/interacting with windows.
    - window ids: the command used to find out the relevant window IDs. See below.
    - master window: the wine **virtual desktop** name pattern of the master window (i.e. the one which you will keep focused most of the time).
    - slave windows: the wine **virtual desktop** name pattern of the slave windows (i.e. the ones which you will only focus to execute a specific action manually on that character alone).

Some further clarification on the config options:

- window ids: this command currently works on my setup, but I have not tested it extensively and it might need some more parametrization. It is tied to the output of xwininfo. If you have some shell knowledge, you know what it does. This command is needed for two things:
    1. Finding out the window IDs of the virtual desktops themselves. This is used for handling focus events properly.
    2. Finding out the window IDs of the actual WoW windows inside the virtual desktop. This is used for keyboard/mouse events.
- master/slave window/s: this is a name pattern. All my wine virtual desktops start with the pattern described here. e.g. I have one 'master_wow' VD and one (or many) 'wow_N' VDs, where N is simply a number but can be anything. Pattern matching works because *xdotool search* will match the name if it contains that pattern. You should ensure that no other windows in your session match this pattern, as it **will** cause issues.

## Issues

Currently, the only outstanding issue I found while in my testing, is due to NumLock being configured by default for auto-running. Sometimes when a key event is sent, the numlock state also gets picked up and the character might start running on its own. To fix this, I simply unbound NumLock from the keybindings (I use a different keybinding for auto-running anyway).

## Contributing

All help to improve this tool is of course welcome. If you spot a problem, open an issue. If you think you can contribute some code, feel free to submit a pull request.

Note that this is done on my free time, as work and life allows, so it might take me some time to tend to things.

## TODO

A lot of things. Seriously, a lot. So many that I can't write them down just yet.

## Authors

* [Juan Manuel Santos (godlike)](https://github.com/godlike64)

## License

This project is licensed under the [GPLv3 license](https://choosealicense.com/licenses/gpl-3.0/).