#!/bin/python
from pymodbus.client.sync import ModbusSerialClient
import time, sys


print('')
print('SRI-47x   B A R E    M I N I M U M')
print('(written by  upracht 2021. Please report bugs to sri-47x@posteo.de)')
print('')
print('available commands')

print('')
print('\t init .................. initialize cooler using auto port-scan')
print('\t init <port> ........... initialize cooler on port <val>')
print('')
print('\t go .................... start the cooler max speed')
print('')
print('\t start ................. start the cooler')
print('\t stop .................. stop the cooler')
print('\t target <val> .......... start cooler in closed loop and aim for <val>C (needs diode to be installed)')
print('\t kickstart on/off ...... activate/deactivate kickstart on power-on')
print('')
print('\t live .................. current performance')
print('\t para .................. current operation parameters')
print('\t diode <val> ........... set <val> as diode setpoint and diode closed-loop operation')
print('\t speed <val> ........... set <val> as speed setpoint and speed closed-loop operation')
print('\t open <val> ............ deactivate any PID control')
print('\t PID ................... display PID values')
print('\t P/I/D <val> ........... set <val> for P/I/D')
print('')
print('\t delete ................ clear control register')
print('\t error ................. view error register')
print('\t clear ................. clear error register')
print('\t save .................. save current settings to flash memory')
print('\t load .................. load settigs from flash memory')
print('\t default ............... reset cooler to factory settings')
print('')
print('\t read <reg> ............ read register <reg>')
print('\t write <reg> <val> ..... write value <val> to register <val> (Expert mode, not fail-safe!')
print('\t calibrate ............. run calbration routine (Don´t run this unless you know what you are doing)')
print('')
print('\t exit .................. leave the application')


codes = {0:"NO ERROR",
                        1:"POSITION SENSOR OFFSET",
                        2:"PEAK OVERCURRENT LIMIT",
                        4:"POSITION SENSOR RANGE",
                        16:"DC BUS LIMIT LOW",
                        32:"DC BUS LIMIT HIGH",
                        64:"DIODE DISCONNECTED",
                        256:"DC BUS LIMIT LOW FAST",
                        512:"POSITION SENSOR NOT CALIBRATED",
                        1024:"WRONG ROTATION DIRECTION",
                        8192:"CURRENT OFFSET",
                        16384:"ADC SPI",
                        32768:"DIODE VOLTAGE CALIBRATION"}



class Cooler():
	def __init__(self, port):

		if sys.platform=='linux':
			pre = '/dev/ttyUSB'
		elif sys.platform=='win32':
			pre = 'COM'

		if port != None:

			self.port = f"{pre}{port}"
			self.client = ModbusSerialClient(method='rtu', port = self.port, baudrate=38400)
			if self.client.connect() == True:
				print(f'connected on {self.port}')
			else:
				print('no device found')
				run = False
		else:
			search,i = True,0
			while search == True:
				self.port = f"{pre}{i}"
				self.client = ModbusSerialClient(method='rtu', port = self.port, baudrate=38400)
				if self.client.connect() == True:
					search = False
					print(f'connected on {self.port}')

				else:
					i += 1
					if i > 100:
						run = False
						print('no device found')
						time.sleep(1)

	def read(self,reg):
		res = 0
		try:
			res = self.client.readwrite_registers(read_address=reg, read_count=1,  write_address=24, write_registers=51, unit=51).registers[0],
		except (AttributeError,UnboundLocalError) as e:
			print(f'error while reading - {e}')
		return res

	def write(self,reg,val):
		res = 0
		try:
			res = self.client.readwrite_registers(read_address=reg, read_count=1,  write_address=reg, write_registers=val, unit=51).registers[0],
		except (AttributeError,UnboundLocalError) as e:
			print(f'error while reading - {e}')
		return res


	def TtoV(self,T):
		self.V = -0.0192*T**2 - 22.218*T + 6681.6
		return self.V

	def VtoT(self,V):
		self.T = 4.19658*10**(-17)*V**5 - 1.73015*10**(-12)*V**4 + 2.75529*10**(-8)*V**3 - 0.000213335*V**2 + 0.757513837*V - 865.6646704
		return self.T

