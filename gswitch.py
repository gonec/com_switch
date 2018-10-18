import sys
import serial
from serial.tools.list_ports import comports
import threading
import time
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QHBoxLayout, QPushButton, QTextBrowser, QVBoxLayout, QGridLayout, QMenu, QMenuBar
class UserSettings(QWidget):
	def __init_(self):
		pass
class ComWidget(QWidget):
	def __init__(self):
		super().__init__()
		
		self.bs = serial.Serial()	
		self.gridLayout = QGridLayout()
		self.vLayout = QVBoxLayout()
		self.cbA = QComboBox()
		self.cbB = QComboBox()		
		self.cbBaudrateA = QComboBox()		
		self.cbBaudrateB = QComboBox()	
		baudrates = [str(b) for b in self.bs.BAUDRATES if b>=9600 ]	
		self.cbBaudrateA.addItems(baudrates)	
		self.cbBaudrateB.addItems(baudrates)	
		db_pos = self.cbBaudrateA.findText('115200')	
		self.cbBaudrateA.setCurrentIndex(db_pos)
		self.cbBaudrateB.setCurrentIndex(db_pos)
		#self.cbBaudRate.insertItems(serial.Serial.BAUDRATES)
		self.flConnected = False		
		#ports = [p.device for p in comports()]
		#self.cbA.addItems(ports)	
		#self.cbB.addItems(ports)	
		self.pbRescan = QPushButton()
		self.pbRescan.setText('Rescan')
		self.pbCon = QPushButton()
		self.pbCon.setText('Connect')
		self.gridLayout.addWidget(self.cbA, 0, 0)
		self.gridLayout.addWidget(self.cbB, 0, 1)
		self.gridLayout.addWidget(self.cbBaudrateA, 1, 0) 
		self.gridLayout.addWidget(self.cbBaudrateB, 1, 1)
		self.gridLayout.addWidget(self.pbCon)
		self.gridLayout.addWidget(self.pbRescan)
		self.vLayout.addLayout(self.gridLayout)	
		self.setLayout(self.vLayout)
		self.setWindowTitle('Com switch')
		
		self.textBrowser = QTextBrowser()	
		self.vLayout.addWidget(self.textBrowser)	
		self.cbA.activated[int].connect( self.activated_a )	
		self.cbB.activated[int].connect( self.activated_a )	
		self.pbCon.clicked.connect( self.com_connect )	
		self.pbRescan.clicked.connect( self.rescan )
		self.gridLayout.setSpacing(15)
		self.rescan()	
		self.default_speed = 115200
		print(self.width())
		width = 340 
		height = 380 
		self.resize(width, height)	
		print(self.width())
	
	def rescan(self):
		ports = [p.device for p in comports()]
		self.cbA.clear()	
		self.cbB.clear()	
		self.cbA.addItems(ports)
		if len(ports) < 2:
			self.pbCon.setEnabled(false)
		else:
			self.pbCon.setEnabled(True)
			self.cbB.addItems(ports)
			txt_a = self.cbA.currentText()	
			index = self.cbB.findText(txt_a)
			self.cbB.removeItem(index)
				
	def activated_a(self, indx):
		txt_b = self.cbB.currentText()	
		txt_a = self.cbA.currentText()	
		if txt_b == txt_a:
			self.pbCon.setEnabled(False)	
		else:
			self.pbCon.setEnabled(True)
	
	def activated_b(self, indx):
		txt_b = self.cbB.currentText()	
		txt_a = self.cbA.currentText()	
		if txt_b == txt_a:
			self.pbCon.setEnabled(False)	
		else:
			self.pbCon.setEnabled(True)

	
	def com_connect(self):
		if not self.flConnected:	
				self.com_a = self.cbA.currentText()
				self.com_b = self.cbB.currentText()
				self.speed_a = self.cbBaudrateA.currentText()
				self.speed_b = self.cbBaudrateB.currentText()

				try:
					self.ser_a = serial.Serial(self.com_a, self.speed_a, timeout=0)	
					self.cbA.setEnabled(False)
				except:
					self.cbA.setEnabled(True)
					print('EXCEPT A ERROR')
					self.flConnected = False
					return 				
				
				try:
					self.ser_b = serial.Serial(self.com_b, self.speed_b, timeout=0)	
					self.cbB.setEnabled(False)
				except:
					self.cbA.setEnabled(True)
					self.cbB.setEnabled(True)
					self.flConnected = False
					self.ser_a.close()
					print('EXCEPT B ERROR')
					return
				
				self.flConnected = True
				self.pbCon.setText('Disconnect')	
				flRun = True
				
				def make_buff(buff_b):
					str_=""
					for b in buff_b:
						if b>31 and b < 128:
							str_=str_ + chr(b)
						else:
							str_=str_ + str(hex(b))
					return str_
												
				def thread1():
					print('STARTED')
					buff_a=b''
					buff_b=b''
					a_printed = True 
					b_printed = True 
					b_accepted = datetime.now()	
					a_accepted = datetime.now()	

					while flRun:	
						bt_a = self.ser_a.read(1)
						if ( bt_a != b'' and bt_a[0]!=0 ):	
							print(bt_a[0])
							buff_a = buff_a + bt_a
							a_printed = False
							a_accepted = datetime.now()
							if b_printed != True:
								#str=buff_b.decode('ascii') 
								str_ = make_buff(buff_a)
								self.textBrowser.append(str_)
								print(buff_b)
								b_printed = True
								buff_b = b''
							r = self.ser_b.write(bt_a)
							continue	
						bt_b = self.ser_b.read(1)
						if ( bt_b != b'' and bt_b[0] != 0 ):
							print(bt_b[0])
							b_printed = False
							buff_b = buff_b + bt_b
							b_accepted = datetime.now()
							if a_printed != True:
								#str=buff_b.decode('ascii') 
								str_=""
								str_ = make_buff(buff_b)	
								self.textBrowser.append(str_)
								print(buff_a)
								a_printed = True
								buff_a=b''
							r = self.ser_a.write(bt_b)
							continue
						#print( (datetime.now()-b_accepted ).total_seconds(), b_printed )	
						#print( (datetime.now()-a_accepted ).total_seconds(), a_printed )	
						b_passed = (datetime.now() - b_accepted ).total_seconds()
						if  b_passed > .1 and b_printed == False:
							print('PUT BY TIMEOUT B: ', b_passed)
							b_printed = True
							#str = buff_b.decode('ascii') 
							str_=""
							str_ = make_buff(buff_b)
							self.textBrowser.append(str_)
							buff_b=b''	
						if ( datetime.now() - a_accepted ).total_seconds()> .1 and a_printed == False:
							print('PUT BY DATE')
							a_printed = True
							#str = buff_a.decode('ascii') 
							str_=''
							str_ = make_buff(buff_a)
							self.textBrowser.append(str_)
							buff_a=b''	
	
					return
				self.thread_a = threading.Thread(target=thread1)
				self.thread_a.start()
		else:
			flRun = False		
			if self.ser_a.is_open():
				self.ser_a.close()
			
			if self.ser_b.is_open():
				self.ser_b.close()

			self.pbCon.setText('Connect')	
			self.flConnected = False
	def start():
		pass
def main():
	app = QApplication(sys.argv)
	w = ComWidget()
	w.show()
	app.exec_()

main()
