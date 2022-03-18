from mesa.visualization.ModularVisualization import ModularServer
from mesa.batchrunner import batch_run

from boarding_model.agent import AgentStates
from boarding_model.model import BoardingModel
from boarding_model.model import top_to_bottom_boarding_class, outside_in_boarding_class, random_boarding_class

import pandas as pd
import matplotlib.pyplot as plt

def convert_to_dataframe(completed):
    data = {}

    for run in completed:
        key = run['RunId']

        if not key in data:
            data[key] = run["Step"]

    # df = pd.DataFrame(data.items(), columns=['RunId', 'Step'])
    s = pd.Series(data, name='Step')
    s.index.name = 'RunId'
    s.reset_index()

    return s

if __name__ == '__main__':
    params = {"width": 7, "height": 35, 'boarding_class': [tuple(outside_in_boarding_class)]}

    results = batch_run(
        BoardingModel,
        parameters=params,
        iterations=100,
        max_steps=5000,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

    s = convert_to_dataframe(list(filter(lambda x: x['is_complete'], results)))

    s.to_csv("aisle_first.csv")

    params = {"width": 7, "height": 35, 'boarding_class': [tuple(top_to_bottom_boarding_class)]}

    results = batch_run(
        BoardingModel,
        parameters=params,
        iterations=100,
        max_steps=6000,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )


    s = convert_to_dataframe(list(filter(lambda x: x['is_complete'], results)))

    s.to_csv("back_to_front.csv")

    # breakpoint()
    params = {"width": 7, "height": 35, 'boarding_class': [tuple(random_boarding_class)]}

    results = batch_run(
        BoardingModel,
        parameters=params,
        iterations=100,
        max_steps=6000,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

    s = convert_to_dataframe(list(filter(lambda x: x['is_complete'], results)))

    s.to_csv("random.csv")

    