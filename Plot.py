from matplotlib import pyplot as plt
plt.ion()
class DynamicUpdate():
    global list_amareloX, list_amareloY, list_azulX, list_azulY, list_laranjaX, list_laranjaY, list_carroX, list_carroY
    list_amareloX = [] # Lista das coordenadas X dos cones amarelos
    list_amareloY = [] # Lista das coordenadas Y dos cones amarelos
    list_azulX = [] # Lista das coordenadas X dos cones azuis
    list_azulY = [] # Lista das coordenadas Y dos cones azuis
    list_laranjaX = [] # Lista das coordenadas X dos cones laranja
    list_laranjaY = [] # Lista das coordenadas Y dos cones laranja
    list_carroX = [] # Lista das coordenadas X do carro
    list_carroY = [] # Lista das coordenadas Y do carro

    def __del__(self):
        plt.show(block = True)


    def __init__(self):
        self.figure, self.ax = plt.subplots()
        self.azul, = self.ax.plot([],[], 'o', color ='Blue') # Plot inicial dos cones azuis
        self.amarelo, = self.ax.plot([],[], 'o', color = 'Yellow') # Plot inicial dos cones amarelos
        self.laranja, = self.ax.plot([],[], 'o', color = 'Orange') # Plot inicial dos cones laranja
        self.carro, = self.ax.plot([],[], color = 'Black') # Plot inicial do carro
        plt.xlabel("Metros (m)")
        plt.ylabel("Metros (m)")
        self.ax.set_autoscaley_on(True)
        self.ax.grid()
        ...

    def on_running(self, amareloX, amareloY, azulX, azulY, laranjaX, laranjaY, carroX, carroY):
        self.azul.set_xdata(azulX) # Atualiza os dados das coordenadas X dos cones azuis
        self.azul.set_ydata(azulY) # Atualiza os dados das coordenadas Y dos cones azuis 
        self.amarelo.set_xdata(amareloX) # Atualiza os dados das coordenadas X dos cones amarelos
        self.amarelo.set_ydata(amareloY) # Atualiza os dados das coordenadas Y dos cones amarelos
        self.laranja.set_xdata(laranjaX) # Atualiza os dados das coordenadas X dos cones laranjas
        self.laranja.set_ydata(laranjaY) # Atualiza os dados das coordenadas Y dos cones laranjas
        self.carro.set_xdata(carroX) # Atualiza os dados das coordenadas X do carro
        self.carro.set_ydata(carroY) # Atualiza os dados das coordenadas Y do carro
        self.ax.relim()
        self.ax.autoscale_view()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def atualiza(self, final_amareloX, final_amareloY, final_azulX, final_azulY, final_laranjaX, final_laranjaY, final_carX, final_carY):
        import time
        if final_amareloX == None:
            pass
        elif len(list_amareloX) == 0:
            list_amareloX.append(final_amareloX)
            list_amareloY.append(final_amareloY)
        elif final_amareloX != list_amareloX[len(list_amareloX)-1]:
            list_amareloX.append(final_amareloX)
            list_amareloY.append(final_amareloY)
        if final_azulX == None:
            pass
        elif len(list_azulX) == 0:
            list_azulX.append(final_azulX)
            list_azulY.append(final_azulY)
        elif final_azulX != list_azulX[len(list_azulX)-1]:
            list_azulX.append(final_azulX)
            list_azulY.append(final_azulY)
        if final_laranjaX == None:
            pass
        elif len(list_laranjaX) == 0:
            list_laranjaX.append(final_laranjaX)
            list_laranjaY.append(final_laranjaY)
        elif final_laranjaX != list_laranjaX[len(list_laranjaX)-1]:
            list_laranjaX.append(final_laranjaX)
            list_laranjaY.append(final_laranjaY)
        if final_carX == None:
            pass
        elif len(list_carroX) == 0:
            list_carroX.append(final_carX)
            list_carroY.append(final_carY)
        elif final_carX != list_carroX[len(list_carroX)-1]:
            list_carroX.append(final_carX)
            list_carroY.append(final_carY)
        self.on_running(list_amareloX, list_amareloY, list_azulX, list_azulY, list_laranjaX, list_laranjaY, list_carroX, list_carroY)