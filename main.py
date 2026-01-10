import tkinter as ui
from tkinter import messagebox, font
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
chatInput: Optional[ui.Entry] = None
root: Optional[ui.Tk] = None
messageCanvas: Optional[ui.Canvas] = None
messageContainer: Optional[ui.Frame] = None
isAttached = False
isDarkMode = False
transport = WebsocketsTransport(url="wss://fxdbjbvpegpmnrlqmvwc.hasura.eu-west-2.nhost.run/v1/graphql")
attachButton : Optional[ui.Button] = None
unattachButton : Optional[ui.Button] = None
darkModeButton : Optional[ui.Button] = None
logoutButton : Optional[ui.Button] = None
playingGameLabel : Optional[ui.Label] = None
messageScrollContainer : Optional[ui.Frame] = None
mainContainer : Optional[ui.Frame] = None
scrollbar : Optional[ui.Scrollbar] = None
needsToLogin = True
sessionKey : Optional[str] = None
usernameInput : Optional[ui.Entry] = None
passwordInput : Optional[ui.Entry] = None
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
        messagebox.showinfo("Failed to Attach", "No log files can be found.")
        return
    
    with open(max(logFiles, key=os.path.getmtime), "r", encoding="utf-8") as file:
        logContent = file.read()
        
    jobIdMatches = re.findall(r"\[FLog::Output\] ! Joining game '(.+?)'", logContent)
    placeIdMatches = re.findall(r"placeid:([^\s,]+)", logContent)
    universeIdMatches = re.findall(r"universeid:([^\s,]+)", logContent)
    userIdMathces = re.findall(r"userid:([^\s,]+)", logContent)
    
    if len(jobIdMatches) == 0:
        messagebox.showinfo("Failed to Attach", "Couldn't find JobId in the log file. If Roblox has just started, please wait a moment before trying again.")
        return
    
    if len(placeIdMatches) == 0:
        messagebox.showinfo("Failed to Attach", "Couldn't find PlaceId in the log file. If Roblox has just started, please wait a moment before trying again.")
        return
    
    if len(universeIdMatches) == 0:
        messagebox.showinfo("Failed to Attach", "Couldn't find UniverseId in the log file. If Roblox has just started, please wait a moment before trying again.")
        return
    
    if len(userIdMathces) == 0:
        messagebox.showinfo("Failed to Attach", "Couldn't find UserId in the log file. If Roblox has just started, please wait a moment before trying again.")
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
        messagebox.showinfo("Failed to Attach", f"Cant get info on game u prlaying: stat code {Response.status_code}")
        jobId = None
        placeId = None
        universeId = None
        return
    
    newMessage("loaded game info", False)
    
    UserInfo = requests.get(f"https://users.roblox.com/v1/users/{userId}")
    if UserInfo.status_code != 200:
        messagebox.showinfo("Failed to Attach", f"Cant get info on your accoun: {UserInfo.status_code}")
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
        messagebox.showinfo("Failed to Unattach", "Not attached")
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
        messagebox.showinfo("Failed to Attach", "Already attached")
        return
    
    didFindRBLXProcess = False
    for process in psutil.process_iter(["name"]):
        if process.info["name"] == "RobloxPlayerBeta.exe":
            didFindRBLXProcess = True
            
    if didFindRBLXProcess == False:
        messagebox.showinfo("Failed to Attach", "Roblox is not running!")
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
        messagebox.showinfo("Failed to Send Message", f"You are not playing anything")
        return
    
    Result = requests.post(messageFunctionURL, json={"job_id": jobId, "sessionKey": sessionKey, "message": chatInput.get()})
    if Result.status_code == 200:
        return
    
    if Result.status_code == 429:
        messagebox.showinfo("Failed to Send Message", f"why are you sending so many messages")
        return
    elif Result.status_code == 500:
        messagebox.showinfo("Failed to Send Message", f"internal server error, please dm highspeedtrain with info")
        return
    elif Result.status_code == 400:
        messagebox.showinfo("Failed to Send Message", f"message was more than 300 characters, please split up message")
        return
    elif Result.status_code == 401:
        messagebox.showinfo("Failed to Send Message", f"authentication failed, please restart the client")
    else:
        messagebox.showinfo("wtf", f"unknown error {Result.status_code}")
        
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
    
    if messageCanvas is None or root is None:
        return
    
    text = ui.Text(messageContainer, height=1, wrap="word", bg="#f0f0f0", borderwidth=0, font=font.nametofont("TkDefaultFont"))
    if isDarkMode:
        text.config(bg="#323232", fg="white")
    text.pack(pady=2, padx=2, fill="x")
    text.insert("end", message)
    text.configure(state="disabled")
    
    if wasChat:
        text.tag_add("highlight", f"1.{0}", f"1.{len(message[1:message.index(":")])+1}")
        text.tag_config("highlight", foreground=computeNameColour(re.search(r"\[(.*?)\]:", message).group(1))) # type: ignore
    
    messageCanvas.update_idletasks()
    
