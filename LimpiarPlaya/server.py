import mesa

from model import Habitacion, RobotLimpieza, Celda, Mueble

MAX_NUMBER_ROBOTS = 20


def agent_portrayal(agent):
    if isinstance(agent, RobotLimpieza):
        return {"Shape": "circle", "Filled": "false", "Color": "Cyan", "Layer": 1, "r": 0.9}
    elif isinstance(agent, Mueble):
        return {"Shape": "rect", "Filled": "true", "Color": "black", "Layer": 0,
                "w": 0.9, "h": 0.9}
    elif isinstance(agent, Celda):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "Black"}
        if agent.sucia:
            portrayal["Color"] = "#fff"
            portrayal["text"] = "🗑️"
        else:
            portrayal["Color"] = "#f6d7b0"
            portrayal["text"] = ""
        return portrayal


grid = mesa.visualization.CanvasGrid(
    agent_portrayal, 20, 20, 400, 400)
chart_celdas = mesa.visualization.ChartModule(
    [{"Label": "CeldasSucias", "Color": 'red', "label": "Celdas Sucias"}],
    50, 200,
    data_collector_name="datacollector"
)

model_params = {
    "num_agentes": mesa.visualization.Slider(
        "Número de Robots",
        4,
        4,
        MAX_NUMBER_ROBOTS,
        4,
        description="Escoge cuántos robots deseas implementar en el modelo",
    ),
    "porc_celdas_sucias": mesa.visualization.Slider(
        "Porcentaje de Celdas Sucias",
        0.3,
        0.0,
        0.75,
        0.05,
        description="Selecciona el porcentaje de celdas sucias",
    ),
    "porc_muebles": mesa.visualization.Slider(
        "Porcentaje de Muebles",
        0.1,
        0.0,
        0.25,
        0.01,
        description="Selecciona el porcentaje de muebles",
    ),
    "modo_pos_inicial": mesa.visualization.Choice(
        "Posición Inicial de los Robots",
        "Fija",
        ["Fija"]
    ),
    "M": 20,
    "N": 20,
}

server = mesa.visualization.ModularServer(
    Habitacion, [grid, chart_celdas],
    "botCleaner", model_params, 8522
)

server.launch()