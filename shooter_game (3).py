
from pygame import *
from random import *
from time import time as timer# обовязково щоб працював таймер

#класс для завантаження спрайтів
class GameSprite(sprite.Sprite):
    #конструктор класу
    def __init__(self, player_image, player_x, player_y, width,height, speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image),(width,height))
        self.speed = speed
        
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    
    # Метод для відображення спрайту
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
  
# клас для управляння гравцем       
class Player(GameSprite):
    
    # метод у якому реалізовано управління персонажем
    def update(self):
        keys = key.get_pressed()
        
        if keys[K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width-80:
            self.rect.x += self.speed  
        # управління на мишку  
        pos = mouse.get_pos() 
        #self.rect.x = pos[0]-40
        #self.rect.y = pos[1]-40
      
    # метод пострілу.     
    def fire(self):
        #створити кулю
        bullet = Bullet("bullet.png", self.rect.centerx - 20, self.rect.y, 40,40, 10)
        bullets.add(bullet)# додати куля у групу
   
# клас для монстрів      
class Enemy(GameSprite):
    
    #метод переміщення ворогів циклічно
    def update(self):
        global lost
        
        self.rect.y += self.speed
        
        if self.rect.y > win_height + 50:
            self.rect.y = -50
            self.rect.x = randint(80, win_width -80)
            self.speed = randint(1,20)
             
            lost += 1
 
# клас переміщення кулі. Якщо куля  
class Bullet(GameSprite):
    
    def update(self):
        self.rect.y -= self.speed
        
        if self.rect.y < -50:
            self.kill()
            
bullets = sprite.Group()#група куль. Зручно звертатись до всіх одночасно
 

#клас бос
class Boss(GameSprite):
    #конструктор класу. На вхід приймає назву картинки, позиції, , кількість життів, швидкість польоту кулі
    def __init__(self, boss_image ,  boss_x, boss_y, size_x,size_y, live = 100, fire_speed = 10):
        super().__init__(boss_image ,  boss_x, boss_y, size_x,size_y, 0)
        self.live = live#життя
        self.startLive = live#кількість житів на початку 
        self.fire_speed = fire_speed# швидкість польоту кулі
        
        self.bossIsDead = False#статус живий бос чи ні
        self.bossBullets = sprite.Group() #група куль які буде вистрелювати бос
        self.last_time = 0#момент часу, коли востаннє був постріл
   
    # вся логіка боса
    def update(self):
        
        #якщо бос убитий, то метод припиняє роботу відразу
        if self.bossIsDead:
            return
        
        #якщо життя скінчились, то встановити статуст бос вбитий
        if self.live < 1:
            self.bossIsDead = True
            self.rect.y  = - 1000
        
        #розмальовка життів боса
        if self.live > self.startLive * 0.5:
            fill_color = (0,200, 0)
        elif self.live > self.startLive * 0.1:
            fill_color = (200,200, 0)
        else:
            fill_color = (200,0, 0)
        
        #відобразити здоровя боса
        text_live = font2.render("Boss: " + str(self.live),1,fill_color)
        window.blit(text_live,(10,150))
        
        #постріли боса щосекунди
        now_time = timer()
        if now_time - self.last_time > 1:
            bossBullet = Bullet("bullet.png",randint(self.rect.x, self.rect.right), self.rect.top + 150, 25, 35, -self.fire_speed)
            self.bossBullets.add(bossBullet)
            self.last_time = timer()
       
        #переміщення куль боса     
        self.bossBullets.draw(window)
        self.bossBullets.update()
        
        #відображення боса
        self.reset()
 
#створення боса із класу бос   
boss = Boss("boss2.png", 250, 0, 200,200, 50, 20 )

#клас анімацій 
class Anim(sprite.Sprite):
    #на вхід приймається назви папки , координати де необхідно відобразити анімацію, кількість спрайтів анімації
    def __init__(self,nameDirAnim,pos_x,pos_y,countSprite):
        sprite.Sprite.__init__(self)
        #завантаження спрайтів анімацій
        self.animation_set = [transform.scale(image.load(f"{nameDirAnim}/{i}.png"),(100,100)) for i in range(0, countSprite)]
        self.i = 0#лічильник кадрів
        self.x = pos_x# позиція х
        self.y = pos_y#позиція у
    
    #оновлення кадру
    def update(self):
        #відображення кадрів
        window.blit(self.animation_set[self.i], (self.x, self.y))
        self.i += 1
        if self.i > len(self.animation_set) - 1:
            self.kill()
#група анімацій
animsHit = sprite.Group()               
#клас для додавання зброї      
class Gun(GameSprite):
    #на вхід приймає картинку зборої, картинку кулі, корабиль за яким слідує зброя
    # розміри зброї та швидкість кулі
    def __init__(self, gun_image,bullet_image, player, size_x, size_y, fire_speed):
        super().__init__(gun_image, player.rect.x, player.rect.y, size_x, size_y, 0)  
        self.bullet_image = bullet_image#зберігаємо спрайт кул
        self.player = player#зерігаємо гравця
        self.fire_speed = fire_speed#швидкість кулі
    
    #переміщення зброї за гравцем. Можливість робити невеликий здвих для кращого відображення
    def update(self, shift_x = 0, shift_y=0):
        self.reset()
        self.rect.x = player.rect.x + shift_x
        self.rect.y = player.rect.y + shift_y
        
    #метож для пострілу
    def fire(self):
        bullet = Bullet(self.bullet_image, self.rect.centerx - 25, self.rect.y, 50,50, self.fire_speed)
        bullets.add(bullet)
      
      
      
        
win_width = 700
win_height = 500

window = display.set_mode((win_width, win_height))
display.set_caption("Shooter")
background = transform.scale(image.load("galaxy.jpg"),(win_width,win_height))

clock = time.Clock()
game = True
finish = False
#музику
mixer.init()
mixer.music.load("space.ogg")
fireSound = mixer.Sound("fire.ogg")
#mixer.music.play()
font.init()
font2 = font.SysFont("Ariel",35 )

score = 0
lost = 0

player = Player("rocket.png",50,380, 70,120, 10 )#Створюємо гравця
gun1 = Gun("spaceGun.png", "bullet.png",player, 50, 100, 10) #створюємо першу пушку
gun2 = Gun("spaceGun.png", "bullet.png",player, 50, 100, 10)#створюємо другу пушку
 
nameEnemy = ["ufo.png","asteroid.png","123.png","rocket2.png"]
monsters = sprite.Group()
for i in range(10): 
    monster = Enemy(choice(nameEnemy), randint(80, win_width-80),-30, 80,60, randint(1,10))
    monsters.add(monster)
 
    

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        
        
    
        if e.type == KEYDOWN:  
             
            if e.key == K_1:#якщо натиснути кнопку 1, то вмикається перший вид зброї
                gun1 = Gun("spaceGun.png", "bullet.png",player, 50, 100, 10) 
                gun2 = Gun("spaceGun.png", "bullet.png",player, 50, 100, 10)
            if e.key == K_2:#якщо натиснута кнопка 2, то вмикається другий вид зброї 
                gun1 = Gun("spaceGun2.png", "fire.png",player, 50, 100, 10) 
                gun2 = Gun("spaceGun2.png", "fire.png",player, 50, 100, 10)
                 
            if e.key == K_SPACE:
                #fireSound.play()
                #постріл 
                gun1.fire()
                gun2.fire()
                 
                
        
              
        
            
    if not finish:
        window.blit(background, (0,0))
        
        text = font2.render("Рахунок: "+ str(score), True, (0,0,200))
        window.blit(text,(10,20))
        
        text_lost = font2.render("Пропущено: "+ str(lost), True, (0,0,200))
        window.blit(text_lost,(10,50))
        
        monsters.update()
        monsters.draw(window)
        
        bullets.update()
        bullets.draw(window)
        
        player.reset()
        player.update()
        
        #оновлення відображення зброї
        gun1.update(-20,20)
        gun2.update(40,20)
        #оновлення анімацій
        animsHit.update() 
         
        
        if score > 30:#уомва відображення боса
            boss.update()#відображення боса
            if sprite.spritecollide(boss, bullets, True):#якщо куля потрапила у боса, то -1 до життів
                boss.live -= 1
        
        collide =  sprite.groupcollide(bullets,monsters, True,True)
        
        for i in collide:
  
            #створення анімацій влучання
            x, y = i.rect.x-50, i.rect.y-10#визначаємо координати куди влучили
            hit = Anim("boom",x,y,9)#створюємо анімацію
            animsHit.add(hit)#додаємо анфмацію у групу
            
            score+= 1
            monster = Enemy(choice(nameEnemy), randint(80, win_width-80),-50, 80,60, randint(1,10))
            monsters.add(monster)
            
        
        
    display.update()
    clock.tick(50)