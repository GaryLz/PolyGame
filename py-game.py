# -*- coding: utf-8 -*-
import pygame
import pygame_menu
import random
import numpy as np
import sys

# 窗口大小
WINDOW_SIZE = (640, 480)
FPS = 60.0

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
class PolygonAgent(object):
	def __init__(self,n,m,op = [], v = []):
	   
		super().__init__()
		self.__n = n              #多边形边数

		self.__m = m             #此位置定义一个三维数组存取    
								#[][][] m; //m[i][n][1]：
								# 代表一开始删除第i条边，长度为n的链（包含n个顶点），
								# 所能得到的最大值
								#m[i][n][0]：代表一开始删除第i条边，
								# 长度为n的链，所能得到的最小值     
  
		self.__op = op            #每条边对应操作数
		self.__v = v              #每个顶点数值
		self.__cut = np.zeros((n+1, n+1, 2))   #记录合并点的数组
		self.__bestScore = 0                #记录最优得分
		self.__firstDelEdge = 0             #记录最优情况下，第一条删除的边
											#此处定义一个栈(python实现方式)
		self.__stack = Stack()                   #用栈保存合并边的顺序
		self.__memorystack = []             #记录每次走的情况

	def minMax(self,i,s,j,resDict):
		r = (i+s-1) % self.__n + 1 
		a = self.__m[i][s][0]     #i->s 的链能取得的最小值        
		b = self.__m[i][s][1]     #i->s 的链能取得的最大值
		c = self.__m[r][j-s][0]   #->j-s 的链能取得的最小值
		d = self.__m[r][j-s][1]   #->j-s 的链能取得的最大值
		if(self.__op[r] == '+'):
			#用字典实现HashMap
			resDict['minf'] = a+c
			resDict['maxf'] = b+d
		if(self.__op[r] == '*'):
			e = [0,a*c,a*d,b*c,b*d]
			minf = e[0]
			maxf = e[0]
			k = 1
			while(k < 5):
				if(minf > e[k]): 
					minf = e[k]
				if(maxf < e[k]):
					maxf = e[k]
				k+=1
			resDict['minf'] = minf
			resDict['maxf'] = maxf 
		#print(resDict)
		return resDict

	#获取多边形的最高得分
	def polyMax(self):
		resDict = {}
		n = self.__n
		for j in range(2,n + 1):
			for i in range(1, n +1):
				self.__m[i][j][0] = sys.maxsize             #取得python整型最大值
				self.__m[i][j][1] = -sys.maxsize            #取得python整型最小值
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
			if(self.__bestScore < self.__m[i][n][1]):
				self.__bestScore = self.__m[i][n][1]
				self.__firstDelEdge = i         #如果一开始删除第i边有更优结果，则更新
		for i in range(1,n + 1):
			print("i=",i,self.__m[i][n][1])
		print("firstDelEdge= ",self.__firstDelEdge)
		self.getBestSolution(self.__firstDelEdge,self.__n,True)
		while(self.__stack.is_empty()):
			top = int(self.__stack.top())
			self.__stack.pop()
			print("stack--> ",top)
			
		return int(self.__bestScore)

	#获取最优的合并序列，存入stack中
	#@parm i 指子链从哪个顶点开始4
	#@parm j 指子链的长度
	#@parm needMax 是否取子链的最大值，如果传入值为false，则取最小值
	def getBestSolution(self,i,j,needMax):
		s = 0
		r = 0
		n = self.__n
		m = self.__m
		j = int(j)
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
		
		r = (i+s-1) % n + 1 
		r = int(r)
		self.__stack.push(r)
		if(self.__op[r] == '+'):
			if(needMax): #如果合并得到的父链需要取得最大值
				self.getBestSolution(i,s,True)
				self.getBestSolution(r,j-s,True)
			else:       #如果合并得到的父链需要得到最小值
				self.getBestSolution(i,s,False)
				self.getBestSolution(r,j-s,False)
		else:
			s=int(s)
			a = m[i][s][0]
			b = m[i][s][1]
			c = m[r][j-s][0]
			d = m[r][j-s][1]
			e = [0,a*c,a*d,b*c,b*d] #最大最小值的数组
			mergeMax = e[0]
			mergeMin = e[0]
			merge = 0
			for k in range(1,5):
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

	def showList(self,opt = [],val = []):
		n = len(val)
		track = ""
		for i in range(1,n):
			print(val[i],end = ' ')
			track = track + str(val[i])
			if i != n-1:
				print(opt[i],end = ' ')
				track = track + " "+opt[i]+" "
		self.__memorystack.append(track)
		print('\n')
			

	def showPolygon(self, slen):
		n = self.__n
		v = self.__v
		op = self.__op
		arg = slen
		
		#第一行
		for i in range(n):
			if i != n-1:
				print("|{}|--{}--".format(v[i+1], op[i+2]), end='')    
			else:
				print("|",end= '')
				print(v[n],end='') #最后一个变量值
				print("|")
		
		j = 6*(n-1)+arg #字符占位数
		
		#第二行
		for i in range(j):
			if (i==0 or i==j-1):
				print('|', end = '')
			else:
				print(' ', end = '')
		
		print() #newline
			
		#第三行
		for i in range(j):
			
			if (i==0 or i==j-1):
				print(' ', end = '')
			elif (i==int(j/2)):
				print(op[1], end='')
			else:
				print('-', end='')
				
		print("\n") #newline

		
	def play(self):
		n = self.__n
		val = list.copy(self.__v)
		opt = list.copy(self.__op)
		first = int(input("choose the first arc to delete: "))
		opt.pop(first)            
		for i in range(1,first):
			recordV = val[1]           #记录第一个数
			recordOpt = opt[1]         #记录第一个操作符
			for s in range(1,n):
				if s == n-1:
					opt[s] = recordOpt
					continue
				opt[s] = opt[s+1]
			for j in range(1,n+1):    #从first点开始左移直到first 为第一个数
				if j == n:
					val[j] = recordV
					continue
				val[j] = val[j+1]
		while(1):
			self.showList(opt,val)
			if len(val) == 2:
				break
			self.chanceAre(opt,val)
	
	def chanceAre(self,opt = [],val = []):
		cut = int(input("choose the point you want to cut:"))
		if opt[cut] == '+':
			result = val[cut] + val[cut+1]
		elif opt[cut] == '*':
			result = val[cut] * val[cut+1]
		opt.pop(cut)
		val[cut] = result
		val.pop(cut+1)

	def translate2list(self,str = "",opt = [],val = []):
		topt = opt     
		tval = val
		memeryList = list(str.split())     #将字符串记录转化成List
		memeryListLen = int((len(memeryList)+1)/2) 
		for i in range(0,memeryListLen):
			tval.append(int(memeryList[2*i]))
			if (i!=0) :
				topt.append(memeryList[2*i-1])

