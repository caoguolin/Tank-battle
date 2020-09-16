from os import remove
from random import randint
from sys import setprofile
import pygame
from pygame import fastevent
import time
import random
from pygame.sprite import Sprite

screen_width = 800
screen_height = 500
background_color = pygame.Color(0,0,0)
text_color = pygame.Color(255,0,0)

#定义一个基类
class BaseItem(Sprite):
    def __init__(self,color,width,height):
        pygame.sprite.Sprite.__init__(self)

class MainGame():
    window = None
    my_tank = None
    #存储敌方坦克的列表
    enemyTanklist = []
    #定义敌方坦克的数量
    enemyTankcount = 5
    #存储我方子弹的列表
    myBulletlist = []
    #存储敌方子弹的列表
    enemyBulletlist = []
    #存储爆炸效果的列表
    explodelist = []
    #存储墙壁的列表
    walllist = []
    def __init__(self):
        pass
    #开始游戏
    def startGame(self):
        #加载主窗口
        #初始化窗口
        pygame.display.init()
        #设置窗口的大小及显示
        MainGame.window=pygame.display.set_mode([screen_width,screen_height])
        #初始化我方坦克
        self.createmytank()
        #初始化敌方坦克，并将敌方坦克添加到列表中
        self.createEnemyTank()
        #初始化墙壁
        self.createwall()
        #设置窗口的标题
        pygame.display.set_caption('坦克大战')
        #一直显示
        while True:
            #使坦克移动的速度慢一点（循环执行得慢一点）
            time.sleep(0.02)
            #给窗口设置填充色
            MainGame.window.fill(background_color)
            #获取事件
            self.getEvent()
            #绘制文字
            MainGame.window.blit(self.getTextSurface('敌方坦克剩余数量:%d'%len(MainGame.enemyTanklist)),(10,10))
            #调用坦克显示的方法
            #判断我方坦克是否存活状态
            if MainGame.my_tank and MainGame.my_tank.live:
                MainGame.my_tank.displayTank()
            else:
                #删除我方坦克
                del MainGame.my_tank
                MainGame.my_tank = None
            #循环遍历敌方坦克列表，展示敌方坦克
            self.blitEnemyTank()
            #循环遍历显示我方坦克的子弹
            self.blitmyBullet()
            #循环遍历敌方敌方子弹
            self.blitenemyBullet()
            #循环遍历爆炸列表，展示爆炸效果
            self.blitexplode()
            #循环遍历墙壁列表，展示墙壁
            self.blitwall()
            #调用移动方法
            #判断：如果坦克的开关开启才可以移动
            if MainGame.my_tank and MainGame.my_tank.live:
                if not MainGame.my_tank.stop:
                    MainGame.my_tank.move()
                    #检测我方坦克是否与墙壁发生碰撞
                    MainGame.my_tank.hitwall()
                    #检测我方坦克是否与敌方坦克发生碰撞
                    MainGame.my_tank.mytank_hit_enemytank()
                    
            pygame.display.update()

    #创建墙壁的方法
    def createwall(self):
        for i in range(6):
            #初始化墙壁
            wall = Wall(i*130,220)
            #将墙壁添加到列表中
            MainGame.walllist.append(wall)

    #创建我方坦克的方法
    def createmytank(self):
        MainGame.my_tank = MyTank(350,300)
        #创建Music对象
        music = Music('img/start.wav')
        #播放
        music.playMusic()

    def createEnemyTank(self):
        top = 100
        #循环生成敌方坦克
        for i in range(MainGame.enemyTankcount):
            left = random.randint(0,600)
            speed = random.randint(1,4)
            enemy = EnemyTank(left,top,speed)
            MainGame.enemyTanklist.append(enemy)

    def blitEnemyTank(self):
        for EnemyTank in MainGame.enemyTanklist:
            #先判断敌方坦克是否活着
            if EnemyTank.live:
                EnemyTank.displayTank()
                EnemyTank.randMove()
                #检测敌方坦克是否与墙壁发生碰撞
                EnemyTank.hitwall()
                #检测敌方坦克是否与我方坦克发生碰撞
                if MainGame.my_tank and MainGame.my_tank.live:
                    EnemyTank.enemytank_hit_mytank()
                #敌方坦克发射子弹 
                EnemyBullet = EnemyTank.shot()
                #判断敌方子弹是否是None，如果不是则添加到列表
                if EnemyBullet:
                    #将敌方坦克子弹存储到列表中
                    MainGame.enemyBulletlist.append(EnemyBullet)
            else:
                MainGame.enemyTanklist.remove(EnemyTank)

    def blitmyBullet(self):
        for myBullet in MainGame.myBulletlist:
            #判断当前子弹的状态而选择进行显示与否
            if myBullet.live:
                myBullet.displayBullet()
                #调用子弹的移动方法
                myBullet.move()
                #调用检测我方子弹是否与敌方坦克发生碰撞
                myBullet.myBullet_hit_enemyTank()
                #检测我方坦克子弹是否与墙壁发生碰撞
                myBullet.hitwall()
            else:
                MainGame.myBulletlist.remove(myBullet)

    def blitenemyBullet(self):
        for enemyBullet in MainGame.enemyBulletlist:
            if enemyBullet.live:
                enemyBullet.displayBullet()
                enemyBullet.move()
                #调用敌方子弹与我方坦克碰撞的方法
                enemyBullet.enemybullet_hit_mytank()
                #检测敌方坦克子弹是否与墙壁碰撞
                enemyBullet.hitwall()
            else:
                MainGame.enemyBulletlist.remove(enemyBullet)

    def blitexplode(self):
        for explode in MainGame.explodelist:
            #判断是否活着
            if explode.live:
                #展示
                explode.displayExplode()
            else:
                #在爆炸列表中移除
                MainGame.explodelist.remove(explode)

    def blitwall(self):
        for wall in MainGame.walllist:
            #判断墙壁是否存活
            if wall.live:
                #调用墙壁的展示方法
                wall.displayWall()
            else:
                #从墙壁列表移除
                MainGame.walllist.remove(wall)

           
    #结束游戏
    def endGame(self):
        print('不再玩一会儿吗？')
        exit(0)

    #左上角文字的绘制
    def getTextSurface(self,text):
        #初始化字体模块
        pygame.font.init()
        #获取字体Font对象
        font = pygame.font.SysFont('kaiti',18)
        #绘制文本信息
        textSurface = font.render(text,True,text_color)
        return textSurface
    #获取事件
    def getEvent(self):
        eventlist=pygame.event.get()
        for event in eventlist:
            #判断按下的键是关闭还是键盘按下
            #如果按的是退出，关闭窗口
            if event.type == pygame.QUIT:
                self.endGame()
            if event.type == pygame.KEYDOWN:
                #当坦克死亡时
                if not MainGame.my_tank:
                    #按下的是esc键，让我方坦克重生
                    if event.key == pygame.K_ESCAPE:
                        #让我方坦克重生,调用创建我方坦克的方法
                        self.createmytank()
                if MainGame.my_tank and MainGame.my_tank.live:
                    #判断按下的是什么方向
                    if event.key == pygame.K_LEFT:
                        #切换方向
                        MainGame.my_tank.direction = 'L'
                        #修改坦克的开关状态
                        MainGame.my_tank.stop = False
                        # MainGame.my_tank.move()
                        # print('左，向左移动')
                    elif event.key == pygame.K_RIGHT:
                        MainGame.my_tank.direction = 'R'
                        MainGame.my_tank.stop = False
                        # MainGame.my_tank.move()
                        # print('右，向右移动')
                    elif event.key == pygame.K_UP:
                        MainGame.my_tank.direction = 'U'
                        MainGame.my_tank.stop = False
                        # MainGame.my_tank.move()
                        # print('上，向上移动')
                    elif event.key == pygame.K_DOWN:
                        MainGame.my_tank.direction = 'D'
                        MainGame.my_tank.stop = False
                        # MainGame.my_tank.move()
                        # print('下，向下移动')
                    elif event.key == pygame.K_SPACE:
                        # print('发射子弹')
                        #如果当前子弹列表小于限定值时，才可以进行创建
                        if len(MainGame.myBulletlist) < 3:
                            #创建我方坦克发射的子弹                    
                            myBullet = Bullet(MainGame.my_tank)
                            MainGame.myBulletlist.append(myBullet)
                            #添加我方坦克发射子弹音效
                            music = Music('img/hit.wav')
                            music.playMusic()

            #松开方向键，停止坦克移动，修改坦克的开关状态
            if event.type == pygame.KEYUP:
                #判断松开的键是方向键还是空格键
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    if MainGame.my_tank and MainGame.my_tank.live:
                        MainGame.my_tank.stop = True

