#!/usr/bin/env python
# coding: utf-8

# In[227]:


class Data:
    def __init__(self, dataID:int, time:int, size:int):
        self.dataID = dataID
        self.time = time
        self.size = size
        self.status = "WAIT"
        
    def clear(self):
        self.status = "WAIT"
    
    def run(self):
        self.status  = "RUNNING"
    
    def done(self):
        self.status = "DONE"
        
    def __str__(self):
        return str(self.dataID) + "\t" + str(self.time) + "\t" + str(self.size) + "\t" + self.status + "\n"
    
class Storage:
    def __init__(self, storeID:int, size:int):
        self.storeID = storeID
        self.size = size
        self.free = True
        
    def use(self):
        self.free = False
    
    def release(self):
        self.free = True
    
    def __str__(self):
        return str(self.storeID) + "\t" + str(self.size) + "\t" + ("FREE" if self.free else "IN USE") + "\n"
    
class Timer:
    def __init__(self, data:Data, storage:Storage):
        self.data = data
        self.storage = storage
        self.time = data.time
        
    def run(self) -> bool:
        if self.time > 0:
            self.data.run()
            self.storage.use()
            self.time-=1
            return False
        else:
            self.data.done()
            self.storage.release()
            return True
        
    def __str__(self):
        return str(self.data.dataID) + "\t" + str(self.storage.storeID)
        
class File:
    def __init__(self):
        self.dList = []
        self.sList = []
        
    def readFile(self, filename:str, filetype:str):
        with open(filename,'r') as file:
            process = file.read()
        process = " ".join(process.split())
        process = process + " "
        
        while len(process) != 0:
            if filetype == "data":
                data = int(process[:process.find(" ")])
                process = process[process.find(" ") + 1:]
                time = int(process[:process.find(" ")])
                process = process[process.find(" ") + 1:]
                size = int(process[:process.find(" ")])
                process = process[process.find(" ") + 1:]
                self.dList.append(Data(data,time,size))
            elif filetype == "storage":
                storage = int(process[:process.find(" ")])
                process = process[process.find(" ") + 1:]
                size = int(process[:process.find(" ")])
                process = process[process.find(" ") + 1:]
                self.sList.append(Storage(storage,size))
        
