import numpy as np
from scipy.optimize import fsolve

class curva():
    global nlsistema, eq_2grau, reta_ou_curva, erro

    # Função para calcular erro percentual
    def erro(x1,x2):
        if x1>x2:
            return np.absolute(((x1-x2)*100)/x2)
        else:
            return np.absolute(((x2-x1)*100)/x1)

    def nlsistema(variaveis): # sistema que queremos resolver
        (x,y,r) = variaveis     # variáveis do sistema
        eq1 = (x-valores[0]*2)*x+(y-valores[3]*2)*y+(valores[0]**2)+(valores[3]**2)-(r**2) # equação 1
        eq2 = (x-valores[1]*2)*x+(y-valores[4]*2)*y+(valores[1]**2)+(valores[4]**2)-(r**2) # equação 2
        eq3 = (x-valores[2]*2)*x+(y-valores[5]*2)*y+(valores[2]**2)+(valores[5]**2)-(r**2) # equação 3
        return [eq1,eq2,eq3]
    
    def executa(self,x, y):
        global valores
        global s
        valores = [x[0],x[1],x[2],y[0],y[1],y[2]] # Salva o valor das variaveis X e Y dos cones analisados
        s0 = np.array([1,1,1]) 
        s = fsolve(nlsistema,s0)
        s[2] = np.absolute(s[2]) # Raio da curva
        a1 = np.arctan(1.55/(s[2]+2.1)) # Angulo da roda interno a curva
        a2 = np.arctan(1.55/(s[2]+0.9)) # Angulo da roda externo a curva
        return a1, a2, s[2], reta_ou_curva()
    
    def velocidade(self, a_ackerman):
        Vmax = np.sqrt(0.3*9.8*(s[2]+1.5)) # Velocidade maxima para fazer a curva
        Win = (Vmax/0.203)*(1-(0.6*(np.tan(a_ackerman)/1.55))) # Velocidade da roda interna a curva
        Wout = (Vmax/0.203)*(1+(0.6*(np.tan(a_ackerman)/1.55))) # Velocidade da roda externa a vurva
        return Win, Wout

    def eq_2grau(variaveis): # sistema que queremos resolver
        (a,b,c) = variaveis     # variáveis do sistema
        if (erro(valores[0],valores[1])<0.1 or erro(valores[1],valores[2])<0.1 or erro(valores[2],valores[0])<0.1) or (erro(valores[3],valores[4])<0.1 or erro(valores[4],valores[5])<0.1 or erro(valores[5],valores[3])<0.5):
            return "fail" # Fail caso o erro percentual entre as coordenadas dos cones seja muito pequeno, podendo ser uma reta
                          # com uma pequena inclinação ou com erro na hora de pegar a posição do cone
        eq1 = ((valores[0]**2)*a+valores[0]*b+c-valores[3]) # equação 1
        eq2 = ((valores[1]**2)*a+valores[1]*b+c-valores[4]) # equação 2
        eq3 = ((valores[2]**2)*a+valores[2]*b+c-valores[5]) # equação 3
        return [eq1,eq2,eq3]

    def reta_ou_curva():
        s0 = np.array([1,1,1])
        try:
            s = fsolve(eq_2grau,s0)
            s[0] = round(s[0],3)
            s[1] = round(s[1],3)
            s[2] = round(s[2],3)
            return True
        except TypeError:
            return False

    def plot(self, ang_rad, temp, velocidade):
        pos = temp*velocidade # Valor da distancia o qual o carro percorreu em relação ao ultimo plot
        y = np.sin(ang_rad)*pos # Posição Y do carro incluindo sua inclinação
        x = np.cos(ang_rad)*pos # Posição X do carro incluindo sua inclinação
        return y,x

    def plot_cone(self, ang_rad, x, z):
        hip = np.sqrt(x**2+z**2) # Calcula a hipotenusa do cone em relaçao ao carro
        ang = np.arccos(x/hip) # Calcula o valor do angulo entre o carro e o cone
        ang_total = ang_rad-ang # Soma o valor do angulo do carro com o valor do cone em relaçao ao carro
        y_cone = np.sin(ang_total)*hip # Posição Y do cone em relação ao mundo
        x_cone = np.cos(ang_total)*hip # Posição X do cone em relação ao mundo
        return x_cone,y_cone

