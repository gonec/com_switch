import sys
import serial
from serial.tools.list_ports import comports
import threading
import time



from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QHBoxLayout, QPushButton, QTextBrowser, QVBoxLayout

class ComWidget(QWidget):
	
	def __init__(self):
		super().__init__()
		self.hLayout = QHBoxLayout()
		self.vLayout = QVBoxLayout()
		self.cbA = QComboBox()
		self.cbB = QComboBox()		
		self.flConnected = False		
		ports = [p.device for p in comports()]
		self.cbA.addItems(ports)	
		self.cbB.addItems(ports)	
		self.pbCon = QPushButton()
		self.pbCon.setText('Connect')
		self.hLayout.addWidget(self.cbA)
		self.hLayout.addWidget(self.cbB)
		self.hLayout.addWidget(self.pbCon)
		self.vLayout.addLayout(self.hLayout)	
		self.setLayout(self.vLayout)
		self.setWindowTitle('Com switch')
		
		self.textBrowser = QTextBrowser()	
		self.vLayout.addWidget(self.textBrowser)	
		self.cbA.activated[int].connect( self.activated_a )	
		self.cbB.activated[int].connect( self.activated_a )	
		self.pbCon.clicked.connect( self.com_connect )	
	
	def activated_a(self, indx):
		pass
	
	def activated_b(self, indx):
		pass
	
	def com_connect(self):
		if not self.flConnected:	
				self.com_a = self.cbA.currentText()
				self.com_b = self.cbB.currentText()
				try:
					self.ser_a = serial.Serial(self.com_a, 115200, timeout=0)	
					self.cbA.setEnabled(False)
				except:
					self.cbA.setEnabled(True)
					print('EXCEPT A ERROR')
					self.flConnected = False
					return 				
				
				try:
					self.ser_b = serial.Serial(self.com_b, 115200, timeout=0)	
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
						bt_a = self.ser_a.read(1)
						if ( bt_a != b'' and bt_a[0]!=0):	
							buff_a = buff_a + bt_a
							a_printed = False
							if b_printed != True:
								#self.textBrowser.append(buff_b.decode() )
								print(buff_b)
								b_printed = True
								buff_b = b''
							r = self.ser_b.write(bt_a)
							
						bt_b = self.ser_b.read(1)
						if ( bt_b !=b'' and bt_b[0]!=0):
							b_printed = False
							buff_b = buff_b + bt_b
							if a_printed != True:
								#self.textBrowser.append(buff_a.decode())
								print(buff_a)
								a_printed = True
								buff_a=b''
							r = self.ser_a.write(bt_b)

					return
				thread_a = threading.Thread(target=thread1)
				thread_a.start()
		else:
			if self.ser_a.is_open():
				self.ser_a.close()
			
			if self.ser_b.is_open():
				self.ser_b.close()

			self.ser_a.close()
			self.ser_b.close()
			self.pbCon.setText('Connect')	
			self.flConnected = False
			flRun = False		
	def start():
		pass
def main():
	app = QApplication(sys.argv)
	w = ComWidget()
	w.show()
	app.exec_()

main()