run = True
while run:
	cmd = input('>>> ')

	if cmd == 'go':
		c.write(6,3900)
		c.write(5,7)

	elif cmd == 'exit':
		run=False
		print('...leaving. Thank you, Sir!')
	elif 'kickstart' in cmd:
		val = cmd.split(' ')[1]
		if val == 'on':
			if c.read(5)[0] < 1000:
				send = c.read(5)[0] + 1024
				c.write(5,send)
			else:
				pass
		elif val == 'off':
			if c.read(5)[0] > 1000:
				send = c.read(5)[0] - 1024
				c.write(5,send)
			else:
				pass

	elif  'T ' in cmd:
		val = float(cmd.split(' ')[1])
		V = c.TtoV(val)/10000.
		print(f"{val}C correspond to {round(V,4)}V")

	elif cmd == 'T':
		V = c.read(1)[0]
		T = c.VtoT(V)
		print(f"{round(T,2)}C or {round(T,2)+273.15}K ")

	elif 'init' in cmd:
		try:
			port =  int(cmd.split(' ')[1])
		except:
			port = None
		c = Cooler(port)

	elif cmd == 'start':
		send = c.read(5)[0] + 1
		c.write(5,send)

	elif cmd == 'stop':
		send = c.read(5)[0] - 1
		c.write(5,send)

	elif cmd == 'live':
		bus = c.read(2)[0]/10.
		rpm = c.read(0)[0]
		diode = c.read(1)[0]/10000.
		print(f'speed: {rpm} RPM  -  diode: {diode} V  -  bus: {bus} VDC ')

	elif 'speed' in cmd:
		val = int(cmd.split(' ')[1])
		if 0 <= val <= 3900:
			c.write(6,val)
			print(f"speed set value changed to {c.read(6)[0]} RPM")
		else:
			print('ERROR: speed set value must be within 0 - 3900 RPM')

		if c.read(5)[0]%2 == 0: # off
			c.write(5,4)
		else:
			c.write(5,5) 

	elif 'read' in cmd:
		reg = int(cmd.split(' ')[1])
		res = c.read(reg)[0]
		print(res)

	elif 'write' in cmd:
		reg = int(cmd.split(' ')[1])
		val = int(cmd.split(' ')[2])
		res = c.write(reg,val)

	elif cmd == 'error':
		print(codes[c.read(4)[0]])

	elif cmd  == 'clear':
		c.write(5,8)


	elif cmd == 'calibrate':
		print('Note: Calibration is required only in rare cases of malfunction.\nRun this routine only if you know what you are doing.\nThe process will last for about 30 seconds.')
		cal = input('start? (y/n)' )
		if cal == 'y' or cal == 'Y':
			print('clear error register')
			c.write(5,8)
			print('...done')
			print('clear control register')
			c.write(5,0)
			print('...done')
			print('load default seetings')
			c.write(5,128)
			print('...done')
			print('start calibration sequence')
			c.write(19,20001)
			while c.read(0)[0] < 100:
				print('...')
				time.sleep(1)
			c.write(5,0)
			print('done')
		else:
			pass


	elif cmd == 'open':
		send = c.read(5)[0]
		if send%2 == 1: #on
			if send > 1000:
				c.write(5,1031)
			else:
				c.write(5,7)
		else:
			if send > 1000:
				c.write(5,1030)
			else:
				c.write(5,6)

#	elif cmd == 'closed':
#		if c.read(5)[0] >= 6:
#			send = c.read(5)[0] - 6
#			c.write(5,send)
#		else:
#			pass

	elif cmd == 'delete':
		c.write(5,0)


	elif 'diode' in cmd:
		val = int(float(cmd.split(' ')[1])*10000)
		if 0 <= val <= 14000:
			c.write(8,val)
			print(f"diode set value changed to {c.read(8)[0]/10000.} V")
		else:
			print('ERROR: diode set value must be within 0 - 1.4V')

		c.write(6,3900) # allow the full speed range

		if c.read(5)[0]%2 == 0: # off
			c.write(5,2)
		else:
			c.write(5,3) 

	elif cmd == 'default':
		c.write(5,128)

	elif cmd == 'PID':
		P = c.read(14)[0]
		I = c.read(15)[0]
		D = c.read(16)[0]
		print(f'P: {P}  -  I {I}  -  D {D}')

	elif 'P ' in cmd:
		val = int(cmd.split(' ')[1])
		if 0 < val < 32767:
			c.write(14,val)
		else:
			print(f'ERROR: P must be within 0 ... 32767. Default is P = 25000.')
	elif 'I ' in cmd:
		val = int(cmd.split(' ')[1])
		if 0 < val < 32767:
			c.write(15,val)
		else:
			print(f'ERROR: I must be within 0 ... 32767. Default is I = 4500.')
	elif 'D ' in cmd:
		val = int(cmd.split(' ')[1])
		if 0 < val < 32767:
			c.write(16,val)
		else:
			print(f'ERROR: D must be within 0 ... 32767. Default is D = 20.')

	elif cmd == 'time':
		res = c.read(18)[0]/4.
		print(f'total operational time {res}h')

	elif cmd == 'save':
		send = c.read(5)[0] + 32
		c.write(5,send)

	elif cmd == 'load':
		send = c.read(5)[0] + 64
		c.write(5,send)


	elif 'target' in cmd:
		val = int(cmd.split(' ')[1])
		V = int(c.TtoV(val))
		c.write(8,V)
		c.write(5,1)
