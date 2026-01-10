# RBLXChatApp
Don't want to give your face to a billion dollar corporation being sued for using your data to train AI?
use this chat app

Chat will automatically find the server id, game and account that you're playing and connect you to any other players in the same server.

# How to Use
You will need a [highspeedtrain.net](https://highspeedtrain.net/account/create) account to use this.
Install (see below)
Open the .exe and sign in using your highspeedtrain.net account information
Join a Roblox game
Click "Attach"
Wait until the chat says "[Server]: Connected to WS"
You can then use chat as normal, type in the box, press enter to send message.
After leaving, press Unattach.

# Moderation
Currently, there is no chat filter.
However, slurs, hate speech, harrasment, homophobia, racism will not be tolerated.
Moderators will issue IP bans for those who partake in this behaviour.

# Installation
## Release
Download the latest release and double click
## Building from Source
I use pyinstaller to convert the Python script into an executable, make sure you have that installed
```
pip install pyinstaller
```
then, run
```
pyinstaller --onefile --noconsole  main.py
```

# FAQ
Q: Does this violate Roblox ToS?\n
A: No\n
Q: Does Roblox view this as an exploit?\n
A: No, all it does is read the logs (which are in %LOCALAPPDATA%\Roblox\logs\)\n
Q: UI is terrible im deleting this app\n
A: yes i know\n
Q: ew so slow python terrible rewrite in java/c++/assembly/machine code/transistors\n
A: shut up\n
Q: can i be mod/admin\n
A: no\n

# Contributing
This code is godawful since i was in a rush to make it, please do make PRs improving it.
Style guide:
use camelCase, not snake_case or i kill
no semicolons

# Discover a security vulnerability?
Please dont use issues, DM highspeedtrain on discord