class Tank(BaseItem):
    #添加距离左边left和距离上面top
    def __init__(self,left,top):
        #保存加载的图片
        self.images={
            'U':pygame.image.load('img/p1tankU.gif'),
            'D':pygame.image.load('img/p1tankD.gif'),
            'L':pygame.image.load('img/p1tankL.gif'),
            'R':pygame.image.load('img/p1tankR.gif'),
            }
        #方向
        self.direction='U'
        #根据当前图片的方向获取图片 surface
        self.image = self.images[self.direction]
        #根据图片获取区域
        self.rect = self.image.get_rect()
        #设置区域的left和top
        self.rect.left = left
        self.rect.top = top
        #速度决定移动的快慢
        self.speed = 10
        #坦克移动的开关
        self.stop = True
        #坦克存活状态
        self.live = True
        #新增属性原来坐标
        self.oldleft = self.rect.left
        self.oldtop = self.rect.top

    #移动
    def move(self):
        #移动后记录原始的坐标
        self.oldleft = self.rect.left
        self.oldtop = self.rect.top
        #判断坦克的方向进行移动
        if self.direction == 'L':
            if self.rect.left >0:
                self.rect.left -= self.speed
        elif self.direction == 'R':
            if self.rect.left + self.rect.height < screen_width:
                self.rect.left += self.speed
        elif self.direction == 'U':
            if self.rect.top >0:
                self.rect.top -= self.speed
        elif self.direction == 'D':
            if self.rect.top + self.rect.height < screen_height:
                self.rect.top +=self.speed

    def stay(self):
        self.rect.left = self.oldleft
        self.rect.top = self.oldtop

    #检测坦克是否与墙壁发生碰撞
    def hitwall(self):
        for wall in MainGame.walllist:
            if pygame.sprite.collide_rect(self,wall):
                #将坐标设置为移动之前的坐标
                self.stay()
    #射击
    def shot(self):
        return Bullet(self)
    #展示
    def displayTank(self):
        #获取展示的对象
        self.image = self.images[self.direction]
        #调用blit方法展示
        MainGame.window.blit(self.image,self.rect)
        
