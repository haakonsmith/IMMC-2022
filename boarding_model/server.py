from mesa.visualization.ModularVisualization import ModularServer

from boarding_model.agent import AgentStates
from .model import BoardingModel

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "text": agent.target_str(),
                 "text_color": "black",
                 "r": 0.5}
    if agent.state == AgentStates.waiting:
        portrayal["Color"] = 'green'
    if agent.state == AgentStates.sitting:
        portrayal["Color"] = 'orange'
    if agent.stowing:
        portrayal["Color"] = 'blue'

    return portrayal


grid = CanvasGrid(agent_portrayal, 7, 35, 500, 500)
# chart = ChartModule(
#     [{"Label": "Gini", "Color": "#0000FF"}], data_collector_name="datacollector"
# )

model_params = {
    "N": UserSettableParameter(
        "slider",
        "Number of agents",
        100,
        1,
        200,
        1,
        description="Choose how many agents to include in the model",
    ),
    "width": 7,
    "height": 35,
}

server = ModularServer(BoardingModel, [grid], "Money Model", model_params)
server.port = 8521