import sys
from PyQt5 import QtCore, QtGui, uic,QtWidgets
from PyQt5.QtCore import Qt,QObject,QUrl
from PyQt5.QtCore import QPoint,QByteArray
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter,QFont
from PyQt5.QtGui import QColor,QPicture
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QSystemTrayIcon,QDesktopWidget,QHBoxLayout,QVBoxLayout
from PyQt5.QtWidgets import QPushButton,QPlainTextEdit,QAction,QWidget,QLineEdit
from PyQt5.QtWidgets import QSizeGrip,QShortcut
from CBullet import Bullet
import random,GLOBAL
from PyQt5.QtNetwork import QNetworkRequest,QNetworkAccessManager
import requests,time
from multiprocessing.dummy import Pool as ThreadPool
import _thread
# from LabelButton import labelButton

# qtCreatorFile="ui.ui"

# Ui_MainWindow, QtBaseClass=uic.loadUiType(qtCreatorFile)

# class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
class MyApp(QtWidgets.QMainWindow):
	mouseLeaveTimer=0

	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		# Ui_MainWindow.__init__(self)
		#自己有__init__函数时,不会默认调用基类的__init__函数
		# 因为这里重写了__init__将基类的覆盖掉了,故需要主动调用之
		super(MyApp,self).__init__()
		# 	Get the Screen size
		self.screenWidth=QDesktopWidget().availableGeometry().width()
		self.screenHeight=QDesktopWidget().availableGeometry().height()
		#初始化字体
		font=QFont('黑体')
		font.setPointSize(12)
		app.setFont(font)
		#  ColorSetting
		self.bgColor=QColor(66,66,77,88)

		#
		# self.setupUi(self)
		self.initUI();
		#用来控制半透明的bg面板自动消失
		self.timer=QTimer()
		self.timer.start(30)
		self.setGeometry(0,30,self.screenWidth,self.screenHeight//3)

		#Flagsq
		self.IsMouseHover=False
		self.MouseOver=False
		self.Locked=False
		self.Hidden=False
		self.isDrag=False
		self.isResize=False
		#变量初始化
		GLOBAL.WINDOWWIDTH=self.width()
		GLOBAL.WINDOWHEIGHT=self.height()
		self.bullets=[]
		self.dragPos=QPoint(22,22)
		self.savedName=''
		# self.screenBuffer=QBitmap(GLOBAL.WINDOWWIDTH,GLOBAL.WINDOWHEIGHT)
		# self.bufferPainter=QPainter(self.screenBuffer)
		self.picture=QPicture()
		# 建立connection和slot的连接
		self.createConnections()


	def initUI(self):
		#构建托盘
		self.trayIcon=QSystemTrayIcon(self)
		self.trayIcon.setIcon(QtGui.QIcon("tmpIcon.ico"))
		self.trayIcon.show()
		self.trayIcon.setToolTip('BulletGo')

		# 构建托盘菜单
		action_quit=QAction('退出',self)
		action_quit.triggered.connect(self.exitApp)
		# action_switchLock=QAction('锁定/解锁(F6)',self)
		# action_switchLock.triggered.connect(self.switchLock)
		action_showHide=QAction('显示/隐藏',self)
		action_showHide.triggered.connect(lambda:self.switchVisible(self))
		action_Settings=QAction('设置',self)
		action_Settings.triggered.connect(lambda:self.switchVisible(self.settingWindow))
		trayIconMenu=QtWidgets.QMenu(self)
		# trayIconMenu.addAction(action_switchLock)
		trayIconMenu.addAction(action_showHide)
		trayIconMenu.addSeparator()
		trayIconMenu.addAction(action_Settings)
		trayIconMenu.addAction(action_quit)

		#设定快捷键
		QtWidgets.QShortcut(QtGui.QKeySequence(\
			QtCore.Qt.Key_F7),self,\
		(lambda:self.switchVisible(self.settingWindow)))
		QtWidgets.QShortcut(QtGui.QKeySequence(\
			QtCore.Qt.Key_F6),self,\
		(self.switchLock))

		self.trayIcon.setContextMenu(trayIconMenu)
		# 保障不按下鼠标也追踪mouseMove事件
		self.setMouseTracking(True)
		self.setMinimumSize(600,260)
		self.setWindowTitle("BulletGo")
		sizeGrip=QtWidgets.QSizeGrip(self)
		self.setWindowFlags(Qt.FramelessWindowHint\
			|Qt.WindowStaysOnTopHint|Qt.SubWindow\
			|Qt.Tool|Qt.X11BypassWindowManagerHint)
		#Plan A
		self.setAttribute(Qt.WA_TranslucentBackground,True)
		#这一句是给Mac系统用的,防止它绘制(很黯淡的)背景
		self.setAutoFillBackground(False)
		QSizeGrip(self).setVisible(True)
		#Plan B  失败
		# palette=QPalette()
		# color=QColor(190, 230, 250)
		# color.setAlphaF(0.6)
		# palette.setBrush(self.backgroundRole(), color)
		# self.setPalette(palette)
		# self.setAutoFillBackground(True)
		# self.setBackgroundRole(QPalette.Window)

		#创建房间的Button和 输入框

		self.roomName=QPlainTextEdit()
		self.roomName.setPlaceholderText('请输入房间名')
		# self.roomName.resize(50,20)
		# self.roomName.move(0,0)
		# self.roomName.setBackgroundVisible(False)
		self.createBtn=QPushButton("创建/进入")
		self.hideBtn=QPushButton('隐藏本设置窗口')
		self.hideBtn.clicked.connect(lambda:self.switchVisible(self.settingWindow))
		# self.createBtn.resize(50,20)
		# self.move(0,100)
		# self.d
		settingLayout=QVBoxLayout()
		hLayout=QHBoxLayout()
		settingLayout.addWidget(self.roomName)
		hLayout.addWidget(self.hideBtn)
		hLayout.addWidget(self.createBtn)
		self.settingWindow=QWidget()
		# self.hideBtn=setShortcut(QtGui.QKeySequence('Ctrl+B'))
		settingLayout.addLayout(hLayout)
		self.settingWindow.setLayout(settingLayout)
		# Qt.Tool的作用是  不在任务栏显示
		self.settingWindow.setWindowFlags(Qt.FramelessWindowHint|Qt.Tool\
			|Qt.X11BypassWindowManagerHint|Qt.Popup)
		self.roomName.show()
		self.createBtn.show()
		self.settingWindow.resize(160,26)
		self.settingWindow.show()


		# self.btnFire=QPushButton("Fire",self)
		# self.btnFire.resize(60,60)
		# self.btnFire.move(100,30)
		# self.btnFire.show()

		# self.btnLock=QPushButton("Lock",self)
		# self.btnLock.resize(40,40)
		# self.btnLock.move(self.screenWidth/2,30)
		# self.btnLock.setFlat(True)
		# self.btnLock.setIcon(QtGui.QIcon("tmpIcon.png"))
		# self.btnLock.show()



		# self.danmakuEditText=QPlainTextEdit(self)
		# self.danmakuEditText.resize(200,100)
		# self.danmakuEditText.move(100,100)
		# self.danmakuEditText.setBackgroundVisible(False)
		# self.danmakuEditText.show()



	def fireBtn(self):
		txt=self.danmakuEditText.toPlainText()
		tmpbullet=Bullet(txt,GLOBAL.ORANGE,random.randrange(9,16,2))
		self.bullets.append(tmpbullet)
		tmpbullet.prepare()
		# print(len(self.bullets))
		# testStr="line1\nline2\nline3"
		# textsAndInfo=self.preProcessText(testStr)
		# print(len(textsAndInfo))
		# print

	


	def fireABullet(self,txt,color=GLOBAL.ORANGE):
		tmpbullet=Bullet(txt,color,random.randrange(12,22,2))
		self.bullets.append(tmpbullet)
		tmpbullet.prepare()

	def createConnections(self):
		self.timer.timeout.connect(self.update)
		# self.btnFire.clicked.connect(self.fireBtn)
		self.createBtn.clicked.connect(self.createRoom)
		# self.btnLock.clicked.connect(self.switchLock)
		# self.btnLock.clicked.connect(self.pullMsg)
		self.trayIcon.activated.connect(self.trayClick)

	def switchVisible(self,handle):
		if(handle.isHidden()):
			handle.activateWindow()
		handle.setHidden(not handle.isHidden())

	def trayClick(self,reason):
		#单击事件还没设计好
		# if(reason==QSystemTrayIcon.Trigger):
		# 	self.switchVisible(self)
		if(reason==QSystemTrayIcon.DoubleClick):
			self.switchVisible(self.settingWindow)


	def switchLock(self):
		self.Locked=not self.Locked

	def genQColorFromStr(self,color):
		return{
			'white':GLOBAL.WHITE,
			'green':GLOBAL.GREEN,
			'red':GLOBAL.RED,
			'pink':GLOBAL.PINK,
			'purple':GLOBAL.PURPLE,
			'darkblue':GLOBAL.DARKBLUE,
			'blue':GLOBAL.BLUE,
			'yellow':GLOBAL.YELLOW,
			'cyan':GLOBAL.CYAN,
			'orange':GLOBAL.ORANGE
		}[color]

	def preProcessText(self,string):
		return string.split('`<')

	def realPullMsg(self):
		url='http://danmaku.applinzi.com/message.php'
		r =  requests.post(url,data=self.savedName)
		r.encoding='utf-8'
		#预处理收到的字符串  
		# print(r.text)
		# r.te
		textsAndInfo=self.preProcessText(r.text)
		i=0
		# print(textsAndInfo)
		# print(r.text)
		if(len(textsAndInfo)>1):
			while(i<len(textsAndInfo)-1):
				# print(len(textsAndInfo))
				# print('ddddd')
				# print(i)
				self.fireABullet(textsAndInfo[i],self.genQColorFromStr(textsAndInfo[i+1]))
				i+=2

	def pullMsg(self):
		_thread.start_new_thread(self.realPullMsg,())

	def createRoom(self):
		#编码问题实在天坑!!!
		# postData='#0'.encode('utf-8')
		# postData=self.roomName.toPlainText()
		self.savedName=self.roomName.toPlainText().encode('utf-8')#保存自己的房间号
		postData=self.roomName.toPlainText().encode('utf-8')
		r = requests.post('http://danmaku.applinzi.com/createroom.php',data=postData)
		r.encoding='utf-8'
		self.fireABullet(r.text)
		# print(r.encoding)
		if(len(r.text)==7):
			# 开始自动获取服务器上的消息内容
			self.pullTimer=QTimer()
			self.pullTimer.start(1000)
			self.pullTimer.timeout.connect(self.pullMsg)
		# print(r.content)
		# print(r.text)

	def closeEvent(self,e):
		e.accept()

	def mouseReleaseEvent(self,e):
		if(e.button()==Qt.LeftButton):
			self.isDrag=False
			self.isResize=False

	def mousePressEvent(self,e):
		if e.button()==Qt.LeftButton:
			self.LDown=True
			# self.dragPos=e.globalPos()-self.frameGeometry().topLeft()
			self.dragPos=e.pos()#效果同上,鼠标相对窗口左上角的位置
			
			if(GLOBAL.WINDOWWIDTH-e.pos().x()<16\
			and GLOBAL.WINDOWHEIGHT-e.pos().y()<16):
				self.topLeft=self.frameGeometry().topLeft()
				self.isResize=True
			else:
				self.isDrag=True
		# else:
		# 	if e.button()==Qt.RightButton:
		# 		self.exitApp()
		e.accept()

	def mouseMoveEvent(self,e):
		if(GLOBAL.WINDOWWIDTH-e.pos().x()<16\
			and GLOBAL.WINDOWHEIGHT-e.pos().y()<16):
			#更改鼠标样式
			self.setCursor(Qt.SizeFDiagCursor)
		else:
			self.setCursor(Qt.ArrowCursor)
		#如果是Resize,改变窗口大小
		if(self.isResize):
			tmp=e.globalPos()-self.topLeft
			self.move(self.topLeft)
			self.resize(tmp.x(),tmp.y())
		if (self.isDrag):
			self.move(e.globalPos()-self.dragPos)
		e.accept();



	def enterEvent(self,e):
		self.MouseOver=True
		self.IsMouseHover=True
		return super(MyApp,self).enterEvent(e)

	def setMouseHoverFalse(self):
		# if(not self.MouseOver):
		self.IsMouseHover=self.MouseOver


	def leaveEvent(self,e):
		QTimer.singleShot(800,self.setMouseHoverFalse)
		self.MouseOver=False
		return super(MyApp,self).leaveEvent(e)

	def resizeEvent(self,e):
		GLOBAL.WINDOWWIDTH=self.width()
		GLOBAL.WINDOWHEIGHT=self.height()
		# self.screenBuffer=QBitmap(GLOBAL.WINDOWWIDTH,GLOBAL.WINDOWHEIGHT)
		# self.bufferPainter=QPainter(self.screenBuffer)
		# print('resized')
		# self.repaint()
		e.accept()

	def paintEvent(self,e):
		# Get the Painter
		painter=QPainter(self)
		font=QFont('黑体',GLOBAL.BULLETFONTSIZE,QFont.Bold)
		painter.setFont(font)
		#Draw a semi-Transparent rect whose size is the same with this window
		if(self.IsMouseHover and (not self.Locked)):
			painter.fillRect(0,0,GLOBAL.WINDOWWIDTH,GLOBAL.WINDOWHEIGHT\
				,self.bgColor)
		# painter.setBackground(QBrush(QColor(123,222,123,122)))
		#画所有bullet
		for b in self.bullets:
			b.draw(painter)
		for b in self.bullets:
			if(b.IsExpired):
				self.bullets.remove(b)
		# painter.drawPicture(0,0,self.picture)
		# painter.drawText(30,100,"Hello this is a PyQt5 App我也会说中文")
		return super(MyApp,self).paintEvent(e)

	def exitApp(self):
		self.trayIcon.hide()
		sys.exit()

if __name__=="__main__":
	app=QtWidgets.QApplication(sys.argv)
	window=MyApp()
	window.show()
	sys.exit(app.exec_())