def toggleUiMode():
    if mainContainer is None or logoutButton is None or messageContainer is None or attachButton is None or unattachButton is None or darkModeButton is None or playingGameLabel is None or chatInput is None or messageCanvas is None or messageScrollContainer is None or scrollbar is None:
        return
    
    global isDarkMode
    
    isDarkMode = not isDarkMode
    if isDarkMode:
        mainContainer.config(bg="#323232")
        messageContainer.config(bg="#323232")
        attachButton.config(bg="#111111", fg="white")
        unattachButton.config(bg="#111111", fg="white")
        darkModeButton.config(bg="#111111", fg="white", text="Light")
        logoutButton.config(bg="#111111", fg="white")
        playingGameLabel.config(bg="#323232", fg="white")
        chatInput.config(bg="#111111", fg="white")
        messageCanvas.config(bg="#323232")
        messageScrollContainer.config(bg="#323232")
        scrollbar.config(troughcolor="#323232")
        
        for child in messageContainer.winfo_children():
            child.configure(bg="#323232", fg="white") # type: ignore
    else:
        mainContainer.config(bg="#f0f0f0")
        messageContainer.config(bg="white")
        attachButton.config(bg="white", fg="black")
        unattachButton.config(bg="white", fg="black")
        logoutButton.config(bg="white", fg="black")
        darkModeButton.config(bg="white", fg="black", text="Dark")
        playingGameLabel.config(bg="#f0f0f0", fg="black")
        chatInput.config(bg="white", fg="black")
        messageCanvas.config(bg="#f0f0f0")
        messageScrollContainer.config(bg="#f0f0f0")
        scrollbar.config(bg="#f0f0f0")
        for child in messageContainer.winfo_children():
            child.configure(bg="#f0f0f0", fg="black", height=1, borderwidth=0) # type: ignore

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
        messagebox.showinfo("Signed In", f"Signed in as {data["data"]["username"]}")
        with open(os.path.join(appdata, "info.txt"), "w") as file:
            file.write(f"sessionkey:{sessionKey}\n")
            file.write(f"username:{usernameInput.get()}\n")
            file.write(f"password:{passwordInput.get()}")
        return
    
    if response.status_code == 400:
        messagebox.showerror("Login Error", "Username and password are required")
    elif data["message"] == "Invalid username":
        messagebox.showerror("Login Error", "Invalid username")
    elif data["message"] == "Invalid password":
        messagebox.showerror("Login Error", "Invalid password")
    elif response.status_code == 500:
        messagebox.showerror("Login Error", "An internal server error occured. Please try again.")
    elif response.status_code == 429:
        messagebox.showerror("Login Error", "You have attempted to login too many times. Please wait a minute before retrying.")
    else:
        messagebox.showerror("Login Error", f"an unknown error happened while logging in. please create an issue with this message: LogInHttpError-{response.status_code}-{data["message"]}")
        
def onSignOutClicked():
    global needsToLogin
    global appdata
    global sessionKey
    
    needsToLogin = True
    
    requests.post("https://highspeedtrain.net/api/auth/authorise", headers={"Content-Type": "application/json"}, json={"Action": "Logout", "SessionKey": sessionKey})
    sessionKey = None
    
    os.remove(os.path.join(appdata, "info.txt"))
    onUnattachClicked()

