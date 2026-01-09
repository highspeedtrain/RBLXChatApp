import tkinter as ui
from tkinter import messagebox
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
transport = WebsocketsTransport(url="wss://fxdbjbvpegpmnrlqmvwc.hasura.eu-west-2.nhost.run/v1/graphql")

messageFunctionURL = "https://fxdbjbvpegpmnrlqmvwc.functions.eu-west-2.nhost.run/v1/message"

def onMessage():
    global jobId
    
async def initRealtime():
    subscriptionQuery = gql("""
    subscription {
        messages {
            message_id
            job_id
            username
            message
        }
    }
    """)
    
    async with Client(transport=transport, fetch_schema_from_transport=False) as session:
        async for result in session.subscribe(subscriptionQuery):
            if isAttached == False or result["messages"][-1]["job_id"] != jobId:
                continue
            newMessage(f"[{result["messages"][-1]["username"]}]: {result["messages"][-1]["message"]}")
    
def getJobId():
    global placeId
    global jobId
    global universeId
    global playingGame
    global userId
    global isAttached
    global userName
    
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

    newMessage(f"logfile read success")
    newMessage(f"jobid: {jobId}")
    newMessage(f"placeid: {placeId}")
    Response = requests.post(f"https://highspeedtrain.net/api/rblx/GetGameInfo", json={"placeIds": [placeId]}, headers=({"Accept": "application/json"}))
    if Response.status_code != 200:
        messagebox.showinfo("Failed to Attach", f"Cant get info on game u prlaying: stat code {Response.status_code}")
        jobId = None
        placeId = None
        universeId = None
        return
    
    newMessage("loaded game info")
    
    UserInfo = requests.get(f"https://users.roblox.com/v1/users/{userId}")
    if UserInfo.status_code != 200:
        messagebox.showinfo("Failed to Attach", f"Cant get info on your accoun: {UserInfo.status_code}")
        jobId = None
        placeId = None
        universeId = None
        return
    newMessage("loaded user info")
    
    ResponseData = Response.json()
    UserInfoData = UserInfo.json()
    if playingGame is None:
        return
    playingGame.set(f"Playing {ResponseData["data"][0]["name"]} by {ResponseData["data"][0]["builder"]}")
    userName = UserInfoData["name"]

    requests.post(messageFunctionURL, json={"job_id": jobId, "username": "System", "message": f"{userName} has joined"})
    newMessage("[Server]: Welcome to RBLXChat! Please keep things respectful.")
    newMessage("[Server]: Harrassment, homophobia, racism etc is not allowed.")
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
    
    newMessage("unattaching")
    
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
    
    Result = requests.post(messageFunctionURL, json={"job_id": jobId, "username": userName, "message": chatInput.get()})
    if Result == 200:
        return
    
    if Result == 429:
        messagebox.showinfo("Failed to Send Message", f"why are you sending so many messages")
        return
    elif Result == 500:
        messagebox.showinfo("Failed to Send Message", f"internal server error, please dm highzpeedtrain with info")
        return
    elif Result == 400:
        messagebox.showinfo("Failed to Send Message", f"server declined request cause of missing fields, please retry.")
        return
    
def newMessage(message):
    if messageCanvas is None or root is None:
        return
    
    ui.Label(messageContainer, text=message, anchor="w", justify="left").pack(pady=2, padx=2, fill="x")
    messageCanvas.update_idletasks()

def initUi(loop):
    global playingGame
    global chatInput
    global root
    global messageCanvas
    global messageContainer
    
    root = ui.Tk()
    root.title("RBLXChatApp")
    root.geometry(f"{500}x{300}")
    root.resizable(True, True)
    root.attributes("-topmost", True)
    
    playingGame = ui.StringVar(value="Not playing anything")

    attachButton = ui.Button(root, text="Attach", command=onAttachClicked)
    attachButton.place(x=root.winfo_width()-10, y=10, anchor="ne")
    
    unattachButton = ui.Button(root, text="Unattach", command=onUnattachClicked)
    unattachButton.place(x=root.winfo_width()-10, y=10, anchor="ne")
    
    playingGameLabel = ui.Label(root, textvariable=playingGame)
    playingGameLabel.place(x=10, y = 10, anchor = "nw")
    
    chatInput = ui.Entry(root)
    chatInput.place(relx=0.5, y=root.winfo_height()-10, anchor="s", width=root.winfo_width()-20)
    chatInput.bind("<FocusIn>", onMessageClicked)
    chatInput.bind("<FocusOut>", onMessageLeft)
    chatInput.bind("<Return>", onReturn)
    chatInput.insert(0, "Enter message here")
    
    messageScrollContainer = ui.Frame(root, borderwidth=1, relief="solid", bg="white")
    
    messageCanvas = ui.Canvas(messageScrollContainer)
    scrollbar = ui.Scrollbar(messageScrollContainer, orient="vertical", command=messageCanvas.yview)
    messageCanvas.config(yscrollcommand=scrollbar.set)
    
    messageCanvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    messageContainer = ui.Frame(messageCanvas)
    window = messageCanvas.create_window((0, 0), window=messageContainer, anchor="nw")
    
    def update_position():
        if root is None or chatInput is None or messageCanvas is None:
            return
        
        attachButton.place(x=root.winfo_width()-10, y=10, anchor="ne", width=55)
        unattachButton.place(x=root.winfo_width()-10, y=40, anchor="ne", width=55)
        chatInput.place(relx=0.5, y=root.winfo_height()-10, anchor="s", width=root.winfo_width()-20)
        messageScrollContainer.place(x=10, y=35, width=root.winfo_width()-80, height=root.winfo_height()-70)
        messageCanvas.config(scrollregion=messageCanvas.bbox("all"))
        messageCanvas.itemconfig(window, width=messageCanvas.winfo_width())
        messageCanvas.yview_moveto(1)
        loop.call_soon(loop.stop)
        loop.run_forever()
        root.after(100, update_position)
    
    root.after(100, update_position)
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