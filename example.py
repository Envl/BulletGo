#coding=utf-8
'''
Created on 2012-4-6
 
@author: 大孟
'''
 
import sys
from PyQt5 import  QtGui, QtCore  ,QtWidgets,uic
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QTime 
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QColor 
from PyQt5.QtGui import QPolygon
#from PyQt5.QtCore import SIGNAL as signal
# qtCreatorFile="ui.ui"

# Ui_MainWindow, QtBaseClass=uic.loadUiType(qtCreatorFile)
 
class Clock(QtWidgets.QMainWindow):
    '''
    classdocs
    '''
 
 
    def __init__(self):
        '''
        Constructor
        '''
         
        super(Clock, self).__init__()  
         
        self.hourColor=QColor(127, 0, 127);
        self.minuteColor=QColor(0, 127, 127, 191)
        self.secondColor=QColor(127, 127,0,120)
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30) 
        self.show() 
         
    def handChange(self):    
         
        self.side = min(self.width(), self.height())
        self.hand=(max(self.side/200,4), max(self.side/100,8), max(self.side/40,30))
        self.hourHand=QPolygon([QPoint(self.hand[0],self.hand[1]),QPoint(-self.hand[0],self.hand[1]),QPoint(0,-self.hand[2])])
        self.minuteHand=QPolygon([QPoint(self.hand[0],self.hand[1]),QPoint(-self.hand[0],self.hand[1]),QPoint(0,-self.hand[2]*2)])
        self.secondHand=QPolygon([QPoint(self.hand[0],self.hand[1]),QPoint(-self.hand[0],self.hand[1]),QPoint(0,-self.hand[2]*3)]) 
     
    def set_transparency(self, enabled):
        if enabled:
            self.setAutoFillBackground(False)
        else:
            self.setAttribute(Qt.WA_NoSystemBackground, False)
        #下面这种方式好像不行
#        pal=QtGui.QPalette()
#        pal.setColor(QtGui.QPalette.Background, QColor(127, 127,10,120))
#        self.setPalette(pal) 
        self.setAttribute(Qt.WA_TranslucentBackground, enabled)
        self.repaint()
    
    def initUI(self):      
  
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Clock')
        self.handChange()
        self.rightButton=False
        # 下面两个配合实现窗体透明和置顶
        sizeGrip=QtWidgets.QSizeGrip(self)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow ) 
        #self.setMouseTracking(True);
        self.trans=True
 
        self.set_transparency(True) 
 
        self.popMenu= QtWidgets.QMenu() 
   
         
    def resizeEvent(self, e):  
        self.handChange()
         
    def backClicked(self):
        if self.trans == True :
            self.trans = False 
            self.set_transparency(False)
        else: 
            self.trans = True
            self.set_transparency(True)
         
    def mouseReleaseEvent(self,e): 
        if self.rightButton == True:
            self.rightButton=False
            self.popMenu.popup(e.globalPos())
 
    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            self.move(e.globalPos()-self.dragPos)
            e.accept()
    def mousePressEvent(self, e):
       
        if e.button() == Qt.LeftButton: 
            self.dragPos=e.globalPos()-self.frameGeometry().topLeft() 
            e.accept()
        if e.button() == Qt.RightButton and self.rightButton == False:
            self.rightButton=True
            sys.exit()
     
    def paintEvent(self, e): 
        time = QTime.currentTime() 
        qp = QPainter()
 
        qp.begin(self)
        #qp.setRenderHint(QPainter.Antialiasing)  # 开启这个抗锯齿,会很占cpu的!
        qp.translate(self.width() / 2, self.height() / 2) 
        qp.scale(self.side / 200.0, self.side / 200.0)
  
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(self.hourColor)
        qp.save()
        qp.rotate(30.0 * ((time.hour() + time.minute()/ 60.0)))
        qp.drawConvexPolygon(self.hourHand)
        qp.restore()
         
        qp.setPen(self.minuteColor)
        qp.drawText(0,0,"Testdddddddddddddd")
        for i in range(12): 
            qp.drawLine(88, 0, 96, 0)
            qp.rotate(30.0) 
         
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(self.minuteColor)
        qp.save()
         
        qp.rotate(6.0 * ((time.minute() + (time.second()+time.msec()/1000.0) / 60.0)))
        qp.drawConvexPolygon(self.minuteHand)
        qp.restore()
         
         
        qp.setPen(self.minuteColor)
        for i in range(60): 
            if (i % 5) is not 0:
                qp.drawLine(92, 0, 96, 0)
            qp.rotate(6.0) 
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(self.secondColor)
        qp.save()
        qp.rotate(6.0*(time.second()+time.msec()/1000.0))
        qp.drawConvexPolygon(self.secondHand)
        qp.restore() 
        qp.end() 
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    clock = Clock()
    clock.show()
    sys.exit(app.exec_())