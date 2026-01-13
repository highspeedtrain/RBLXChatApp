# RBLXChatApp
Don't want to give your face to a billion dollar corporation being sued for using your data to train AI?
use this chat app

Chat will automatically find the server id, game and account that you're playing and connect you to any other players in the same server.

# How to Use
You will need a [highspeedtrain.net](https://highspeedtrain.net/account/create) account to use this.
By using the services, you agree to the [highspeedtrain.net Terms of Use](https://highspeedtrain.net/about)<br>
Install (see below)<br>
Open the .exe and sign in using your highspeedtrain.net account information<br>
Join a Roblox game<br>
Click "Attach"<br>
Wait until the chat says "[Server]: Connected to WS"<br>
You can then use chat as normal, type in the box, press enter to send message.<br>
After leaving, press Unattach.<br>

# Moderation
Currently, there is no chat filter.<br>
However, slurs, hate speech, harrasment, homophobia, racism will not be tolerated.<br>
Moderators will issue IP bans for those who partake in this behaviour.<br>

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
Q: Does this violate Roblox ToS?<br>
A: No<br>
Q: Does Roblox view this as an exploit?<br>
A: No, all it does is read the logs (which are in %LOCALAPPDATA%\Roblox\logs\)<br>
Q: UI is terrible im deleting this app<br>
A: yes i know<br>
Q: ew so slow python terrible rewrite in java/c++/assembly/machine code/transistors<br>
A: shut up<br>
Q: can i be mod/admin<br>
A: no<br>

# Contributing
This code is godawful since i was in a rush to make it, please do make PRs improving it.
Style guide:
use camelCase, not snake_case or i kill
no semicolons

# Discover a security vulnerability?
Please dont use issues, DM highspeedtrain on discord