def go_back_func():
	print("回步回步")

def best_solution():
	print("最佳走法")

def restart_game():
	print("重新开始游戏")

def main_background():
	global surface
	surface.fill((128, 0, 128))
	
def main():
	
	global pygame_menu
	global surface
	global clock
	
	# 初始化游戏
	pygame.init()
	
	# 创建窗口
	surface = pygame.display.set_mode(WINDOW_SIZE)
	pygame.display.set_caption('Game Mode')
	clock = pygame.time.Clock()
	
	
	'''
	创建菜单: 游戏中菜单
	- 回步
	- 最佳演示
	- 重新开始
	- 返回
	'''	
	game_menu = pygame_menu.Menu(
		height = WINDOW_SIZE[1]*0.5,
		onclose = pygame_menu.events.DISABLE_CLOSE,
		title='Game Menu',
		width = WINDOW_SIZE[0]*0.5,
	)
	
	submenu_theme = pygame_menu.themes.THEME_DEFAULT.copy()
	submenu_theme.widget_font_size = 10
	game_submenu = pygame_menu.Menu(
		height=WINDOW_SIZE[1] * 0.3,
		theme=submenu_theme,
		title='Submenu',
		width=WINDOW_SIZE[0] * 0.3,
	)
	
	game_submenu.add_button('回步', go_back_func)
	game_submenu.add_button('最佳演示', best_solution)
	game_submenu.add_button('重新开始', restart_game)
	game_submenu.add_button('返回', pygame_menu.events.BACK)
	
	
	while True:
		clock.tick(FPS)
		
		# 背景draw
		main_background() #可换draw_backgroud() bgcolor
		
		# 捕捉事件events-判定事件
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				exit()
			#elif event.type == 
				
		# Game_menu
		game_menu.mainloop(surface, main_background, disable_loop=test, fps_limit=FPS)
		
		# Flip surface
		pygame.display.flip()

		# At first loop returns
		#if test:
			#pass
			#break
	
if __name__ == '__main__':
	main()



