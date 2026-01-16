import customtkinter as ui
from CTkMessagebox import CTkMessagebox
from typing import Optional
import sys
import platform
import psutil
import os
import re
import requests
import asyncio
from gql import gql, Client
from gql.transport.websockets import WebsocketsTransport


jobId = None
placeId = None
universeId = None
userId = None
userName = None
playingGame: Optional[ui.StringVar] = None
chatInput: Optional[ui.CTkEntry] = None
root: Optional[ui.CTk] = None
isAttached = False
isDarkMode = True
transport = WebsocketsTransport(url="wss://fxdbjbvpegpmnrlqmvwc.hasura.eu-west-2.nhost.run/v1/graphql")
attachButton : Optional[ui.CTkButton] = None
unattachButton : Optional[ui.CTkButton] = None
darkModeButton : Optional[ui.CTkButton] = None
logoutButton : Optional[ui.CTkButton] = None
playingGameLabel : Optional[ui.CTkLabel] = None
messageScrollContainer : Optional[ui.CTkScrollableFrame] = None
mainContainer : Optional[ui.CTkFrame] = None
scrollbar : Optional[ui.CTkScrollbar] = None
needsToLogin = True
sessionKey : Optional[str] = None
usernameInput : Optional[ui.CTkEntry] = None
passwordInput : Optional[ui.CTkEntry] = None
appdata = os.path.join(os.environ.get("LOCALAPPDATA"), "RBLXChatApp") #type:ignore

NAME_COLOURS = [
"#FD2943",
"#01A2FF",
"#02B857",
"#6B0A7C",
"#DA8541",
"#F5D030",
"#E8BAC8",
"#D7C59A"
]

messageFunctionURL = "https://fxdbjbvpegpmnrlqmvwc.functions.eu-west-2.nhost.run/v1/message"

async def initRealtime():
    subscriptionQuery = gql("""
    subscription {
        messages(order_by: [{ created_at: desc }] limit: 1) {
            message_id
            job_id
            username
            message
            created_at
        }
    }
    """)
    
    async with Client(transport=transport, fetch_schema_from_transport=False) as session:
        async for result in session.subscribe(subscriptionQuery):
            if len(result["messages"]) == 0:
                continue
            
            if isAttached == False or result["messages"][0]["job_id"] != jobId:
                continue
            
            newMessage(f"[{result["messages"][0]["username"]}]: {result["messages"][0]["message"]}", True)
    
def getJobId():
    global placeId
    global jobId
    global universeId
    global playingGame
    global userId
    global isAttached
    global userName
    global sessionKey
    
    logDir = os.path.join(os.environ["LOCALAPPDATA"], "Roblox", "Logs")
    logFiles = []
    
    for file in os.listdir(logDir):
        if file.endswith("log") == False:
            continue
        
        logFiles.append(os.path.join(logDir, file))
        
    if len(logFiles) == 0:
        CTkMessagebox(title="Failed to Attach", message="No log files can be found.")
        return
    
    with open(max(logFiles, key=os.path.getmtime), "r", encoding="utf-8") as file:
        logContent = file.read()
        
    jobIdMatches = re.findall(r"\[FLog::Output\] ! Joining game '(.+?)'", logContent)
    placeIdMatches = re.findall(r"placeid:([^\s,]+)", logContent)
    universeIdMatches = re.findall(r"universeid:([^\s,]+)", logContent)
    userIdMathces = re.findall(r"userid:([^\s,]+)", logContent)
    
    if len(jobIdMatches) == 0:
        CTkMessagebox(title="Failed to Attach", message="Couldn't find JobId in the log file. If Roblox has just started, please wait a moment before trying again.")
        return
    
    if len(placeIdMatches) == 0:
        CTkMessagebox(title="Failed to Attach", message="Couldn't find PlaceId in the log file. If Roblox has just started, please wait a moment before trying again.")
        return
    
    if len(universeIdMatches) == 0:
        CTkMessagebox(title="Failed to Attach", message="Couldn't find UniverseId in the log file. If Roblox has just started, please wait a moment before trying again.")
        return
    
    if len(userIdMathces) == 0:
        CTkMessagebox(title="Failed to Attach", message="Couldn't find UserId in the log file. If Roblox has just started, please wait a moment before trying again.")
        return
    
    for AjobId in jobIdMatches:
        jobId = AjobId
        
    for AplaceId in placeIdMatches:
        placeId = AplaceId
        
    for AUniverseId in universeIdMatches:
        universeId = AUniverseId
    
    for AUserId in userIdMathces:
        userId = AUserId

    newMessage(f"logfile read success", False)
    newMessage(f"jobid: {jobId}", False)
    newMessage(f"placeid: {placeId}", False)
    Response = requests.post(f"https://highspeedtrain.net/api/rblx/GetGameInfo", json={"placeIds": [placeId]}, headers=({"Accept": "application/json"}))
    if Response.status_code != 200:
        CTkMessagebox(title="Failed to Attach", message=f"Cant get info on game u prlaying: stat code {Response.status_code}")
        jobId = None
        placeId = None
        universeId = None
        return
    
    newMessage("loaded game info", False)
    
    UserInfo = requests.get(f"https://users.roblox.com/v1/users/{userId}")
    if UserInfo.status_code != 200:
        CTkMessagebox(title="Failed to Attach", message=f"Cant get info on your accoun: {UserInfo.status_code}")
        jobId = None
        placeId = None
        universeId = None
        return
    newMessage("loaded user info", False)
    
    ResponseData = Response.json()
    UserInfoData = UserInfo.json()
    if playingGame is None:
        return
    playingGame.set(f"Playing {ResponseData["data"][0]["name"]} by {ResponseData["data"][0]["builder"]}")
    userName = UserInfoData["name"]

    requests.post(messageFunctionURL, json={"job_id": jobId, "sessionKey": sessionKey, "message": f"{userName} has joined"})
    newMessage("[Server]: Welcome to RBLXChat! Please keep things respectful.", False)
    newMessage("[Server]: Harrassment, homophobia, racism etc is not allowed.", False)
    isAttached = True
    