#我方坦克
class MyTank(Tank):
    def __init__(self,left,top):
        super(MyTank,self).__init__(left,top)

    #检测我方坦克与敌方坦克发生碰撞
    def mytank_hit_enemytank(self):
        #循环遍历敌方坦克列表
        for Enemytank in MainGame.enemyTanklist:
            if pygame.sprite.collide_rect(self,Enemytank):
                self.stay()

#敌方坦克
class EnemyTank(Tank):
    def __init__(self,left,top,speed):
        #调用父类的初始化方法
        super(EnemyTank,self).__init__(left,top)
        #加载图片集
        self.images = {
            'U':pygame.image.load('img/enemy1U.gif'),
            'D':pygame.image.load('img/enemy1D.gif'),
            'L':pygame.image.load('img/enemy1L.gif'),
            'R':pygame.image.load('img/enemy1R.gif')
        }
        #方向,随机生成敌方坦克的方向
        self.direction = self.randDirection()
        #根据方向获取图片
        self.image = self.images[self.direction]
        #区域
        self.rect = self.image.get_rect()
        #对left和top进行赋值
        self.rect.left = left
        self.rect.top = top
        #速度
        self.speed = speed
        #移动开关
        self.flag = True
        #步数变量
        self.step = 50
    
    #敌方坦克是否与我方坦克发生碰撞
    def enemytank_hit_mytank(self):
        if pygame.sprite.collide_rect(self,MainGame.my_tank):
            self.stay()

    #随机生成敌方坦克的方向
    def randDirection(self):
        num = random.randint(1,4)
        if num == 1:
            return 'U'
        elif num == 2:
            return 'D'
        elif num == 3:
            return 'L'
        elif num == 4:
            return 'R'

    #敌方坦克随机移动的方法
    def randMove(self):
        if self.step <= 0:
            self.direction = self.randDirection()
            #让步数复位
            self.step = 50
        else:
            self.move()
            #步数递减
            self.step -= 1

    #重写shot方法
    def shot(self):
        #随机生成数
        num = random.randint(0,100)
        if num < 5:
            return Bullet(self)


