import socket
import pickle
import struct
import threading
import time
import random
import action
import psutil
import tracemalloc

# import singleton

# ip = "192.168.0.5"
ip = "localhost"

tracemalloc.start()

class CarbonIface(object):

    class Fields:
        temperature = 0.0
        humidity = 0.0
        atmosphericPressure = 0.0
        amountSnowfall = 0.0
        roadTemperature = 0.0 
        freezingPoint = 0.0
        waterFilmThickness = 0.0
        snowHeight = 0.0
        iceRatio = 0.0
        coefficientOfFriction = 0.0
        roadConditions = 0.0 
        signalStrength = 0.0

    def __init__(self, host, port, event_url=None):
        self.host = host
        self.port = port
        self.event_url = event_url
        self.__data = []
        self.__data_lock = threading.Lock()

    def add_data(self, metric, value, ts=None):
        if not ts:
            ts = time.time()
        if self.__data_lock.acquire():
            self.__data.append((metric, (ts, value)))
            self.__data_lock.release()
            return True
        return False

    def add_data_dict(self, dd):
        if self.__data_lock.acquire():
            for k, v in dd.items():
                ts = v.get("ts", time.time())
                value = v.get("value")
                self.__data.append((k, (ts, value)))
            self.__data_lock.release()
            return True
        return False

    def add_data_list(self, dl):
        if self.__data_lock.acquire():
            self.__data.extend(dl)
            self.__data_lock.release()
            return True
        return False

    def send_data(self, data=None):
        save_in_error = False

        if not data:
            if self.__data_lock.acquire():
                data = self.__data
                self.__data = []
                save_in_error = True
                self.__data_lock.release()
            else:
                return False

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        payload = pickle.dumps(data)
        header = struct.pack("!L", len(payload))
        message = header + payload

        s.connect((self.host, self.port))

        try:
            s.send(message)
        except:
            print("Error when sending data to carbon")
            if save_in_error:
                self.__data.extend(data)
            return False
        else:
            print('Sent data to {host}:{port}: {0} metrics, {1} bytes'.format(len(data), len(message), host = self.host, port=self.port))
            return True
        finally:
            s.close()

while True:
    time.sleep(10)
    # def sendData():
    #     fields = ['temperature','humidity','atmosphericPressure','amountSnowfall','roadTemperature','freezingPoint','waterFilmThickness','snowHeight','iceRatio','coefficientOfFriction','roadConditions','signalStrength']
    #     carbon = CarbonIface(ip, 2004)##서버아이피주소로 변경
    #     datas = singleton.DataLogger.get_data()
    #     ts = time.time()
    #     for i in range(0,len(fields)):
    #         carbon.add_data("snowmelting." + fields[i], datas[i].get('value'), ts)
    #     carbon.send_data()
    # sendData()
    def sendData():
            fields = ['temperature','humidity','atmosphericPressure','amountSnowfall','roadTemperature','freezingPoint','waterFilmThickness','snowHeight','iceRatio','coefficientOfFriction','roadConditions','signalStrength']
            carbon = CarbonIface(ip, 2004)
            datas = []
            for i in fields:
                    if i == "roadConditions":
                        test = random.uniform(0,0.7)*10
                        datas.append(round(test, 0))
                        print(round(test, 0))
                    elif i == "signalStrength":
                        test = 0
                        datas.append(test)
                    elif i == "temperature":
                        test = random.uniform(-0.2,1.6)*10
                        datas.append(round(test, 0))
                    else:
                        datas.append(random.uniform(0,1)*10)
                        
            ts = time.time()
            for i in range(0,len(fields)):
                if fields[i] == '1':
                    carbon.add_data("snowmelting." + fields[i], -300, ts)
                    print("에러확인")
                else:
                    carbon.add_data("snowmelting." + fields[i], datas[i], ts)
            carbon.send_data()
            print(datas)
            action.all()
            return datas
    process = psutil.Process()
    mem_info = process.memory_info()
    mem_usage = mem_info.rss / 1024 / 1024 # KB -> MB
    print("Current memory usage: {} MB".format(mem_usage))
    sendData()
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 10**6}MB")