def onUnattachClicked():
    global jobId
    global placeId
    global universeId
    global userName
    global isAttached
    
    if isAttached == False:
        CTkMessagebox(title="Failed to Unattach", message="Not attached")
        return
    
    newMessage("unattaching", False)
    
    if playingGame is None:
        return
    
    playingGame.set("Not playing anything")
    jobId = None
    placeId = None
    universeId = None
    userName = None
    isAttached = False

def onAttachClicked():
    global isAttached
    if isAttached:
        CTkMessagebox(title="Failed to Attach", message="Already attached")
        return
    
    didFindRBLXProcess = False
    for process in psutil.process_iter(["name"]):
        if process.info["name"] == "RobloxPlayerBeta.exe":
            didFindRBLXProcess = True
            
    if didFindRBLXProcess == False:
        CTkMessagebox(title="Failed to Attach", message="Roblox is not running!")
        return
        
    getJobId()
    
def onMessageClicked(*args):
    if chatInput is None:
        return
    chatInput.delete(0, "end")
    
def onMessageLeft(*args):
    if chatInput is None or root is None:
        return
    chatInput.delete(0, "end")
    chatInput.insert(0, "Enter message here") 
    root.focus()
    
def onReturn(*args):
    global userName
    
    if root is None or chatInput is None:
        return
    root.focus()
    
    if jobId is None:
        CTkMessagebox(title="Failed to Send Message", message=f"You are not playing anything")
        return
    
    Result = requests.post(messageFunctionURL, json={"job_id": jobId, "sessionKey": sessionKey, "message": chatInput.get()})
    if Result.status_code == 200:
        return
    
    if Result.status_code == 429:
        CTkMessagebox(title="Failed to Send Message", message=f"why are you sending so many messages")
        return
    elif Result.status_code == 500:
        CTkMessagebox(title="Failed to Send Message", message=f"internal server error, please dm highspeedtrain with info")
        return
    elif Result.status_code == 400:
        CTkMessagebox(title="Failed to Send Message", message=f"message was more than 300 characters, please split up message")
        return
    elif Result.status_code == 401:
        CTkMessagebox(title="Failed to Send Message", message=f"authentication failed, please restart the client")
    else:
        CTkMessagebox(title="wtf", message=f"unknown error {Result.status_code}")
        
def getNameColour(name):
    value = 0
    for index in range(len(name)):
        cValue = ord(name[index])
        reverseIndex = len(name) - index
        
        if len(name) % 2 == 1:
            reverseIndex -= 1

        if reverseIndex % 4 >= 2:
            cValue = -cValue
            
        value += cValue
    
    return value

