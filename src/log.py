import os
class Log():
    def __init__(self,path):
        self._canLog = False
        self.LOGS:dict[str,list] = {}
        self.PATH = path
        if not os.path.isdir(path):
            os.makedirs(path)

    @property
    def canLog(self):
        return self._canLog

    @canLog.setter
    def canLog(self, new_value):
        self._canLog = new_value
        self.on_change(new_value)

    def on_change(self,new_value):
        if(new_value):
            self.__log()

    def create_log(self,key:str):
        if not self.has_key(key):
            self.LOGS[key] = []

    def add_entry(self,key,entry):
        self.create_log(key)
        self.LOGS[key].append(entry)
        if self._canLog:
            self.__log()            

    def __log(self):
        for log in self.LOGS:
            #print(f"Antes:\t{self.LOGS[log]}")
            if self.LOGS[log]:
                aux = self.LOGS[log].copy()
                file = os.path.join(self.PATH,log)
                #print(file)
                with open(file,'a') as f_log:
                    for entry in aux:
                        f_log.write(entry)
                        if entry in aux:
                            self.LOGS[log].remove(entry)
                        f_log.flush()
            #print(f"Depois:\t{self.LOGS[log]}")
    def has_key(self,key):
        return self.LOGS.__contains__(key)
    def __str__(self):
        return str(self.LOGS)