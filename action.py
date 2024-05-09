
import requests
import socket
import threading
import time
import pickle
import struct
import yaml
import config
import dataBaseMaria
import logging
import singleton
# logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# mariadb = dataBaseMaria.DatabaseMaria('localhost', 3306, 'jang', 'jang','pochen','utf8')

class CarbonIface(object):

    class Fields:
        
        roadConditions = 0.0 

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

class readSet:

    read_condition = []
    radio_Check = 0
    select_Check = 0
    power = 0
    load_Data = 0

class readManual:
    manual_value : bool
    manual_mode : bool

def get_average(data):
    values = [point[0] for point in data if point[0] not in [None]]
    if values:
        average = sum(values) / len(values)
        return round(average, 1)
    else:
        return None

def get_road_conditions():
    field = 'roadConditions'
    data = requests.get("http://"+config.BACKEND_CONFIG['ip']+config.BACKEND_CONFIG['dbport']+"/render/?&target="+config.BACKEND_CONFIG['metric']+field + "&from=-1min&format=json")
    average_value = get_average(data.json()[0].get('datapoints'))
    if average_value is not None:
        average_value = round(average_value)
        print(average_value)
        readSet.load_Data = average_value
    return {'data':field, 'value':average_value}

count = 0
def sendOnOff(num):
    global count
    if count == 24:
        logging.info(f'POWER : {num}')
        count = 0
    else:
        count += 1
    fields = 'signal'
    carbon = CarbonIface(config.BACKEND_CONFIG['ip'], 2004)
    datas = ''
    ts = time.time()
    if num == False:
        carbon.add_data(config.BACKEND_CONFIG['metric']+ fields, 0, ts)
        singleton.DataLogger.set_data(0)
        print("전원OFF서버전송")
    if num == True:
        carbon.add_data(config.BACKEND_CONFIG['metric']+ fields, 1, ts)
        singleton.DataLogger.set_data(1) 
        print("전원ON서버전송")
    carbon.send_data()
    return None


def readSetting():
    with open('/home/ces/backend/start_action.yaml','r') as file:
    # with open('/home/ces_sanchez/backend/start_action.yaml','r') as file:
    # with open('/Users/hanjinjang/Desktop/Project/snowmelting/backend/start_action.yaml','r') as file:
        data = yaml.safe_load(file)
        readSet.read_condition = data['data']
        readSet.select_Check = data['select']
        readSet.radio_Check = data['radio']
        return None
    
##신규로직
def readManualSetting():
    with open('/home/ces/backend/manual_btn_status.yaml','r') as file:
        readManual.manual_value = yaml.safe_load(file)
        print(readManual.manual_value,"<><><><>manual_value<><><><>")
        return None
def readManualMode():
    with open('/home/ces/backend/manual_mode_status.yaml','r') as file:
        readManual.manual_mode = yaml.safe_load(file)
        print(readManual.manual_mode,"<><><><>manual_mode<><><><>")
        return None
    


def thread_test():
        print("타임오버!!가동종료!!")
        readSet.power =  0
        print(readSet.power,"<><><><>파워현황<><><><>")
        return None

class Operating:

    def __init__(self, num):
        self.num = num

    def operating_condition():
        oper_list = []
        for i in range(len(readSet.read_condition)):
            if readSet.read_condition[i]:
                oper_list.append(i)
        return min(oper_list)
    
    def end_operation():
        if readSet.load_Data >= readSet.select_Check:
            return True
        else:
            return False    

    def oper_bool():
        oper_condition = Operating.operating_condition()
        end_value = Operating.end_operation()
        if oper_condition <= readSet.load_Data and end_value:
            # singleton.DataLogger.set_data(1)
            return True
        else:
            # singleton.DataLogger.set_data(0)
            return False

    def operating():
        try:
            if not readManual.manual_mode:
                oper_bool = Operating.oper_bool()
                if oper_bool is None:  # test1 값이 None인 경우
                    raise ValueError("Error: operating_condition returned None")
                return sendOnOff(oper_bool)
            else:
                if readManual.manual_value:
                    return sendOnOff(True)
                else:
                    return sendOnOff(False)
        except ValueError as e:
            print(e)
    # def operating():
    #     test = False
    #     for i in range(len(readSet.read_condition)):
    #         if i == readSet.load_Data and readSet.read_condition[i]:
    #             # singleton.DataLogger.set_data(1)
    #             test = True
    #             print("가동!<><><><>파워현황<><><><>")
    #             if readSet.select_Check < 10:
    #                 if readSet.load_Data <= readSet.select_Check :
    #                     print(readSet.select_Check,"select_Check",readSet.load_Data)
    #                     test = False
    #                     # singleton.DataLogger.set_data(0)
    #                     print("휴동!<><><><>파워현황<><><><>")
    #             elif readSet.select_Check > 10:
    #                 t = threading.Timer(readSet.select_Check, thread_test)
    #                 t.start()
    #                 print("타이머 작동!!!")
    #         else:
    #             print("휴동!!")
    #     return sendOnOff(test)
    
functions = [get_road_conditions, readManualSetting, readManualMode , readSetting, Operating.operating]

def all():
    for function in functions:
        function()


# import schedule
# import time
# import threading

# def clear_file():
#     with open("/Users/hanjinjang/Desktop/unitTest/app.log", 'w') as file:
#         pass

# schedule.every(180).days.do(clear_file)

# def run_schedule():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# # Run the schedule in a separate thread
# thread = threading.Thread(target=run_schedule)
# thread.start()

# # You can do other tasks here
# print("The schedule is running in a separate thread.")