import threading
import time
import serial
import sys
com_a = 'COM1'
com_b = 'COM4'

ser_a = serial.Serial(com_a, 9600, timeout=0)
ser_b = serial.Serial(com_b, 9600, timeout=0)
flRun = True
def thread1():
	while flRun:	
		bt_a = ser_a.read(1)
		if ( bt_a != b''):	
			print('ACCEPTED:'+bt_a)
			r = ser_b.write(bt_a)
			print('WRITED: ' + str(r) )
		bt_b = ser_b.read(1)
		if ( bt_b !=b''):
			print('ACCEPTED:'+bt_a[0])
			r = ser_a.write(bt_b)

	return
thread_a = threading.Thread(target=thread1)


def thread3():
	k = input()
	print('print exit for quit')
	if k=="exit":
		print("EXITING")	
		global flRun
		flRun=False	
thread_c = threading.Thread(target=thread3)
thread_a.start()
thread_c.start()

thread3()
time.sleep(2)
sys.exit(0)

