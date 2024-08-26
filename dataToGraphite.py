import socket
import pickle
import struct
import threading
import time
import action
import tracemalloc
import random
import datetime
# import singleton
import config

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
    time.sleep(5)
    # def sendData():
    #     fields = ['temperature','humidity','atmosphericPressure','amountSnowfall','roadTemperature','freezingPoint','waterFilmThickness','snowHeight','iceRatio','coefficientOfFriction','roadConditions','signalStrength']
    #     carbon = CarbonIface(config.BACKEND_CONFIG['ip'], 2004)##서버아이피주소로 변경
    #     datas = singleton.DataLogger.get_data()
    #     ts = time.time()
    #     for i in range(0,len(fields)):
    #         carbon.add_data("snowmelting." + fields[i], datas[i].get('value'), ts)
    #     carbon.send_data()
    #     action.all()
    #     return datas
    def sendData():
            fields = ['temperature','humidity','atmosphericPressure','amountSnowfall','roadTemperature','freezingPoint','waterFilmThickness','snowHeight','iceRatio','coefficientOfFriction','roadConditions','signalStrength']
            carbon = CarbonIface(config.BACKEND_CONFIG['ip'], 2004)
            datas = []
            for i in fields:
                    if i == "roadTemperature":
                        # test = round(random.uniform(18.0, 22.0), 1)
                        test = -3.5
                        datas.append(test)
                    elif i == "roadConditions":
                        test = 5    
                        datas.append(test)
                        print(test, "도로상황")
                    elif i == "temperature":
                        # test = round(random.uniform(13.0, 13.5), 1)
                        test = -1.2
                        datas.append(test)
                    elif i == "humidity":
                        test = round(random.uniform(40.0, 60.0), 1)
                        datas.append(test)
                    elif i == "atmosphericPressure":
                        test = round(random.uniform(850.0, 985.0), 1)
                        datas.append(test)
                    elif i == "waterFilmThickness":
                        test = round(random.uniform(200.0, 300.0), 1)
                        datas.append(test)
                    elif i == "amountSnowfall":
                        test = round(random.uniform(0.0, 0.5), 1)
                        datas.append(test)
                    elif i == "signalStrength":
                        test = 1
                        datas.append(test)
                    elif i == "iceRatio":
                        test = 10
                        datas.append(test)
                    elif i == "amountSnowfall":
                        test = 0
                        datas.append(test)
                    else:
                        datas.append(random.uniform(0,1)*10)
                        
            ts = int(time.time())
            # ts = int(time.time()+(9*3600))
            dt = datetime.datetime.utcfromtimestamp(ts)
            year = dt.year  # 년
            month = dt.month  # 월
            day = dt.day  # 일
            hour = dt.hour  # 시
            minute = dt.minute  # 분
            second = dt.second  # 초

            for i in range(0,len(fields)):
                if fields[i] == '1':
                    carbon.add_data("snowmelting." + fields[i], -300, ts)
                    print("에러확인")
                else:
                    carbon.add_data("snowmelting." + fields[i], datas[i], ts)
            carbon.send_data()
            print(datas, ts,"시간..")
            action.all()
            return datas
    sendData()