#子弹类
class Bullet(BaseItem):
    def __init__(self,tank):
        #加载图片
        self.image = pygame.image.load('img/enemymissile.gif')
        #坦克的方向决定子弹的方向
        self.direction = tank.direction
        #获取区域
        self.rect = self.image.get_rect()
        #子弹的left和top与方向有关
        if self.direction == 'U':
            self.rect.left = tank.rect.left + tank.rect.width/2 - self.rect.width/2
            self.rect.top = tank.rect.top - self.rect.height
        elif self.direction == 'D':
            self.rect.left = tank.rect.left + tank.rect.width/2 - self.rect.width/2
            self.rect.top = tank.rect.top + tank.rect.height
        elif self.direction == 'L':
            self.rect.left = tank.rect.left - self.rect.width/2 - self.rect.width/2
            self.rect.top = tank.rect.top + tank.rect.width/2 -self.rect.width/2
        elif self.direction == 'R':
            self.rect.left = tank.rect.left + tank.rect.width
            self.rect.top = tank.rect.top + tank.rect.width/2 -self.rect.width/2
        #子弹的速度
        self.speed = 6
        #子弹的状态，是否触碰墙壁，触碰则修改状态
        self.live = True

    #移动
    def move(self):
        if self.direction == 'U':
            if self.rect.top > 0:
                self.rect.top -= self.speed
            else:
                #修改状态
                self.live = False
        elif self.direction == 'D':
            if self.rect.top + self.rect.height < screen_height:
                self.rect.top += self.speed
            else:
                self.live = False
        elif self.direction == 'L':
            if self.rect.left > 0:
                self.rect.left -= self.speed
            else:
                self.live = False
        elif self.direction == 'R':
            if self.rect.left + self.rect.width < screen_width:
                self.rect.left += self.speed
            else:
                self.live = False
    
    #子弹是否碰撞墙壁
    def hitwall(self):
        #循环遍历墙壁列表
        for wall in MainGame.walllist:
            if pygame.sprite.collide_rect(self,wall):
                #修改子弹的生存状态，子弹消失
                self.live = False
                #墙壁的生命值减小
                wall.hp -= 1
                if wall.hp <= 0:
                    #修改墙壁的状态
                    wall.live = False

    #展示
    def displayBullet(self):
        #将图片surface加载到窗口
        MainGame.window.blit(self.image,self.rect)
    
    #我方子弹与敌方坦克的碰撞
    def myBullet_hit_enemyTank(self):
        #循环遍历敌方坦克列表，判断是否发生碰撞
        for EnemyTank in MainGame.enemyTanklist:
            if pygame.sprite.collide_rect(EnemyTank,self):
                #修改敌方坦克和我方子弹的状态
                EnemyTank.live = False
                self.live = False
                #创建爆炸对象
                explode = Explode(EnemyTank)
                #将爆炸对象添加到爆炸列表中
                MainGame.explodelist.append(explode)

    #敌方子弹与我方坦克的碰撞
    def enemybullet_hit_mytank(self):
        if MainGame.my_tank and MainGame.my_tank.live:
            if pygame.sprite.collide_rect(MainGame.my_tank,self):
                #产生爆炸对象
                explode = Explode(MainGame.my_tank)
                #将爆炸对象添加到爆炸列表中
                MainGame.explodelist.append(explode)
                #修改敌方子弹与我方坦克的状态
                self.live = False
                MainGame.my_tank.live = False


class Wall():
    def __init__(self,left,top):
        #加载墙壁图片
        self.image = pygame.image.load('img/steels.gif')
        #获取墙壁的区域
        self.rect = self.image.get_rect()
        #设置位置left,top
        self.rect.left = left
        self.rect.top = top
        #是否存活
        self.live = True
        #设置生命值
        self.hp = 3

    #展示墙壁的方法
    def displayWall(self):
        MainGame.window.blit(self.image,self.rect)

class Explode():
    def __init__(self,tank):
        #爆炸的位置由当前子弹打中的坦克位置决定
        self.rect = tank.rect
        self.images = [
            pygame.image.load('img/blast0.gif'),
            pygame.image.load('img/blast1.gif'),
            pygame.image.load('img/blast2.gif'),
            pygame.image.load('img/blast3.gif'),
            pygame.image.load('img/blast4.gif'),
        ]
        self.step = 0
        self.image = self.images[self.step]
        #是否存活状态
        self.live = True

    #展示爆炸效果的方法
    def displayExplode(self):
        if self.step < len(self.images):
            #根据索引获取爆炸对象
            self.image = self.images[self.step]
            self.step += 1
            #添加到主窗口
            MainGame.window.blit(self.image,self.rect)
        else:
            #修改状态
            self.live = False
            self.step = 0

class Music():
    def __init__(self,filename):
        self.filename = filename
        #初始化音乐混合器
        pygame.mixer.init()
        #加载音乐
        pygame.mixer.music.load(self.filename)

    #播放音乐
    def playMusic(self):
        pygame.mixer.music.play()


if __name__=='__main__':
    MainGame().startGame()

