from raytracer import Raytracer
import os
import threading
import clr
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

import System.Drawing as Dwg
import System.Windows.Forms as Frms
        
class Button(Frms.Button):
    def __init__(self,LocX,LocY,Text,ClickEvent):
        self.Location = Dwg.Point(LocX, LocY)
        self.Text = Text
        self.Size = Dwg.Size(80, 28)
        self.Click += ClickEvent       
        
class Label(Frms.Label):
    def __init__(self,LocX,LocY,SizeX,Text):
        self.Location = Dwg.Point(LocX, LocY)
        self.Size = Dwg.Size(SizeX, 18)
        self.Text=Text
        self.TextAlign = Dwg.ContentAlignment.MiddleCenter
        
class TextBox(Frms.TextBox):
    def __init__(self,LocX,LocY,Min,Max):
        self.Location = Dwg.Point(LocX,LocY)
        self.Size = Dwg.Size(25, 25)
        self.TextChanged += self.textBoxChanged
        self.Min=Min
        self.Max=Max
        
    def textBoxChanged(self,sender,e):
        if self.Text.isalpha():self.Text=""
        elif self.Text=="" or self.Text=="-":pass
        elif int(self.Text) < self.Min: self.Text=str(self.Min)
        elif int(self.Text) > self.Max: self.Text=str(self.Max)

class Picture(Frms.PictureBox):
    def __init__(self,SizeX,SizeY,Path):
        self.BackColor = Dwg.Color.White
        self.Location = Dwg.Point(250, 15)
        self.sizeChange(SizeX, SizeY)
        self.Path=Path
    def refresh(self):
        self.Image=Dwg.Bitmap(self.Path)
    def sizeChange(self,SizeX, SizeY):
        self.Size = Dwg.Size(SizeX, SizeY)
    def clear(self):
        if(self.BackColor == Dwg.Color.White):self.BackColor = Dwg.Color.Transparent
        if self.Image != None:
            self.Image.Dispose()
            self.ImageLocation = None
            self.Image = None
            self.Update()
        else:
            pass
        
