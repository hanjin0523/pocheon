import minimalmodbus as minimalmodbus
import serial
import traceback
import time
import math
import config
print(minimalmodbus.__version__)

print() # Pretty Hack

# Initializing Color
isColor = False

class Color:
    reset = "\x1b[0;0m" if isColor else ""
    bold = "\x1b[1m" if isColor else ""
    blink2 = "\x1b[6;6m" if isColor else ""
    black = "\x1b[30m" if isColor else ""
    red = "\x1b[31m" if isColor else ""
    bgpurple = "\x1b[45m" if isColor else ""
    blred = "\x1b[91m" if isColor else ""
    blgreen = "\x1b[92m" if isColor else ""
    blpurple = "\x1b[95m" if isColor else ""
    success = "\x1b[6;30;42m" if isColor else ""
    memo = f"{blink2}{black}{bgpurple}" if isColor else ""

class DataLogger(object):
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):         # Foo 클래스 객체에 _instance 속성이 없다면
            print("__new__ is called\n")
            cls._instance = super().__new__(cls)  # Foo 클래스의 객체를 생성하고 Foo._instance로 바인딩
        return cls._instance                      # Foo._instance를 리턴

    def __init__(self, data):
        cls = type(self)
        if not hasattr(cls, "_init"):             # Foo 클래스 객체에 _init 속성이 없다면
            print("__init__ is called\n")
            self.data = data
            cls._init = True
    
    # Initializing Modbus-RTU
    driver = minimalmodbus.Instrument(config['usbadd'], 0x01, minimalmodbus.MODE_RTU, debug=False) ##서버USB로 변경해줘야함
    # driver = minimalmodbus.Instrument(config.BACKEND_CONFIG['usbadd'], 0x01, minimalmodbus.MODE_RTU, debug=False) ##서버USB로 변경해줘야함
    driver.serial.baudrate = 9600
    driver.serial.bytesize = 8
    driver.serial.parity = serial.PARITY_NONE
    driver.serial.stopbits = 1
    driver.serial.timeout = 1.0

    # Initializing Report data

    
    # Parse Error
    def get_error_value(error):
        result_value = 0
        result_message = ""

        if isinstance(error, minimalmodbus.IllegalRequestError):
            result_value = -100
            result_message = "Illegal request"
        elif isinstance(error, minimalmodbus.NoResponseError):
            result_value = -200
            result_message = "No response"
        elif isinstance(error, minimalmodbus.InvalidResponseError):
            result_value = -300
            result_message = "Invalid response"
        elif isinstance(error, minimalmodbus.SlaveDeviceBusyError):
            result_value = -400
            result_message = "Slave device busy"
        elif isinstance(error, minimalmodbus.ModbusException):
            result_value = -999
            result_message = "Modbus exception"

        result_detail_message = None if result_value == 0 else traceback.format_exc()
        return {'value': result_value, 'message': result_message, 'detail': result_detail_message}

    #Testing Read Registers...
    print(f"test Read register {Color.blpurple}30001{Color.reset} to {Color.blpurple}30023{Color.reset}\n\n")
    
    def get_data():
        report_data = []
        for i in range(1, 13):
            print(report_data)
            map_addr = 0
            hex_addr = 0
            map_addr = i * 2 - 1
            hex_addr = map_addr - 1
            try:
                test_float = DataLogger.driver.read_float(hex_addr, functioncode=0x03, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
                print(test_float)
                if(math.isnan(test_float)):
                    test_float = -2
                report_data.append({'register': map_addr + 30000, 'value': test_float})
            except minimalmodbus.IllegalRequestError as e:
                # 슬레이브가 불법 요청을 받았습니다.
                report_data.append({'register': map_addr + 30000, 'value': -100})
            except minimalmodbus.NoResponseError as e:
                # 슬레이브에서 응답이 없습니다.
                report_data.append({'register': map_addr + 30000, 'value': -200})
            except minimalmodbus.InvalidResponseError as e:
                # The response does not fulfill the Modbus standad, for example wrong checksum.
                report_data.append({'register': map_addr + 30000, 'value': -300})
            except minimalmodbus.SlaveDeviceBusyError as e:
                # The slave is busy processing some command.
                report_data.append({'register': map_addr + 30000, 'value': -400})
            except minimalmodbus.ModbusException as e:
                # Base class for Modbus communication exceptions.
                # Inherits from IOError, which is an alias for OSError in Python3.
                report_data.append({'register': map_addr + 30000, 'value': -999})
        time.sleep(0.1)
        return report_data
DataLogger.get_data()
    # def set_data(num):
        
    #     powerNum = float(num)
    #     print(f"{Color.bold}{Color.blgreen}Reading test is {Color.success}fine\x1b[0m.\n\n")
    #     # Testing Write Registers...

    #     print(f"Test Write Resister {Color.blpurple}30025{Color.reset}\n")
        
    #     try:
    #         map_addr = 25
    #         hex_addr = map_addr - 1
    #         function_code = 0x10

    #         print(f"Map Addr: {Color.blgreen}3{map_addr:04d}{Color.reset}")
    #         print(f"Hex Addr: 0x{Color.blgreen}{hex_addr:04x}{Color.reset}")
    #         print(f"FunctionCode: 0x{Color.blgreen}{function_code:02x}{Color.reset}")
    #         print(f"This Packet's Byteorder is {Color.memo}Little_Swap{Color.reset}")

    #         DataLogger.driver.write_float(hex_addr, powerNum, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    #     except minimalmodbus.IllegalRequestError as e:
    #         print(f"{Color.blred}Error: {e}{Color.reset}")
    #         print(f"{Color.red}30025는 functioncode 0x10 으로 쓸 수 없는 레지스터{Color.reset}")
    #         DataLogger.report_data.append({'register': map_addr + 30000, 'value': DataLogger.get_error_value(e)})
    #     return ##2.13일 추가로직

        # print(f"{Color.success}Fine{Color.reset}") 

        # print("\n\nReport Data")
        # for data in DataLogger.report_data:
        #     print("report start")
        #     print(f"Register: {data['register']} | Value: {data['value']}")
        #     print("report end")

        # print(f"\n\n{Color.success}finish{Color.reset}\n")

# def get_data(): 기존값이 없을 경우 로직 
#     report_data = []
#     prev_test_float = None
#     for i in range(1, 13):
#         map_addr = 0
#         hex_addr = 0
#         map_addr = i * 2 - 1
#         hex_addr = map_addr - 1
#         try:
#             test_float = DataLogger.driver.read_float(hex_addr, functioncode=0x03, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
#             print(test_float)
#             if(math.isnan(test_float)):
#                 test_float = -2
#             report_data.append({'register': map_addr + 30000, 'value': test_float})
#             prev_test_float = test_float
#         except:
#             if prev_test_float is not None:
#                 report_data.append({'register': map_addr + 30000, 'value': prev_test_float})
#             else:
#                 report_data.append({'register': map_addr + 30000, 'value': -999})
#     time.sleep(0.1)
#     return report_data

