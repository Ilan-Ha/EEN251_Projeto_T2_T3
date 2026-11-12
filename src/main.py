import tkinter as tk
from datetime import datetime
from zoneinfo import ZoneInfo
from paho_mqtt import Subscriber,Publisher
from PIL import Image, ImageTk
from log import Log
from env import Env
from dataset import Dataset
import json
import os
import cv2

dataset = Dataset()

RASP = False
LED = False
ULTRASOUND = False
ULTRASOUND_DISTANCE = 30.0
BG = "#000043"
p = os.getcwd()       
if 'src' in p:
    p = os.path.dirname(p)       
p = os.path.join(p,'logs')
log = Log(path=p)
env = Env()
publisher = Publisher(log=log,env=env)
if ULTRASOUND:
    from ultrasound import Ultrasound
    ultrassom = Ultrasound(env=env)
if LED:
    from led_controller import Led_controller
    led = Led_controller(env=env)
    if RASP:
        from facial_recognizer import Recognizer
        f_r = Recognizer(publisher=publisher,dataset=dataset,led=led)
    
subscriber = Subscriber(log=log,env=env,
    topics=[("/v2.0/devices/camera-detection/open-door/lv",1)],
    subscribers_functions=[lambda client,userdata,message: root.after(
         0, update_door, client,userdata,message
     )])

ZONE = ZoneInfo("America/Sao_Paulo")

root = tk.Tk()

SIZE = 40
PAD = 10
FONT_SIZE = 16
WIHE = 2
UPTIME = env.UPDATE_TIME
running_camera = False
retrain_model = False

def on_closing():
    global subscriber,root,log,cameras,main,running_camera,vid
    cameras = False
    main = False
    if running_camera:
        if vid.isOpened():
            vid.release()
        running_camera = False
    subscriber.stop()
    publisher.stop()
    root.destroy()
    if not log._canLog:
        log.canLog = True
    if LED:
        led.clean()
    if ULTRASOUND:
        ultrassom.clean()

info:tk.Label
image_label:tk.Label
detection = [tk.Label(),tk.Label()]
vid: cv2.VideoCapture

root.attributes("-fullscreen", True)
root.eval('tk::PlaceWindow . center')
root.title("Facial ID Control")
main = True
cameras = False
users = False
def draw_borders(root,fun=lambda a:None):
    global main,cameras,info,detection
    app_bar = tk.Frame(master=root,background='#000000',height=SIZE,width=root.winfo_screenwidth())
    app_bar.pack(side='top',fill=tk.X)
    foter = tk.Frame(master=root,background='#000000',height=SIZE,width=root.winfo_screenwidth())
    foter.pack(side='bottom',fill=tk.X)

    bg ='#ff0000' if not cameras else '#000000'
    fg = '#ffffff'if not cameras else '#000000'
    hc = '#ffffff'if not cameras else '#000000'
    bw = 3 if not cameras else 0
    if not main:
        tk.Button(master=app_bar,text='←',takefocus=False,borderwidth=bw,background=bg,foreground=fg,highlightcolor=hc,font=("Arial", FONT_SIZE,"bold"),command=fun).pack(side='left',padx=PAD,pady=PAD)
    else:
        tk.Label(master=app_bar,text='←',takefocus=False,borderwidth=0,background='#000000',foreground='#000000',highlightcolor='#000000',font=("Arial", FONT_SIZE,"bold")).pack(side='left',padx=PAD,pady=PAD)

    tk.Button(master=app_bar,text='X',takefocus=False,borderwidth=bw,background=bg,foreground=fg,highlightcolor=hc,font=("Arial", FONT_SIZE,"bold"),command=on_closing).pack(side='right',padx=PAD,pady=PAD)
    center_bar = tk.Frame(master=app_bar,background='#000000')
    center_bar.pack(anchor='center',fill=tk.X,padx=60)
    left_center = tk.Frame(master=center_bar,background='#000000')
    left_center.pack(side='left')
    right_center = tk.Frame(master=center_bar,background='#000000')
    right_center.pack(side='right')
    center_center = tk.Frame(master=center_bar,background='#000000')
    center_center.pack()
    detection[0] = tk.Label(master=left_center,font=("Arial", FONT_SIZE,"bold"),background='#000000',foreground='#ffffff')
    detection[0].pack(padx=PAD,pady=PAD)
    info = tk.Label(master=center_center,text=datetime.now(ZONE).strftime("%d/%m/%Y | %H:%M:%S"),font=("Arial", FONT_SIZE,"bold"),background='#000000',foreground='#ffffff')
    info.pack(padx=PAD,pady=PAD)
    info.after(UPTIME,update_time)
    detection[1] = tk.Label(master=right_center,font=("Arial", FONT_SIZE,"bold"),background='#000000',foreground='#ffffff')
    detection[1].pack(padx=PAD,pady=PAD)