def initUi(loop):
    global playingGame
    global chatInput
    global root
    global messageCanvas
    global messageContainer
    global attachButton
    global unattachButton
    global darkModeButton
    global playingGameLabel
    global messageScrollContainer
    global scrollbar
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
    
    root = ui.Tk()
    root.title("RBLXChatApp")
    root.geometry(f"{500}x{300}")
    root.resizable(True, True)
    root.attributes("-topmost", True)
    
    loginContainer = ui.Frame(root, height=root.winfo_height(), width=root.winfo_width())
    
    signInLabel = ui.Label(loginContainer, text="Sign In With Your highspeedtrain.net Account")
    usernameInput = ui.Entry(loginContainer, bg="white")
    passwordInput = ui.Entry(loginContainer, bg="white")
    signInButton = ui.Button(loginContainer, text="Sign In", command=onSignInClicked)
    
    mainContainer = ui.Frame(root, height=root.winfo_height(), width=root.winfo_width())
    
    playingGame = ui.StringVar(value="Not playing anything")

    attachButton = ui.Button(mainContainer, text="Attach", command=onAttachClicked)
    attachButton.place(x=mainContainer.winfo_width()-10, y=10, anchor="ne")
    
    unattachButton = ui.Button(mainContainer, text="Unattach", command=onUnattachClicked)
    unattachButton.place(x=mainContainer.winfo_width()-10, y=10, anchor="ne")
    
    darkModeButton = ui.Button(mainContainer, text="Dark", command=toggleUiMode)
    darkModeButton.place(x=mainContainer.winfo_width()-10, y=10, anchor="ne")
    
    logoutButton = ui.Button(mainContainer, text="Logout", command=onSignOutClicked)
    
    playingGameLabel = ui.Label(mainContainer, textvariable=playingGame)
    playingGameLabel.place(x=10, y = 10, anchor = "nw")
    
    chatInput = ui.Entry(mainContainer)
    chatInput.place(relx=0.5, y=mainContainer.winfo_height()-10, anchor="s", width=root.winfo_width()-20)
    chatInput.bind("<FocusIn>", onMessageClicked)
    chatInput.bind("<FocusOut>", onMessageLeft)
    chatInput.bind("<Return>", onReturn)
    chatInput.insert(0, "Enter message here")
    
    messageScrollContainer = ui.Frame(mainContainer, borderwidth=1, relief="solid", bg="white")
    
    messageCanvas = ui.Canvas(messageScrollContainer)
    scrollbar = ui.Scrollbar(messageScrollContainer, orient="vertical", command=messageCanvas.yview)
    messageCanvas.config(yscrollcommand=scrollbar.set)
    
    messageCanvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    messageContainer = ui.Frame(messageCanvas)
    window = messageCanvas.create_window((0, 0), window=messageContainer, anchor="nw")
    
    def updatePosition():
        if root is None or usernameInput is None or passwordInput is None or mainContainer is None or chatInput is None or messageCanvas is None or attachButton is None or unattachButton is None or darkModeButton is None or messageScrollContainer is None or logoutButton is None:
            return
        
        if needsToLogin:
            loginContainer.place(height=root.winfo_height(), width=root.winfo_width())
            signInLabel.place(x=10, y=10)
            usernameInput.place(x=10, y=40, width=200, height=25)
            passwordInput.place(x=10, y=75, width=200, height=25)
            signInButton.place(x=10, y=105)
            loop.call_soon(loop.stop)
            loop.run_forever()
            root.after(100, updatePosition)
            return
        
        mainContainer.place(width=root.winfo_width(), height=root.winfo_height())
        attachButton.place(x=mainContainer.winfo_width()-10, y=10, anchor="ne", width=55)
        unattachButton.place(x=mainContainer.winfo_width()-10, y=40, anchor="ne", width=55)
        darkModeButton.place(x=mainContainer.winfo_width()-10, y=70, anchor="ne", width=55)
        logoutButton.place(x=mainContainer.winfo_width()-10, y=100, anchor="ne", width=55)
        chatInput.place(relx=0.5, y=mainContainer.winfo_height()-10, anchor="s", width=mainContainer.winfo_width()-20)
        messageScrollContainer.place(x=10, y=35, width=mainContainer.winfo_width()-80, height=mainContainer.winfo_height()-70)
        messageCanvas.config(scrollregion=messageCanvas.bbox("all"))
        messageCanvas.itemconfig(window, width=messageCanvas.winfo_width())
        messageCanvas.yview_moveto(1)
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