from cmath import inf
import math
import os
import random
import pygame
from itertools import combinations
import config
from functools import cmp_to_key
from queue import PriorityQueue
import sys


class _Wrapper :
    def __init__(self,item,key) :
        self.item = item
        self.key = key
    def __lt__(self,other):
        return self.key(self.item)<other.key(other.item)
    def __eq__(self,other):
        return self.key(self.item)==other.key(other.item)
    
class kPriorityQueue(PriorityQueue):
    def __init__(self, key) :
        self.key=key
        super().__init__()
    def _get(self):
        wrapper=super()._get()
        return wrapper.item

    def _put(self,item):
        super()._put(_Wrapper(item,self.key))

class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]

class Aki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = []
        visited =[False]*len(coin_distance)
        queue=[]
        queue.append(0)
        visited[0]=True
        while queue :
            s = queue.pop()
            path.append(s)
            small = inf
            visited[s]=True
            ind =-1
            for i in range(1,len(coin_distance)):
                if visited[i]==False :
                    if coin_distance[s][i] < small:
                         small = coin_distance[s][i]
                         ind=i
            if ind!=-1 :
                queue.append(ind)

        return path+[0]


class Jocke(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        data=[]
        for i in range(1, len(coin_distance)):
            data.append(i)
        perm=[]
        for p in self.permutation(data):
            perm.append(p)
        ind=-1
        smallest=sys.maxsize-1
        for i in range(len(perm)):
            suma=0
            perm[i]=[0]+perm[i]+[0]
            for j in range(1,len(perm[i])):
                suma=suma+coin_distance[perm[i][j-1]][perm[i][j]]
            if(smallest>suma):
                smallest=suma
                ind=i
        return perm[ind]
    

    def permutation(self,lst):
        if len(lst) == 0:
         return []
        if len(lst) == 1:
         return [lst]
        l = [] 
        for i in range(len(lst)):
         m = lst[i]
         remLst = lst[:i] + lst[i+1:]
         for p in self.permutation(remLst):
           l.append([m] + p)
        return l



class Uki(Agent):
    def __init__(self, x, y, file_name):
            super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
            path = []
            pq=PriorityQueue()
            tupl=(0,1,0,[0])
            pq.put(tupl)
            while pq :
                pom=pq.get()
                suma,length,last,arr=pom
                if len(arr)==len(coin_distance)+1:
                    path=arr
                    break
                for i in range(1,len(coin_distance)):
                    if(len(arr)==len(coin_distance)):
                        sumica=suma+coin_distance[last][0]
                        tupl=(sumica,-len(arr),0,arr+[0])
                        pq.put(tupl)
                    else:
                        if(not (i in arr)):
                            tupl=(suma+coin_distance[last][i],-len(arr),i,arr+[i])
                            pq.put(tupl)
            return path
        
                    
class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def find(self,i,parent):
        while parent[i] != i:
         i = parent[i]
        return i

    def union(self,i, j,parent):
     a = self.find(i,parent)
     b = self.find(j,parent)
     parent[a] = b

    def kruskalMST(self,cost,parent,arr):
     mincost = 0 # Cost of min MST
     pomcost=[]
     #parent = [i for i in range(len(cost))]
     for i in range(len(cost)):
       a=[]
       for j in range(len(cost)):
            a.append(cost[i][j])
       pomcost.append(a)
     for i in range(1,len(arr)-1):
        for j in range(len(cost)):
            pomcost[arr[i]][j]=0
            pomcost[j][arr[i]]=0
     for i in range(len(cost)):
        parent[i] = i
     edge_count = 0
     while edge_count < len(cost) - 1:
        min = inf
        a = -1
        b = -1
        for i in range(len(pomcost)):
            for j in range(len(pomcost)):
                if pomcost[i][j]!=0 and  self.find(i,parent) != self.find(j,parent) and pomcost[i][j] < min :
                    min = pomcost[i][j]
                    a = i
                    b = j
        self.union(a, b,parent)
        edge_count += 1
        if(min!=inf):
            mincost += min
     return mincost 


    def get_agent_path(self, coin_distance):
        parent = [i for i in range(len(coin_distance))]
        path = []
        pq=PriorityQueue()
        tupl=(0,1,0,[0],0)
        pq.put(tupl)
        while pq :
                pom=pq.get()
                suma,length,last,arr,heur=pom
                if len(arr)==len(coin_distance)+1:
                    path=arr
                    break
                for i in range(1,len(coin_distance)):
                    if(len(arr)==len(coin_distance)):
                        sumica=suma+coin_distance[last][0]
                        heurr=self.kruskalMST(coin_distance,parent,arr)
                        tupl=(sumica+heurr,-len(arr),0,arr+[0],sumica)
                        pq.put(tupl)
                    else:
                        if(not (i in arr)):
                            heurr=self.kruskalMST(coin_distance,parent,arr)
                            tupl=(suma+coin_distance[last][i]+heurr,-len(arr),i,arr+[i],suma+coin_distance[last][i])
                            pq.put(tupl)
        return path



                
         