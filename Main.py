"""acc controller."""

from numpy.compat.py3k import contextlib_nullcontext
from controller import Robot
from controller import Motor
from controller import Camera, GPS, InertialUnit
from controller import CameraRecognitionObject
from vehicle import Driver
from controller import Node
from matplotlib import pyplot as plt
from Plot import DynamicUpdate
import threading
from curva import curva
import numpy as np
import time
global loc, IMU, lm, lista_cone_amarelo, lista_cone_amarelo_position, lista_cone_azul, lista_cone_azul_position, lista_cone_laranja, lista_cone_laranja_position
global lista_car_position, TIME_STEP, TIME_STEP_GPS, MAX_SPEED, exitFlag, c1, camera, id_freio, rd_esq, rd_dir,speed
global count_amarelo, lista_curva
exitFlag = 0

# Função para calcular erro percentual
def erro(x1,x2):
        if x1>x2:
            return np.absolute(((x1-x2)*100)/x2)
        else:
            return np.absolute(((x2-x1)*100)/x1)

# Classe para fazer threads, possibilidando rodar duas funções simultaneamentes.
class myThread(threading.Thread):

  def __init__(self, func):
    threading.Thread.__init__(self)
    self.func = func

  def run(self):
    if self.func == 'robo':
        robo()
    if self.func == 'grafico':
        gera_grafico()


TIME_STEP = 64 # Frequencia de atualização do programa
MAX_SPEED = 6.28 # auxiliar de velocidade

# Declaração das Variaveis do sistema
robot = Robot() # Variavel da classe Robot, que controla todos os componentes do carro (motores)
rm = robot.getDevice('Right Motor') # Variavel para controlar o motor direito do carro
rm.setPosition(float('inf'))
rm.setVelocity(0*MAX_SPEED)
lm = robot.getDevice('Left Motor') # Variavel para controlar o motor esquerdo do carro
lm.setPosition(float('inf'))
lm.setVelocity(0*MAX_SPEED)

rd_esq = robot.getDevice('left_steer') # Variavel que controla o angulo da roda dianteira esquerda
rd_esq.setPosition(0.0)
rd_dir = robot.getDevice('right_steer') # Variavel que controla o angulo da roda dianteira direita
rd_dir.setPosition(0.0)
lista_cone_laranja = [] # Lista que salva os IDs dos cones Laranja
lista_cone_laranja_position = [[],[]] # Lista que salva a posição dos cones Laranja no mundo
lista_cone_azul = [] # Lista que salva os IDs dos cones Azuis
lista_cone_azul_position = [[],[]] # Lista que salva a posição dos cones Azuis no mundo
lista_cone_amarelo = [] # Lista que salva os IDs dos cones Amarelos
lista_cone_amarelo_position = [[],[]] # Lista que salva a posição dos cones amarelos no mundo
lista_car_position = [[],[]] # Lista das posições do carro

loc = robot.getDevice("gps") # Variavel que controla o GPS, usado somente para pegar a velocidade atual do carro
loc.enable(TIME_STEP)
IMU = robot.getDevice("IMU") # Varialvel que controla a IMU, que nos retorna em que orientação o carro está
IMU.enable(TIME_STEP)
camera = robot.getDevice("camera") # Variavel que controla a Camera do carro, possibilitando reconhecer os cones e calcular suas distancias
camera.enable(TIME_STEP)
camera.recognitionEnable(TIME_STEP)
steering = curva() # Variavel da classe curva(), a qual ira fazer todas as contas necessarias para movimentar o carro na pista
lista_curva = [] # Lista de curvas, serve para guardar todas as curvas reconhecidas, e executa-las uma a uma

