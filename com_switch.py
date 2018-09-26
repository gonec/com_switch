import threading
import time
import serial
import sys
com_a = 'COM4'
com_b = 'COM7'
ser_a = serial.Serial(com_a, 9600, timeout=1)
ser_b = serial.Serial(com_b, 9600, timeout=1)
flRun = True
def thread1():
	while flRun:	
		bt = ser_a.read(1)
		if ( bt != b''):	
			print('ACCEPTED:'+bt.decode())
			r = ser_b.write(bt)
			print('WRITED: ' + str(r) )

	return
def thread2():
	while flRun:
		bt = ser_b.read(1)
		if ( bt !=b''):
			print('ACCEPTED:'+bt.decode())
			r = ser_a.write(bt)
			print('WRITED: ' + str(r) )

	return	
thread_a = threading.Thread(target=thread1)
thread_b = threading.Thread(target=thread2)
#thread_c = threading.Thread(target=thread3)


thread_a.start()
thread_b.start()
#thread_c.start()
def thread3():
	k = input()
	print('print exit for quit')
	if k=="exit":
		print("EXITING")	
		global flRun
		flRun=False	

thread3()
time.sleep(2)
sys.exit(0)

