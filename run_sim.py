from mesa.visualization.ModularVisualization import ModularServer
from mesa.batchrunner import batch_run

from boarding_model.agent import AgentStates
from boarding_model.model import BoardingModel

import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    params = {"width": 7, "height": 31}

    results = batch_run(
        BoardingModel,
        parameters=params,
        iterations=1000,
        max_steps=700,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

    completed = list(filter(lambda x: x['is_complete'], results))

    data = {}

    for run in completed:
        key = run['RunId']

        if not key in data:
            data[key] = run["Step"]

    # df = pd.DataFrame(data.items(), columns=['RunId', 'Step'])
    s = pd.Series(data, name='Step')
    s.index.name = 'RunId'
    s.reset_index()

    s.plot()
    print(s.describe())
    print(s)

    plt.show()

    s.plot.hist(alpha=0.5)

    plt.show()