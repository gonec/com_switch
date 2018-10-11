import sys
import serial
from serial.tools.list_ports import comports
import threading
import time
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QHBoxLayout, QPushButton, QTextBrowser, QVBoxLayout, QGridLayout

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
				
				def thread1():
					print('STARTED')
					buff_a=b''
					buff_b=b''
					a_printed = False
					b_printed = False
					while flRun:	
						last_read=datetime.now()		
						bt_a = self.ser_a.read(1)
						if ( bt_a != b'' and bt_a[0]!=0 ):	
							buff_a = buff_a + bt_a
							a_printed = False
							if b_printed != True:
								#self.textBrowser.append(buff_b.decode() )
								print(buff_b)
								b_printed = True
								buff_b = b''
							r = self.ser_b.write(bt_a)
							continue	
						bt_b = self.ser_b.read(1)
						if ( bt_b != b'' and bt_b[0] != 0 ):
							b_printed = False
							buff_b = buff_b + bt_b
							if a_printed != True:
								#self.textBrowser.append(buff_a.decode())
								print(buff_a)
								a_printed = True
								buff_a=b''
							r = self.ser_a.write(bt_b)
							continue
						if a_printed!=True:
							print(buff_a)
							a_printed = True
							buff_a=b''
						if b_printed!=True:
							print(buff_a)
							b_printed = True
							buff_b=b''
	
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