def retaining(root):
    global retrain_model
    if LED and RASP:
        f_r.train_model()
    retrain_model = False
    back(root,main_window)

def main_window(root):
    root.config(background=BG)
    global main,cameras,retrain_model,users
    main = True
    cameras = False
    users = False
    draw_borders(root=root)
    tk.Button(text='Camera',master=root,command=lambda self=root,fun=camera:back(self=self,fun=fun)).pack(side='left',padx=PAD,pady=PAD)
    tk.Button(text='Usuários',master=root,command=lambda self=root,fun=user:back(self=self,fun=fun)).pack(side='left',padx=PAD,pady=PAD)
    if retrain_model:
        retrain_button = tk.Button(master=root, text="retrain", width=10, bg='#ff0000',highlightcolor='#ffffff',takefocus=False,border=3,foreground='#ffffff',font=("Arial", FONT_SIZE,"bold"),command=lambda root=root:retaining(root=root))
        retrain_button.pack(side='left',padx=20, pady=(20, 10))

def back(self,fun):
    global tirando_fotos,cam_fotos
    if tirando_fotos:
        if cam_fotos.isOpened():
            cam_fotos.release()
    for widget in self.winfo_children():
        widget.destroy()
    fun(self)

def back_extra(self,name,path,fun):
    for widget in self.winfo_children():
        widget.destroy()
    fun(self,name,path)

adicionadndo_user = False
tirando_fotos = False
def user(root):
    root.config(background=BG)
    global main,cameras,info,users,adicionadndo_user,tirando_fotos,dataset
    main = False
    cameras = False
    users = True
    adicionadndo_user = False
    tirando_fotos = False
    draw_borders(root=root,fun=lambda self=root,fun=main_window: back(self=self,fun=fun))
    top_pane = tk.Frame(master=root)
    top_pane.pack(side='top')
    bottom_pane=tk.Frame(master=root,bg="#363636")
    bottom_pane.pack(side='bottom')
    tk.Button(text='Add User',master=top_pane,command=lambda self=root,fun=add_user:back(self=self,fun=fun)).pack(side='left',padx=PAD,pady=PAD)
    scrollbar = tk.Scrollbar(master=bottom_pane)
    scrollbar.pack(side='right',fill=tk.Y)
    my_list = tk.Listbox(master=bottom_pane,yscrollcommand=scrollbar.set,font=("Arial", FONT_SIZE,"bold"))
    for line in dataset.data['users']:
        my_list.insert(tk.END,f'ID:{f'{line}':>4}| {dataset.data['users'][line]}')
    my_list.pack(side='left',fill='both')


lbl_warning: tk.Label
txt_add: tk.Text

def add_user(root):
    global users,adicionadndo_user,tirando_fotos,lbl_warning,txt_add
    users = False
    adicionadndo_user = True
    tirando_fotos = False
    root.config(background=BG)
    draw_borders(root=root,fun=lambda self=root,fun=user: back(self=self,fun=fun))
    lbl_add = tk.Label(text="Nome",master=root,font=("Arial", FONT_SIZE,"bold"),bg=BG,fg='#ffffff')
    lbl_add.pack()
    txt_add = tk.Text(master=root,height=5, width=40)
    txt_add.pack()
    lbl_warning = tk.Label(master=root,foreground='#ff0000',background=BG,font=("Arial", FONT_SIZE,"bold"))
    lbl_warning.pack()
    btn_add = tk.Button(text="Adicionar",master=root,command=lambda self=root:adicionando_usuario(root=self))
    btn_add.pack()

