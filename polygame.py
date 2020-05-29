import numpy as np
import sys

# -*- coding: utf-8 -*-

#用列表实现栈
class Stack(object):
    def __init__(self):
        self.stack = []

    def push(self, value):    # 进栈
        self.stack.append(value)

    def pop(self):  #出栈
        if self.stack:
            self.stack.pop()
        else:
            raise LookupError('stack is empty!')

    def is_empty(self): # 如果栈为空
        return bool(self.stack)

    def top(self): 
        #取出目前stack中最新的元素
        return self.stack[-1]

#定义多边形类
class PloygonAgent(object):
    def __init__(self,n,m,op = [], v = []):
       
        super().__init__()
        self.__n = n              #多边形边数

        self.__m =  m             #此位置定义一个三维数组存取    
                                #[][][] m; //m[i][n][1]：
                                # 代表一开始删除第i条边，长度为n的链（包含n个顶点），
                                # 所能得到的最大值
                                #m[i][n][0]：代表一开始删除第i条边，
                                # 长度为n的链，所能得到的最小值     
  
        self.__op = op            #每条边对应操作数
        self.__v = v              #每个顶点数值
        self.__cut = [[[0] *(n+1)]*n+2]*2   #记录合并点的数组
        self.__bestScore = 0                #记录最优得分
        self.__firstDelEdge = 0             #记录最优情况下，第一条删除的边
                                            #此处定义一个栈(python实现方式)
        self.__stack = Stack()                   #用栈保存合并边的顺序

    def minMax(self,i,s,j,resDict):
        r = (i+s-1) % self.n + 1
        a = self.m[i][s][0]     #i->s 的链能取得的最小值        
        b = self.m[i][s][1]     #i->s 的链能取得的最大值
        c = self.m[r][j-s][0]   #->j-s 的链能取得的最小值
        d = self.m[r][j-s][1]   #->j-s 的链能取得的最大值
        if(self.__op[r] == '+'):
            #用字典实现HashMap
            resDict['minf'] = a+c
            resDict['maxf'] = b+d
        else:
            e = [0,a*c,a*d,b*c,b*d]
            minf = e[1]
            maxf = e[1]
            k = 2
            while(k < 5):
                if(minf > e[k]): 
                    minf = e[k]
                if(maxf < e[k]):
                    maxf = e[k]
                ++k
            resDict['minf'] = minf
            resDict['maxf'] = maxf 
        return resDict

    #获取多边形的最高得分
    def polyMax(self):
        resDict = {}
        n = self.__n
        for j in range(2,n + 1):
            for i in range(1, n +1):
                self.__m[i][j][0] = sys.maxsize             #取得python整型最大值
                self.__m[i][j][1] = -sys.maxsize - 1        #取得python整型最小值
                for s in range(1, j):
                    resDict = self.minMax(i,s,j,resDict)
                    if(self.__m[i][j][0] > resDict['minf']):
                        self.__m[i][j][0] = resDict['minf']
                        self.__cut[i][j][0] = s            #记录该链取得最小值得断点
                    if(self.__m[i][j][1] < resDict['maxf']):
                        self.__m[i][j][1] = resDict['maxf']
                        self.__cut[i][j][1] = s            #记录该链取得最大值得断点
            
        self.__bestScore = self.__m[1][n][1]
        self.__firstDelEdge = 1                     #一开始删除的边，默认为第一条边
        
        for i in range(2,n + 1):
            if(self.__bestScore < self.__m[i][n][i]):
                self.__bestScore = self.__m[i][n][1]
                self.__firstDelEdge = i         #如果一开始删除第i边有更优结果，则更新
        for i in range(1,n + 1):
            print("i= %d  %d",i,self.__m[i][n][1])
        print("firstDelEdge= ",self.__firstDelEdge)
        self.getBestSolution(self.__firstDelEdge,self.__n,True)
        while(self.__stack.is_empty()):
            str_list = "".join(self.__stack.pop())
            print("stack--> ",str_list)
            
        return self.__bestScore

    #获取最优的合并序列，存入stack中
    #@parm i 指子链从哪个顶点开始4
    #@parm j 指子链的长度
    #@parm needMax 是否取子链的最大值，如果传入值为false，则取最小值
    def getBestSolution(self,i,j,needMax):
        s = 0
        r = 0
        n = self.__n
        m = self.__m
        #如果只有1个顶点，直接返回
        if(j == 1):
            return
        #如果只有2个顶点，没有子链，无须递归
        if(j == 2):
            s = self.__cut[i][j][1]
            r = (i+s-1) % n + 1
            self.__stack.push(r)
            return
        
        #当链中有2个以上的顶点，将最优的边入栈
        if(needMax):
            s = self.__cut[i][j][1]
        else:
            s = self.__cut[i][j][0]
        pass
        
        r = (i+s-1) % n + 1 
        self.__stack.push(r)
        if(self.__op[r] == '+'):
            if(needMax): #如果合并得到的父链需要取得最大值
                self.getBestSolution(i,s,True)
                self.getBestSolution(r,j-s,True)
            else:       #如果合并得到的父链需要得到最小值
                self.getBestSolution(i,s,False)
                self.getBestSolution(r,j-s,False)
        else:
            a = m[i][s][0]
            b = m[i][s][1]
            c = m[r][j-s][0]
            d = m[r][j-s][1]
            e = [0,a*c,a*d,b*c,b*d] #最大最小值的数组
            mergeMax = e[1]
            mergeMin = e[1]
            merge = 0
            for k in range(2,5):
                if(e[k] > mergeMax):
                    mergeMax = e[k]
                if(e[k] < mergeMin):
                    mergeMin = e[k]
            if(needMax):
                merge = mergeMax
            else:
                merge = mergeMin
            #递归
            if(merge == e[1]): #子链1、2都取最小值
                self.getBestSolution(i,s,False)
                self.getBestSolution(r,j-s,False)
            elif(merge == e[2]):#子链1取最小，子链2取最大
                self.getBestSolution(i,s,False)
                self.getBestSolution(r,j-s,True)
            elif(merge == e[3]):#子链1取最大，子链2取最小
                self.getBestSolution(i,s,True)
                self.getBestSolution(r,j-s,False)
            else:#子链1取最大，子链2取最大
                self.getBestSolution(i,s,True)
                self.getBestSolution(r,j-s,True)

    def showPolygon(self):
        print("哈哈哈，我没开发，别打我。。")
        
        pass

if __name__ == "__main__":
    pass