def computeNameColour(name):
    return NAME_COLOURS[(getNameColour(name) + 0) % len(NAME_COLOURS)]
    
def newMessage(message, wasChat):
    global isDarkMode
    
    if messageScrollContainer is None:
        return
    
    text = ui.CTkTextbox(messageScrollContainer, height=1, wrap="word")
    text.pack(pady=2, padx=2, fill="x")
    text.insert("end", message)
    text.configure(state="disabled")
    
    if wasChat:
        text.tag_add("highlight", f"1.{0}", f"1.{len(message[1:message.index(":")])+1}")
        text.tag_config("highlight", foreground=computeNameColour(re.search(r"\[(.*?)\]:", message).group(1))) # type: ignore
    
    messageScrollContainer.update_idletasks()
    messageScrollContainer._parent_canvas.yview_moveto(1)
    
def toggleUImODE():
    global isDarkMode
    
    if isDarkMode:
        isDarkMode = False
        ui.set_default_color_theme("green")
    else:
        isDarkMode = True
        ui.set_default_color_theme("blue")

def onSignInClicked():
    global needsToLogin
    global usernameInput
    global passwordInput
    global sessionKey
    
    if passwordInput is None or usernameInput is None:
        return
    
    response = requests.post("https://highspeedtrain.net/api/auth/authorise", headers={"Content-Type": "application/json"}, json={"Action": "Login", "Username": usernameInput.get(), "Password": passwordInput.get()})
    data = response.json()

    if response.status_code == 200:
        sessionKey = data["data"]["sessionKey"]
        needsToLogin = False
        CTkMessagebox(title="Signed In", message=f"Signed in as {data["data"]["username"]}")
        with open(os.path.join(appdata, "info.txt"), "w") as file:
            file.write(f"sessionkey:{sessionKey}\n")
            file.write(f"username:{usernameInput.get()}\n")
            file.write(f"password:{passwordInput.get()}")
        return
    
    if response.status_code == 400:
        CTkMessagebox(title="Login Error", message="Username and password are required")
    elif data["message"] == "Invalid username":
        CTkMessagebox(title="Login Error", message="Invalid username")
    elif data["message"] == "Invalid password":
        CTkMessagebox(title="Login Error", message="Invalid password")
    elif response.status_code == 500:
        CTkMessagebox(title="Login Error", message="An internal server error occured. Please try again.")
    elif response.status_code == 429:
        CTkMessagebox(title="Login Error", message="You have attempted to login too many times. Please wait a minute before retrying.")
    else:
        CTkMessagebox(title="Login Error", message=f"an unknown error happened while logging in. please create an issue with this message: LogInHttpError-{response.status_code}-{data["message"]}")
        
        
def onSignOutClicked():
    global needsToLogin
    global appdata
    global sessionKey
    
    needsToLogin = True
    
    requests.post("https://highspeedtrain.net/api/auth/authorise", headers={"Content-Type": "application/json"}, json={"Action": "Logout", "SessionKey": sessionKey})
    sessionKey = None
    
    os.remove(os.path.join(appdata, "info.txt"))
    onUnattachClicked()
    sys.exit(0)