cam_fotos:cv2.VideoCapture
phot_label:tk.Label
def fotos_novas(root,name,path):
    global users,adicionadndo_user,tirando_fotos, cam_fotos,phot_label
    users = False
    adicionadndo_user = False
    tirando_fotos = True
    root.config(background=BG)
    draw_borders(root=root,fun=lambda self=root,fun=user: back(self=self,fun=fun))
    phot_label = tk.Label(root,background=BG,foreground=BG)
    phot_label.pack(padx=PAD,pady=PAD,anchor='center')
    tira_fotos = tk.Button(master=root,text="Tirar foto",height=8,width=8,command=lambda name=name,path=path:salvar_usuario(name=name,path=path))
    tira_fotos.pack(side='bottom',padx=PAD,pady=PAD)
    cam_fotos = cv2.VideoCapture(0)
    root.after(UPTIME,tirando_fotos_de_usuario)

temp_foto:cv2.typing.MatLike
def salvar_usuario(name,path):
    global temp_foto
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.jpg"
    filepath = os.path.join(path, filename)
    cv2.imwrite(filepath, temp_foto)


def tirando_fotos_de_usuario():
    global tirando_fotos,cam_fotos,phot_label,temp_foto
    if tirando_fotos:
        _, frame = cam_fotos.read()
        temp_foto = frame
        cv2.flip(frame,1,frame)
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        captured_image = Image.fromarray(opencv_image)
        photo_image = ImageTk.PhotoImage(image=captured_image)
        phot_label.photo_image = photo_image
        phot_label.config(image=photo_image)
        phot_label.after(UPTIME,tirando_fotos_de_usuario)

def adicionando_usuario(root):
    global lbl_warning,txt_add, retrain_model,dataset
    res = txt_add.get('1.0','end-1c')
    if res == '':
        lbl_warning.config(text="Preencha o campo de nome primeiro")
    else:
        path = dataset.add_user(res)
        retrain_model = True
        back_extra(root,res,path,fotos_novas)
        


def camera(root):
    root.config(background='#000000')
    global main,cameras,image_label,users
    main = False
    cameras = True
    users = True
    draw_borders(root=root,fun=lambda self=root,fun=main_window: back(self=self,fun=fun))
    
    image_label = tk.Label(root,background='#000000',foreground='#000000')
    image_label.pack(padx=PAD,pady=PAD,anchor='center')
    root.after(UPTIME,camera_cycle)

def open_camera():
    global running_camera,vid
    if not running_camera:
        vid = cv2.VideoCapture(0)
        if not vid.isOpened():
            print("Cannot open USB camera")
        running_camera = True
        root.after(UPTIME,camera_loop)

def close_camera():
    global running_camera
    if running_camera:
        running_camera = False

def camera_loop():
    global cameras,vid,image_label,running_camera
    if not cameras:
        if vid.isOpened():
            vid.release()
        image_label.configure(image='')
        if LED:
            led.off()
        return
    _, frame = vid.read()
    cv2.flip(frame,1,frame)
    if LED and RASP:
        frame = f_r.analyse(frame)
    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    captured_image = Image.fromarray(opencv_image)
    photo_image = ImageTk.PhotoImage(image=captured_image)
    image_label.photo_image = photo_image
    image_label.configure(image=photo_image)
    if not running_camera:
        vid.release()
        image_label.configure(image='')
        if LED:
            led.off()
        return
    else:
        image_label.after(UPTIME,camera_loop)

def camera_cycle():
    global cameras
    if ULTRASOUND:
        distance = ultrassom.distance()
        if distance == -1.0:
            print("Erro no ultrassom")
            on_closing()
            return
        if distance < ULTRASOUND_DISTANCE:
            open_camera()
        else:
            close_camera()
    if cameras:
        root.after(UPTIME,camera_cycle)

def update_door(client, userdata, message):
    global subscriber,detection,led,cameras
    subscriber.on_message(client, userdata, message)
    value = float(message.payload.decode("utf-8"))
    
    if value == 1:
        for d in detection:
            d.config(
            text="DOOR OPEN",
            fg="green"
            )
        if LED:
            led.green()
        if cameras:
            open_camera()
        

    else:
        for d in detection:
            d.config(
            text="",
            fg="#000000"
            )
        if LED:
            led.off()
        if cameras:
            close_camera()

def update_time():
    global info
    info.config(text=datetime.now(ZONE).strftime("%d/%m/%Y | %H:%M:%S"))
    info.after(UPTIME,update_time)

main_window(root)

root.protocol("WM_DELETE_WINDOW", on_closing)

subscriber.start()
publisher.start()

root.mainloop()