# Função principal do carro, onde sera feito a aquisição e analise dos dados dos cones, assim como
# o tratamento e as funções do carro.
def robo():
    teste_curva = [[],[]] # Lista de variaveis para testar se é curva ou não
    count_amarelo = 0 # Conta a quantidade de cones amarelo que foram reconhecidos
    id_freio = -1 # variavel para guardar o ID do cone, no qual o carro precisa iniciar a frenagem
    id_curva = -1 # variavel usada pra guardar o ID do cone, no qual o carro deveria virar
    count_tempo = 0 # Variavel para contar o tempo do programa, possibilitando utiliza-lo para estimar a posição do carro
    while robot.step(TIME_STEP) != -1:
        # Analiza de 3 em 3 cones para verificar se é uma curva ou não.
        if count_amarelo % 3 == 0 and count_amarelo != 0:
            count_amarelo = 0
            # Variaveis para armazenar a posição dos 3 cones de teste para curva
            x0 = teste_curva[0][0]
            x1 = teste_curva[0][1]
            x2 = teste_curva[0][2]
            y0 = teste_curva[1][0]
            y1 = teste_curva[1][1]
            y2 = teste_curva[1][2]
            # a1 é o angulo da roda interna a curva
            # a2 é o angulo da roda externa a curva
            # r é o raio da curva
            # ehcurva é True quando for curva, e False quando for uma reta
            a1,a2,r,ehcurva= steering.executa([x0,x1,x2],[y0,y1,y2])
            teste_curva = [[],[]] # Reinicializa a lista teste_curva
            # Pega os angulos para as rodas e o raio da curva, para ser utilizado posteriormente.
            if ((a1 < 0 and a2 <0) or (a1 > 0 and a2 > 0)) and r>1.2 and ehcurva:
                pos_curva = [x1,y1] # Lista da posição na qual a curva é encontrada
                ang_curva = [a1,a2] # Lista dos angulos da roda dianteira do carro
                lista_curva.append([id_curva,ang_curva,pos_curva])
            else:
                lm.setVelocity(10*MAX_SPEED)
                rm.setVelocity(10*MAX_SPEED)
                rd_dir.setPosition(0.0)
                rd_esq.setPosition(0.0)
        # Faz a plotagem do carro no mundo, verificando sua velocidade e o tempo de deslocamento a partir do ultimo plot
        # achando assim a ditancia percorrida.
        if len(lista_car_position[0]) == 0:
            # pos1 é a coordenada X do carro no mundo
            # pos2 é a coordenada Y do carro no mundo
            pos1,pos2 = steering.plot(IMU.getRollPitchYaw()[2],0,loc.getSpeed())
            lista_car_position[0].append(pos1)
            lista_car_position[1].append(pos2)
        else:
            pos1,pos2 = steering.plot(IMU.getRollPitchYaw()[2],count_tempo/1000,loc.getSpeed())
            lista_car_position[0].append(pos1+lista_car_position[0][len(lista_car_position[0])-1])
            lista_car_position[1].append(pos2+lista_car_position[1][len(lista_car_position[1])-1])
        count_tempo = 0
        reconhecidos = camera.getRecognitionObjects() # Variavel que armaneza todos os cones reconhecidos no momento pela camera
        # Faz a iteração por todos os objetos reconhecidos pela camera, neste momento.
        for i in range(len(reconhecidos)):
            # Caso o cone reconhecido seja o escolhido para iniciar a frenagem.
            if reconhecidos[i].get_id() == id_freio:
                if reconhecidos[i].get_position()[2]*-1 < 4:
                    rm.setVelocity(0)
                    lm.setVelocity(0)
            # Se existir algo na lista de curvas, ira começar a fazer o tratamento da curva
            # determinando o momento para que o carro vire.
            if len(lista_curva)!=0:
                teste = lista_curva[0][2][1]-lista_car_position[1][-1] # Variavel para verificar se a distancia do carro para a curva é proxima
                if teste < 3.5:
                    adentro = lista_curva[0][1][0] # Valor no qual a roda interna a curva deve estar
                    afora = lista_curva[0][1][1] # Valor no qual a roda externa a curva deve estar
                    a_ackerman = (adentro+afora)/2 # Variavel do angulo de ackerman, Utilizado para saber para qual lado o carro deve virar
                    # v1 é a velocidade da roda traseira interna a curva
                    # v2 é a velocidade da roda transeira externa a curva
                    v1,v2 = steering.velocidade(a_ackerman)
                    if a_ackerman < 0:
                        lm.setVelocity(v1)
                        rm.setVelocity(v2)
                        rd_dir.setPosition(afora)
                        rd_esq.setPosition(adentro)
                    else:
                        lm.setVelocity(v2)
                        rm.setVelocity(v1)
                        rd_dir.setPosition(adentro)
                        rd_esq.setPosition(afora)
                    lista_curva.pop(0)
            # Verifica se o cone ja foi vizualiado anteriomente, caso verdadeiro, ira partir para o proximo
            # objeto da lista.
            if(reconhecidos[i].get_id() in lista_cone_laranja or reconhecidos[i].get_id() in lista_cone_azul or
                reconhecidos[i].get_id() in lista_cone_amarelo):
                continue
            else:
                # Caso o cone vizualizado no momento for laranja(1,0.6,1)
                if(reconhecidos[i].get_colors() == [1,0.6,0,1,1,1]):
                    # Se for o primeiro cone laranja vizualizado pela camera, ira atribuir uma velocidade inicial para o carro
                    if len(lista_cone_laranja) == 1:
                        lm.setVelocity(10*MAX_SPEED)
                        rm.setVelocity(10*MAX_SPEED)
                    if len(lista_cone_laranja) == 8 and reconhecidos[i].get_position()[2] < 3:
                        id_freio = lista_cone_laranja[7]
                        fim = True
                    # Caso não seja nem o primeiro nem o ultimo cone laranja vizualizado pela camera,
                    # ira salvar seu ID, assim como sua posição no mundo.      
                    else:
                        id = reconhecidos[i].get_id() # Pega o ID do cone
                        lista_cone_laranja.append(id)
                        laranjaX = reconhecidos[i].get_position()[0]*-1 # Pega a coordenada X do cone, em relação ao carro
                        laranjaY = reconhecidos[i].get_position()[2]*-1 # Pega a coordenada Y do cone, em relação ao carro
                        # cone_laranjaX é a variavel que armazena a posição X do cone em relação ao mundo
                        # cone_laranjaY é a variavel que armazena a posição Y do cone em relação ao mundo
                        cone_laranjaX,cone_laranjaY = steering.plot_cone(IMU.getRollPitchYaw()[2],laranjaX,laranjaY)
                        lista_cone_laranja_position[0].append(cone_laranjaX+lista_car_position[0][len(lista_car_position[0])-1])
                        lista_cone_laranja_position[1].append(cone_laranjaY*-1+lista_car_position[1][len(lista_car_position[1])-1])
                # Caso o cone vizualizado no momento for azul(0,0,1),
                # ira salvar seu ID, assim como sua posição no mundo. 
                if(reconhecidos[i].get_colors() == [0,0,1,1,1,1]):
                    id = reconhecidos[i].get_id()
                    lista_cone_azul.append(id)
                    azulX = reconhecidos[i].get_position()[0]*-1# Pega a coordenada X do cone, em relação ao carro
                    azulY = reconhecidos[i].get_position()[2]*-1# Pega a coordenada Y do cone, em relação ao carro
                    # cone_azulX é a variavel que armazena a posição X do cone em relação ao mundo
                    # cone_azulY é a variavel que armazena a posição Y do cone em relação ao mundo
                    cone_azulX,cone_azulY = steering.plot_cone(IMU.getRollPitchYaw()[2],azulX,azulY)
                    lista_cone_azul_position[0].append(cone_azulX+lista_car_position[0][len(lista_car_position[0])-1])
                    lista_cone_azul_position[1].append(cone_azulY*-1+lista_car_position[1][len(lista_car_position[1])-1])
                # Caso o cone vizualizado no momento for amarelo(1,1,0),
                # ira salvar seu ID, assim como sua posição no mundo. 
                if(reconhecidos[i].get_colors() == [1,1,0,1,1,1]):
                    id = reconhecidos[i].get_id()
                    lista_cone_amarelo.append(id)
                    amareloX = reconhecidos[i].get_position()[0]*-1# Pega a coordenada X do cone, em relação ao carro
                    amareloY = reconhecidos[i].get_position()[2]*-1# Pega a coordenada Y do cone, em relação ao carro
                    # cone_amareloX é a variavel que armazena a posição X do cone em relação ao mundo
                    # cone_amareloY é a variavel que armazena a posição Y do cone em relação ao mundo
                    cone_amareloX,cone_amareloY = steering.plot_cone(IMU.getRollPitchYaw()[2],amareloX,amareloY)
                    lista_cone_amarelo_position[0].append(cone_amareloX+lista_car_position[0][len(lista_car_position[0])-1])
                    lista_cone_amarelo_position[1].append(cone_amareloY*-1+lista_car_position[1][len(lista_car_position[0])-1])
                    teste_curva[0].append(lista_cone_amarelo_position[0][len(lista_cone_amarelo_position[0])-1])
                    teste_curva[1].append(lista_cone_amarelo_position[1][len(lista_cone_amarelo_position[1])-1])
                    count_amarelo += 1
        # Quando o carro vier a parar totalmente, ou seja, sua velocidade for "0",
        # ira sair do looping e fizanlizar o programa.
        if lm.getVelocity() == 0:
            break
        count_tempo += TIME_STEP
        continue
    if exitFlag:
        threadName.exit()