def initUi(loop):
    global playingGame
    global chatInput
    global root
    global attachButton
    global unattachButton
    global darkModeButton
    global playingGameLabel
    global messageScrollContainer
    global mainContainer
    global usernameInput
    global passwordInput
    global appdata
    global sessionKey
    global needsToLogin
    global logoutButton
    
    os.makedirs(appdata, exist_ok=True)
    
    exsistingUsername = None
    existingPassword = None
    existingSessionKey = None
    
    if os.path.exists(os.path.join(appdata, "info.txt")):
        with open(os.path.join(appdata, "info.txt"), "r") as file:
            for line in file:
                line = line.strip()
                lineSplitted = line.split(":", 1)
                if lineSplitted[0] == "username":
                    exsistingUsername = lineSplitted[1]
                elif lineSplitted[0] == "password":
                    existingPassword = lineSplitted[1]
                elif lineSplitted[0] == "sessionkey":
                    existingSessionKey = lineSplitted[1]
    
    root = ui.CTk()
    ui.set_widget_scaling(1.0)
    ui.set_window_scaling(1.0)
    root.title("RBLXChatApp")
    root.geometry(f"{500}x{300}")
    root.resizable(True, True)
    root.attributes("-topmost", True)
    
    loginContainer = ui.CTkFrame(root, height=root.winfo_height(), width=root.winfo_width())
    
    signInLabel = ui.CTkLabel(loginContainer, text="Sign In With Your highspeedtrain.net Account")
    usernameInput = ui.CTkEntry(loginContainer)
    passwordInput = ui.CTkEntry(loginContainer)
    signInButton = ui.CTkButton(loginContainer, text="Sign In", command=onSignInClicked)
    
    mainContainer = ui.CTkFrame(root, height=root.winfo_height(), width=root.winfo_width())
    
    playingGame = ui.StringVar(value="Not playing anything")

    attachButton = ui.CTkButton(mainContainer, text="Attach", command=onAttachClicked)
    attachButton.place(x=mainContainer.winfo_width()-10, y=10, anchor="ne")
    
    unattachButton = ui.CTkButton(mainContainer, text="Unattach", command=onUnattachClicked)
    unattachButton.place(x=mainContainer.winfo_width()-10, y=10, anchor="ne")
    
    darkModeButton = ui.CTkButton(mainContainer, text="Light", command=toggleUImODE)
    darkModeButton.place(x=mainContainer.winfo_width()-10, y=10, anchor="ne")
    
    logoutButton = ui.CTkButton(mainContainer, text="Logout", command=onSignOutClicked)
    
    playingGameLabel = ui.CTkLabel(mainContainer, textvariable=playingGame)
    playingGameLabel.place(x=10, y = 5, anchor = "nw")
    
    chatInput = ui.CTkEntry(mainContainer, width=root.winfo_width()-20)
    chatInput.place(relx=0.5, y=mainContainer.winfo_height()-10, anchor="s")
    chatInput.bind("<FocusIn>", onMessageClicked)
    chatInput.bind("<FocusOut>", onMessageLeft)
    chatInput.bind("<Return>", onReturn)
    chatInput.insert(0, "Enter message here")
    
    messageScrollContainer = ui.CTkScrollableFrame(mainContainer) #type: ignore god i hate customtkinter
    
    def updatePosition():
        if root is None or usernameInput is None or passwordInput is None or mainContainer is None or chatInput is None or attachButton is None or unattachButton is None or darkModeButton is None or messageScrollContainer is None or logoutButton is None:
            return
        
        if needsToLogin:
            loginContainer.configure(height=root.winfo_height(), width=root.winfo_width())
            loginContainer.place(relwidth=1, relheight=1)
            signInLabel.place(x=10, y=10)
            usernameInput.place(x=10, y=40)
            usernameInput.configure(width=200, height=25)
            passwordInput.place(x=10, y=75)
            passwordInput.configure(width=200, height=25)
            signInButton.place(x=10, y=105)
            loop.call_soon(loop.stop)
            loop.run_forever()
            root.after(100, updatePosition)
            return
        
        mainContainer.place(relwidth=1, relheight=1)
        mainContainer.configure(width=root.winfo_width(), height=root.winfo_height())
        attachButton.place(x=mainContainer.winfo_width()-10, y=10, anchor="ne")
        attachButton.configure(width=65)
        unattachButton.place(x=mainContainer.winfo_width()-10, y=40, anchor="ne")
        unattachButton.configure(width=65)
        darkModeButton.place(x=mainContainer.winfo_width()-10, y=70, anchor="ne")
        darkModeButton.configure(width=65)
        logoutButton.place(x=mainContainer.winfo_width()-10, y=100, anchor="ne")
        logoutButton.configure(width=65)
        chatInput.place(relx=0.5, y=mainContainer.winfo_height()-10, anchor="s")
        chatInput.configure(width=mainContainer.winfo_width()-20)
        messageScrollContainer.place(x=10, y=35)
        messageScrollContainer.configure(width=mainContainer.winfo_width()-115, height=mainContainer.winfo_height()-90)
        messageScrollContainer._scrollbar.configure(height=0)
        loop.call_soon(loop.stop)
        loop.run_forever()
        root.after(100, updatePosition)
        
    if existingSessionKey is not None and exsistingUsername is not None and existingPassword is not None:
        sessionKey = existingSessionKey
        needsToLogin = False
    
    root.after(100, updatePosition)
    root.mainloop()

if __name__ != "__main__":
    print("dont run as module")
    sys.exit(1)

if platform.system() != "Windows":
    print("rblxhcatapp only supports windos")
    sys.exit(1)
    
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(initRealtime())
initUi(loop)