class ApplicationWindow(Frms.Form):
    def __init__(self):
        self.Raytracer=Raytracer()
        self.SuspendLayout()
        self.WorkingDirectory=os.getcwd()
       
        # 
        # Buttons
        #
        self.ButtonRefresh=Button(35,260,"Refresh",self.renderThread)
        self.Controls.Add(self.ButtonRefresh)
        self.ButtonDefault=Button(135,260,"Default",self.defaultSettings)
        self.Controls.Add(self.ButtonDefault)
        
        # 
        # Labels
        #
        self.LabelCameraPosition=Label(15,20,220,"Camera Position")
        self.Controls.Add(self.LabelCameraPosition)        
        self.LabelCameraPositionX=Label(40,50,15,"X:")
        self.Controls.Add(self.LabelCameraPositionX)       
        self.LabelCameraPositionY=Label(95,50,15,"Y:")
        self.Controls.Add(self.LabelCameraPositionY)     
        self.LabelCameraPositionZ=Label(150,50,15,"Z:")
        self.Controls.Add(self.LabelCameraPositionZ)

        self.LabelLightPosition=Label(15,80,220,"Light Position")
        self.Controls.Add(self.LabelLightPosition)        
        self.LabelLightPositionX=Label(40,110,15,"X:")
        self.Controls.Add(self.LabelLightPositionX)       
        self.LabelLightPositionY=Label(95,110,15,"Y:")
        self.Controls.Add(self.LabelLightPositionY)     
        self.LabelLightPositionZ=Label(150,110,15,"Z:")
        self.Controls.Add(self.LabelLightPositionZ)

        self.LabelLightColor=Label(15,140,220,"Light Color")
        self.Controls.Add(self.LabelLightColor)        
        self.LabelLightColorR=Label(40,170,15,"R:")
        self.Controls.Add(self.LabelLightColorR)       
        self.LabelLightColorG=Label(95,170,17,"G:")
        self.Controls.Add(self.LabelLightColorG)     
        self.LabelLightColorB=Label(150,170,15,"B:")
        self.Controls.Add(self.LabelLightColorB)

        self.LabelCanvas=Label(15,200,220,"Canvas Size")
        self.Controls.Add(self.LabelCanvas)        
        self.LabelCanvasWidth=Label(40,230,40,"Width:")
        self.Controls.Add(self.LabelCanvasWidth)       
        self.LabelCanvasHeight=Label(120,230,40,"Height:")
        self.Controls.Add(self.LabelCanvasHeight) 
        
        self.LabelRefresh=Label(15,300,220,"-")
        self.LabelRefresh.Visible=False
        self.Controls.Add(self.LabelRefresh)
        
        # 
        # TextBoxes
        #
        self.TextBoxCameraPositionX=TextBox(60,48,-20,20)
        self.Controls.Add(self.TextBoxCameraPositionX)
        self.TextBoxCameraPositionY=TextBox(115,48,-20,20)
        self.Controls.Add(self.TextBoxCameraPositionY)
        self.TextBoxCameraPositionZ=TextBox(170,48,-20,20)
        self.Controls.Add(self.TextBoxCameraPositionZ)

        self.TextBoxLightPositionX=TextBox(60,108,-20,20)
        self.Controls.Add(self.TextBoxLightPositionX)
        self.TextBoxLightPositionY=TextBox(115,108,-20,20)
        self.Controls.Add(self.TextBoxLightPositionY)
        self.TextBoxLightPositionZ=TextBox(170,108,-20,20)
        self.Controls.Add(self.TextBoxLightPositionZ)

        self.TextBoxLightColorR=TextBox(60,169,0,255)
        self.Controls.Add(self.TextBoxLightColorR)
        self.TextBoxLightColorG=TextBox(115,169,0,255)
        self.Controls.Add(self.TextBoxLightColorG)
        self.TextBoxLightColorB=TextBox(170,169,0,255)
        self.Controls.Add(self.TextBoxLightColorB)

        self.TextBoxCanvasWidth=TextBox(80,228,0,1500)
        self.TextBoxCanvasWidth.Size = Dwg.Size(35, 25)
        self.Controls.Add(self.TextBoxCanvasWidth)
        self.TextBoxCanvasHeight=TextBox(160,228,0,1000)
        self.TextBoxCanvasHeight.Size = Dwg.Size(35, 25)
        self.Controls.Add(self.TextBoxCanvasHeight)
        self.defaultSettings()
        
        #
        # Image
        #
        self.ImageBox=Picture(self.Raytracer.width, self.Raytracer.height,"{}\\image.png".format(self.WorkingDirectory))
        self.Controls.Add(self.ImageBox)
       
        # 
        # MainForm
        # 
        self.changeWindowSize()
        try:
            self.IconPath="{}\\images\\RT.ico".format(self.WorkingDirectory)
            self.Icon = Dwg.Icon(self.IconPath)
        except:
            pass
            #self.error("Loading icon error")
        
        self.MaximizeBox = False
        self.MinimizeBox = False
        self.TopMost = True 
        self.Text = "Raytracer"
        self.FormBorderStyle = Frms.FormBorderStyle.FixedDialog
        self.ResumeLayout(False)
        self.PerformLayout()
        self.Show()

    def changeWindowSize(self):
        self.ClientSize = Dwg.Size(self.Raytracer.width+265, self.Raytracer.height+30)
        self.ImageBox.sizeChange(self.Raytracer.width, self.Raytracer.height)

    def defaultSettings(self,*args):
        self.TextBoxCameraPositionX.Text="0"
        self.TextBoxCameraPositionY.Text="0"
        self.TextBoxCameraPositionZ.Text="10"

        self.TextBoxLightPositionX.Text="-10"
        self.TextBoxLightPositionY.Text="0"
        self.TextBoxLightPositionZ.Text="0"

        self.TextBoxLightColorR.Text="255"
        self.TextBoxLightColorG.Text="255"
        self.TextBoxLightColorB.Text="255"

        self.TextBoxCanvasWidth.Text="500"
        self.TextBoxCanvasHeight.Text="500"
                
    def renderThread(self,sender,*Args):
        self.LabelRefresh.Visible=True
        self.ButtonRefresh.Enabled=False
        self.ButtonDefault.Enabled=False
        
        self.Raytracer.setCameraPosition(float(self.TextBoxCameraPositionX.Text),float(self.TextBoxCameraPositionY.Text),float(self.TextBoxCameraPositionZ.Text))
        self.Raytracer.light.setLightPosition(float(self.TextBoxLightPositionX.Text),float(self.TextBoxLightPositionY.Text),float(self.TextBoxLightPositionZ.Text))
        self.Raytracer.light.setLightColor(int(self.TextBoxLightColorR.Text),int(self.TextBoxLightColorG.Text),int(self.TextBoxLightColorB.Text))
        self.Raytracer.setCanvas(int(self.TextBoxCanvasWidth.Text),int(self.TextBoxCanvasHeight.Text))
        
        st = threading.Thread(target=self.renderImage)
        st.start()
        
    def renderImage(self):
        try:
            self.Raytracer.renderScene(self.LabelRefresh,self.ImageBox)
        except:
            self.LabelRefresh.Visible=False
            self.ButtonRefresh.Enabled=True
            self.ButtonDefault.Enabled=True
            self.error("Rendering error")
        self.LabelRefresh.Visible=False
        
        try:
            self.changeWindowSize()
            self.ImageBox.refresh()
        except:
            self.error("Loading image error")
            self.ButtonRefresh.Enabled=True
            self.ButtonDefault.Enabled=True
        self.ButtonRefresh.Enabled=True
        self.ButtonDefault.Enabled=True
            
    def error(self,message):
        Frms.MessageBox.Show("Oops!Something went wrong.\n\n{}".format(message), "Error", Frms.MessageBoxButtons.OK, Frms.MessageBoxIcon.Error)

Window=ApplicationWindow()
Frms.Application.Run(Window)
