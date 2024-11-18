from mesa.model import Model
from mesa.agent import Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

import numpy as np


class Celda(Agent):
    def __init__(self, unique_id, model, suciedad: bool = False):
        super().__init__(unique_id, model)
        self.sucia = suciedad


class Mueble(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class RobotLimpieza(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0

    def limpiar_una_celda(self, lista_de_celdas_sucias):
        lista_de_celdas_sucias = [
            celda for celda in lista_de_celdas_sucias
            if celda.pos not in self.model.visitados
        ]
        if lista_de_celdas_sucias:
            celda_a_limpiar = self.random.choice(lista_de_celdas_sucias)
            celda_a_limpiar.sucia = False
            self.sig_pos = celda_a_limpiar.pos
            self.model.visitados.add(self.sig_pos)

    def seleccionar_nueva_pos(self, lista_de_vecinos):
        vecinos_validos = [
            vecino for vecino in lista_de_vecinos
            if vecino.pos not in self.model.visitados
        ]

        if not vecinos_validos:
            vecinos_validos = lista_de_vecinos

        if vecinos_validos:
            self.sig_pos = self.random.choice(vecinos_validos).pos
            self.model.visitados.add(self.sig_pos)

    @staticmethod
    def buscar_celdas_sucia(lista_de_vecinos):
        celdas_sucias = [
            vecino for vecino in lista_de_vecinos
            if isinstance(vecino, Celda) and vecino.sucia
        ]
        return celdas_sucias

    def step(self):
        vecinos = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)

        vecinos = [
            vecino for vecino in vecinos
            if not isinstance(vecino, (Mueble, RobotLimpieza))
        ]

        celdas_sucias = self.buscar_celdas_sucia(vecinos)

        if len(celdas_sucias) == 0:
            self.seleccionar_nueva_pos(vecinos)
        else:
            self.limpiar_una_celda(celdas_sucias)

    def advance(self):
        if self.pos != self.sig_pos:
            self.movimientos += 1

        self.model.grid.move_agent(self, self.sig_pos)


class Habitacion(Model):
    def __init__(self, M: int, N: int,
                 num_agentes: int = 5,
                 porc_celdas_sucias: float = 0.6,
                 porc_muebles: float = 0.1,
                 modo_pos_inicial: str = 'Fija',
                 ):
        super().__init__()
        self.num_agentes = num_agentes
        self.porc_celdas_sucias = porc_celdas_sucias
        self.porc_muebles = porc_muebles
        self.visitados = set()

        self.grid = MultiGrid(M, N, False)
        self.schedule = SimultaneousActivation(self)

        posiciones_disponibles = [pos for _, pos in self.grid.coord_iter()]

        num_muebles = int(M * N * porc_muebles)
        posiciones_muebles = self.random.sample(posiciones_disponibles, k=num_muebles)

        for id, pos in enumerate(posiciones_muebles):
            mueble = Mueble(int(f"{num_agentes}0{id}") + 1, self)
            self.grid.place_agent(mueble, pos)
            posiciones_disponibles.remove(pos)

        self.num_celdas_sucias = int(M * N * porc_celdas_sucias)
        posiciones_celdas_sucias = self.random.sample(
            posiciones_disponibles, k=self.num_celdas_sucias)

        for id, pos in enumerate(posiciones_disponibles):
            suciedad = pos in posiciones_celdas_sucias
            celda = Celda(int(f"{num_agentes}{id}") + 1, self, suciedad)
            self.grid.place_agent(celda, pos)

        if modo_pos_inicial == 'Fija':
            pos_inicial_robots = [
                (0, 0),
                (0, N - 1),
                (M - 1, 0),
                (M - 1, N - 1)
            ]
        else:
            pos_inicial_robots = self.random.sample(posiciones_disponibles, k=num_agentes)

        for id, pos in enumerate(pos_inicial_robots):
            robot = RobotLimpieza(id, self)
            self.grid.place_agent(robot, pos)
            self.schedule.add(robot)

        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid,
                             "CeldasSucias": get_sucias},
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()


def get_grid(model: Model) -> np.ndarray:
    grid = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        x, y = pos
        for obj in cell_content:
            if isinstance(obj, RobotLimpieza):
                grid[x][y] = 2
            elif isinstance(obj, Celda):
                grid[x][y] = int(obj.sucia)
    return grid

def get_sucias(model: Model) -> int:
    sum_sucias = 0
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Celda) and obj.sucia:
                sum_sucias += 1
    return sum_sucias / model.num_celdas_sucias


def get_movimientos(agent: Agent) -> dict:
    if isinstance(agent, RobotLimpieza):
        return {agent.unique_id: agent.movimientos}
