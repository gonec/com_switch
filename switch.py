import threading
import time
import serial
import sys
com_a = 'COM1'
com_b = 'COM6'

ser_a = serial.Serial(com_a, 115200, timeout=0)
ser_b = serial.Serial(com_b, 115200, timeout=0)
ser_a.flushInput()
ser_a.flushOutput()
ser_b.flushInput()
ser_b.flushOutput()

flRun = True

buff_b = b''
def thread1():
	buff_a = b''
	buff_b = b''
	b_printed=True
	a_printed=True
	while flRun:	
		
		bt_a = ser_a.read(1)
		if ( bt_a != b'' and int(bt_a[0])!=0 ):	
			if not b_printed:
				print(buff_b)
				b_printed = True
				buff_b=b''
			#print('AT: '+ str( int(bt_a[0]) ) )
			a_printed=False
			buff_a = buff_a + bt_a
			r = ser_b.write(bt_a)
			
			ser_b.flush()
			#print('WRITED TO AT: ' + str(r) + str(bt_a[0] ))
			continue
			
		
		bt_b = ser_b.read(1)
		if ( bt_b !=b'' and int(bt_b[0])!=0 ):
			r = ser_a.write(bt_b)
			ser_a.flush()
			if not a_printed:
				print(buff_a)
				a_printed = True
				buff_a=b''
			#print('FROM CTR: '+str(int(bt_b[0])) )
			b_printed=False
			buff_b = buff_b + bt_b
			
			continue
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