class Controller:
    def __init__(self):
        self.dList = []
        self.sList = []
        self.queue = []

    def simulateFirstFit(self):
        self.clearDataList()
        self.queue.clear()
        FF = []
        qua = 0
        throughput = []
        storageUtil = []
        queueLength = []
        qWaitingTime = []
        qMaxLength = len(self.dList)
        while True:
            flag = True
            for q in self.queue:
                if q.run():
                    self.queue.remove(q)
                    self.dList[self.dList.index(q.data)].done()
                    self.sList[self.sList.index(q.storage)].release()
            for data in self.dList:
                if data.status == "WAIT":
                    flag = False
                    for store in self.sList:
                        if store.free and data.size <= store.size:
                            FF.append({"data":data.dataID, "memory block":store.storeID})
                            store.use()
                            data.run()
                            storageUtil.append((store.size-data.size)/store.size)
                            qMaxLength-=1
                            qWaitingTime.append(qua)
                            self.addQueue(data,store)
                            break
                    if data.status == "WAIT":
                        for i in range(0,len(self.sList)):
                            if i < len(self.sList) - 1:
                                if self.sList[i].free and self.sList[i+1].free:
                                    if data.size <= (self.sList[i].size + self.sList[i+1].size):
                                        FF.append({"data":data.dataID, "memory block":self.sList[i].storeID})
                                        FF.append({"data":data.dataID, "memory block":self.sList[i+1].storeID})
                                        self.sList[i].use()
                                        self.sList[i+1].use()
                                        data.run()
                                        storageUtil.append((self.sList[i].size + self.sList[i+1].size - data.size)/(self.sList[i].size + self.sList[i+1].size))
                                        qMaxLength-=1
                                        qWaitingTime.append(qua)
                                        self.addQueue(data,self.sList[i])
                                        self.addQueue(data,self.sList[i+1])
            throughput.append(len(self.queue))
            queueLength.append(qMaxLength)
            if flag and len(self.queue) == 0:
                break
            qua+=1
        print("--------------------------------\n\tFIRST FIT SCHEME\n--------------------------------")
        self.printDetails(qua, throughput, storageUtil, queueLength, qWaitingTime)
        
    def simulateWorstFit(self):
        self.clearDataList()
        self.queue.clear()
        WF = []
        throughput = []
        storageUtil = []
        qua = 0
        queueLength = []
        qWaitingTime = []
        qMaxLength = len(self.dList)
        while True:
            flag = True
            for q in self.queue:
                if q.run():
                    self.queue.remove(q)
                    self.dList[self.dList.index(q.data)].done()
                    self.sList[self.sList.index(q.storage)].release()
            for data in self.dList:
                largest = 0
                largeIndex = 0
                if data.status == "WAIT":
                    flag = False
                    combFlag = False
                    for store in self.sList:
                        if store.free and data.size <= store.size:
                            if largest < (store.size - data.size):
                                largest = store.size - data.size
                                largeIndex = self.sList.index(store)
                    if largest == 0 and data.status == "WAIT":
                        combFlag = True
                        for i in range(0,len(self.sList)):
                            if i < len(self.sList) - 1:
                                if self.sList[i].free and self.sList[i+1].free:
                                    if data.size <= (self.sList[i].size + self.sList[i+1].size):
                                        if largest < (self.sList[i].size + self.sList[i+1].size - data.size):
                                            largest = self.sList[i].size + self.sList[i+1].size - data.size
                                            largeIndex = i
                    if largest != 0 and not combFlag:
                        WF.append({"data":data.dataID, "memory block":self.sList[largeIndex].storeID})
                        self.sList[largeIndex].use()
                        data.run()
                        storageUtil.append((self.sList[largeIndex].size - data.size)/self.sList[largeIndex].size)
                        qMaxLength-=1
                        qWaitingTime.append(qua)
                        self.addQueue(data,self.sList[largeIndex])
                    if largest != 0 and combFlag:
                        WF.append({"data":data.dataID, "memory block":self.sList[largeIndex].storeID})
                        WF.append({"data":data.dataID, "memory block":self.sList[largeIndex+1].storeID})
                        self.sList[largeIndex].use()
                        self.sList[largeIndex+1].use()
                        data.run()
                        qWaitingTime.append(qua)
                        storageUtil.append((self.sList[largeIndex].size + self.sList[largeIndex+1].size - data.size)/(self.sList[largeIndex].size + self.sList[largeIndex+1].size))
                        qMaxLength-=1
                        self.addQueue(data,self.sList[largeIndex])
                        self.addQueue(data,self.sList[largeIndex+1])
            throughput.append(len(self.queue))
            queueLength.append(qMaxLength)
            if flag and len(self.queue) == 0:
                break
            qua+=1
        print("--------------------------------\n\tWORST FIT SCHEME\n--------------------------------")
        self.printDetails(qua, throughput, storageUtil, queueLength, qWaitingTime)
    
    def simulateBestFit(self):
        self.clearDataList()
        self.queue.clear()
        self.sList.sort(key=self.sizeKey)
        BF = []
        throughput = []
        storageUtil = []
        queueLength = []
        qWaitingTime = []
        qMaxLength = len(self.dList)
        qua = 0
        while True:
            flag = True
            for q in self.queue:
                if q.run():
                    self.queue.remove(q)
                    self.dList[self.dList.index(q.data)].done()
                    self.sList[self.sList.index(q.storage)].release()
            for data in self.dList:
                if data.status == "WAIT":
                    flag = False
                    for store in self.sList:
                        if store.free and data.size <= store.size:
                            BF.append({"data":data.dataID, "memory block":store.storeID})
                            store.use()
                            data.run()
                            storageUtil.append((store.size - data.size)/store.size)
                            qMaxLength-=1
                            qWaitingTime.append(qua)
                            self.addQueue(data,store)
                            break
                    if data.status == "WAIT":
                        for i in range(0,len(self.sList)):
                            if i < len(self.sList) - 1:
                                if self.sList[i].free and self.sList[i+1].free:
                                    if data.size <= (self.sList[i].size + self.sList[i+1].size):
                                        BF.append({"data":data.dataID, "memory block":self.sList[i].storeID})
                                        BF.append({"data":data.dataID, "memory block":self.sList[i+1].storeID})
                                        self.sList[i].use()
                                        self.sList[i+1].use()
                                        data.run()
                                        storageUtil.append((self.sList[i].size + self.sList[i+1].size - data.size)/(self.sList[i].size + self.sList[i+1].size))
                                        qWaitingTime.append(qua)
                                        qMaxLength-=1
                                        self.addQueue(data,self.sList[i])
                                        self.addQueue(data,self.sList[i+1])
            throughput.append(len(self.queue))
            queueLength.append(qMaxLength)
            if flag and len(self.queue) == 0:
                break
            qua+=1
        print("--------------------------------\n\tBEST FIT SCHEME\n--------------------------------")
        self.printDetails(qua, throughput, storageUtil, queueLength, qWaitingTime)
    
    @staticmethod
    def sizeKey(elem):
        return elem.size
    
    def clearDataList(self):
        for data in self.dList:
            data.clear()
    
    def addData(self, dataID:int, time:int, size:int):
        self.dList.append(Data(dataID,time,size))
        
    def addStorage(self, storeID:int, size:int):
        self.sList.append(Storage(storeID,size))
        
    def addQueue(self, data:Data, storage:Storage):
        self.queue.append(Timer(data,storage))
        
    def addFileData(self, f:File):
        self.addDataList(f.dList)
        self.addStorageList(f.sList)
        
    def addDataList(self, l:list):
        self.dList+=l
    
    def addStorageList(self, s:list):
        self.sList+=s
        
    def printQueue(self, js:list)->str:
        data = "\tJOB SCHEDULE ORDER\nDATA ID\t\tMEMORY BLOCK\n"
        for i in js:
            data+=(str(i["data"]) + "\t\t" + str(i["memory block"]) + "\n")
        return data
    
    def printDetails(self, q:int, throughput:list, storageUtil:list, queueLength:list, qWaitingTime:list):
        print("AVERAGE THROUGHPUT: " + str(round(sum(throughput)/q, 2)))
        print("AVERAGE UNUSED STORAGE: " + str(round((sum(storageUtil)/len(storageUtil)) * 100, 2)) + "%")
        print("AVERAGE USED STORAGE: " + str(round((1 - (sum(storageUtil)/len(storageUtil))) * 100 , 2)) + "%")
        print("AVERAGE QUEUE LENGTH: " + str(round(sum(queueLength)/len(queueLength),2)))
        print("AVERAGE QUEUE WAITING TIME: " + str(round(sum(qWaitingTime)/len(qWaitingTime),2)))
        print("--------------------------------")
    def __str__(self):
        data = "\tDATA\nJOB ID\tTIME\tSIZE\n"
        for i in self.dList:
            data+=str(i)
        data+="---------------------\n\tMEMORY\nSTOREID\tSIZE\n"
        for i in self.sList:
            data+=str(i)
        return data
        


# In[228]:


f = File()
f.readFile("jobData.txt","data")
f.readFile("storageData.txt","storage")
c = Controller()
c.addFileData(f)
c.simulateFirstFit()
c.simulateWorstFit()
c.simulateBestFit()


# In[ ]:




