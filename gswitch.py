import sys
import serial
from serial.tools.list_ports import comports
import threading
import time
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QHBoxLayout, QPushButton, QTextBrowser, QVBoxLayout, QGridLayout, QMenu, QMenuBar, QCheckBox
from PyQt5 import QtCore, QtGui 
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


		
		self.cbShowAscii = QCheckBox('Ascii')	
		self.flAscii = False		

		self.gridLayout.addWidget(self.cbA, 0, 0)
		self.gridLayout.addWidget(self.cbB, 0, 1)
		self.gridLayout.addWidget(self.cbBaudrateA, 1, 0) 
		self.gridLayout.addWidget(self.cbBaudrateB, 1, 1)
		self.gridLayout.addWidget(self.pbCon)
		self.gridLayout.addWidget(self.pbRescan)
		self.gridLayout.addWidget(self.cbShowAscii)
		self.vLayout.addLayout(self.gridLayout)	
		self.setLayout(self.vLayout)
		self.setWindowTitle('Com switch')
		
		self.textBrowser = QTextBrowser()	
		self.scrollBar = self.textBrowser.verticalScrollBar()
		self.scrollBar.rangeChanged.connect(lambda: self.scrollBar.setValue(self.scrollBar.maximum()))
		self.vLayout.addWidget(self.textBrowser)	
		self.cbA.activated[int].connect( self.activated_a )	
		self.cbB.activated[int].connect( self.activated_a )	
		self.pbCon.clicked.connect( self.com_connect )	
		self.cbShowAscii.stateChanged[int].connect(self.switch_ascii)	
		self.pbRescan.clicked.connect( self.rescan )
		self.gridLayout.setSpacing(15)
		self.rescan()	
		self.default_speed = 115200
		print(self.width())
		width = 600 
		height = 500 
		self.resize(width, height)	
		print(self.width())
	
	def switch_ascii(self,code):
		if code == 2:
			self.flAscii = True
		else:
			self.flAscii = False
		pass	

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
				self.flRun = True
				def display_text(buff):
					str_ = ""	
					str_ = make_buff(buff)
					self.scrollBar.setValue( self.scrollBar.maximum()  )
					self.textBrowser.append(str_)
					self.scrollBar.setValue( self.scrollBar.maximum()  )

				def make_buff(buff_b):
					str_=""
					for b in buff_b:
						if b>31 and b < 128:
							str_=str_ + chr(b)
						else:
							if self.flAscii:
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
					print('COM THREAD:'+ str( threading.current_thread() ) )
					while self.flRun:	
						bt_a = self.ser_a.read(1)
						if ( bt_a != b'' and bt_a[0]!=0 ):	
							print(bt_a[0])
							buff_a = buff_a + bt_a
							a_printed = False
							a_accepted = datetime.now()
							if b_printed != True:
								display_text(buff_b)
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
								display_text(buff_a)
								print(buff_a)
								a_printed = True
								buff_a=b''
							r = self.ser_a.write(bt_b)
							continue
						b_passed = (datetime.now() - b_accepted ).total_seconds()
						if  b_passed > .1 and b_printed == False:
							print('PUT BY TIMEOUT B: ', b_passed)
							b_printed = True
							display_text(buff_b)
							buff_b=b''	
						if ( datetime.now() - a_accepted ).total_seconds()> .1 and a_printed == False:
							print('PUT BY DATE')
							display_text(buff_a)
							a_printed = True
							buff_a=b''	
					self.ser_a.close()
					self.ser_b.close()		
					print('THREAD STOPPING')
					return
				self.thread_a = threading.Thread(target=thread1)
				self.thread_a.start()
		else:
			print('SET FL_RUN TO STOP')	
			self.flRun = False		
			#if self.ser_a.is_open:
				#self.ser_a.close()
			
			#if self.ser_b.is_open:
				#self.ser_b.close()
			time.sleep(.5)
			self.pbCon.setText('Connect')	
			self.cbA.setEnabled(True)	
			self.cbB.setEnabled(True)	
			self.flConnected = False

	def closeEvent(self, event):
		self.flRun = False		
		time.sleep(1)
		event.accept()
		print('CLOSE EVENT')

def main():
	app = QApplication(sys.argv)
	w = ComWidget()
	w.show()
	app.exec_()

main()