# Função para plotar o grafico simultaneamente ao funcionamento do carro.
def gera_grafico():
    grafico = DynamicUpdate()
    # Looping para plotar os cones
    while True:
        try:
            if len(lista_cone_amarelo_position[0]) == 0:
                final_amareloX = lista_cone_amarelo_position[0][0]
                final_amareloY = lista_cone_amarelo_position[1][0]
            else:
                final_amareloX = lista_cone_amarelo_position[0][len(lista_cone_amarelo_position[0])-1]
                final_amareloY = lista_cone_amarelo_position[1][len(lista_cone_amarelo_position[1])-1]
        except:
            final_amareloX = None
            final_amareloY = None
            pass
        try:
            if len(lista_cone_azul_position[0]) == 0:
                final_azulX = lista_cone_azul_position[0][0]
                final_azulY = lista_cone_azul_position[1][0]
            else:
                final_azulX = lista_cone_azul_position[0][len(lista_cone_azul_position[0])-1]
                final_azulY = lista_cone_azul_position[1][len(lista_cone_azul_position[1])-1]
        except:
            final_azulX = None
            final_azulY = None
            pass
        try:
            if len(lista_cone_laranja_position[0]) == 0:
                final_laranjaX = lista_cone_laranja_position[0][0]
                final_laranjaY = lista_cone_laranja_position[1][0]
            else:
                final_laranjaX = lista_cone_laranja_position[0][len(lista_cone_laranja_position[0])-1]
                final_laranjaY = lista_cone_laranja_position[1][len(lista_cone_laranja_position[1])-1]
        except:
            final_laranjaX = None
            final_laranjaY = None
            pass
        try:
            if len(lista_car_position[0]) == 0:
                final_carX = lista_car_position[0][lista_car_position[0][0]]
                final_carY = lista_car_position[1][lista_car_position[1][0]]
            else:
                final_carX = lista_car_position[0][len(lista_car_position[0])-1]
                final_carY = lista_car_position[1][len(lista_car_position[1])-1]
        except:
            final_carX = None
            final_carY = None
            pass
        grafico.atualiza(final_amareloX, final_amareloY, final_azulX, final_azulY, final_laranjaX, final_laranjaY, final_carX, final_carY)
        if lm.getVelocity() == 0:
            break
    if exitFlag:
        grafico.__del__()
        threadName.exit()

# Thread para rodar o programa principal do carro
thread1 = myThread('robo')
# Thread para rodar o programa que faz o Plot do carro e dos cones
#thread2 = myThread('grafico')
# Inicializando ambas as threads
thread1.start()
#thread2.start()
gera_grafico()
