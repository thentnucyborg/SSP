import json
from CREPE import QueueService
import math
from plotter import *
import numpy as np

# TODO: Input validation and error messages

# IR sensor preprocessor 
# Takes JSON sensor data from the hardware-api, preprocesses, sends to meame
# Due to the unfortunate lack of healthy cell cultures, this performs
# all stages of the analysis, and essentially attempts to send the conclusion
# through the nevral network. 
# In more "proper" circumstances, this would perform simple operations
# on the data, such as Fourier transforms.

class IRPreprocessor(QueueService):

    def __init__(self, name="IRPrePros", queue_plot=None, **kwargs):
        #global plotter
        #plotter = VisdomLinePlotter(env_name='CREPE')
        # Initialize queue service
        QueueService.__init__(
            self, 
            name=name, 
            **kwargs
        )

        if queue_plot is not None:
            self.queue_plot = queue_plot
        else:
            print("Error: queue_plot not recived")
            raise ValueError()
        
        # Set a threshold for whether or not a pixel is part of hand or not.
        self.on_threshold = 20

        # Set some thresholds for how many pixels a rock, scissors and paper
        # have.
        self.rock_threshold = 3  # TODO: Placeholder
        self.scissors_threshold = 7 #TODO: Placeholder
        self.paper_threshold = 14  # TODO: placeholder

        

    def run(self):
        while True:
            # Fetch new json item to process
            new_data_j = str(self.get())[2:-1]
            print(new_data_j)
            new_data = json.loads(new_data_j)
            new_data = np.array(new_data)
            #plot heatmap
            #plotter.plot_map(new_data, "IMG", "input image")
            self.queue_plot.put(new_data)
            # Try to get data from it
            conclusion = self.analyze_simple(new_data)
            print("CONCLUSION: " + conclusion)
            self.put(conclusion)
    
            
    def analyze_simple(self, ir_mat):
        '''
        Perform a simple analysis of the matrix, by counting the number of
        "on" pixels. It is assumed that different shapes will have different
        numbers of "on" pixels. For example: Rock < scissors < paper. 
        :param byte[] ir_mat: NxM IR data matrix
        Returns one of 4 conclusions: "None", "Rock", "Scissors" or "Paper"
        '''

        # only take the upper rigth quadrant
        x = math.floor(len(ir_mat)/2)
        y = math.floor(len(ir_mat[0])/2)
        ir_mat = ir_mat[...,y:]
        ir_mat = ir_mat[:x,...]

        mat_N = len(ir_mat)  # Number of rows
        mat_M = len(ir_mat[0])  # Number of columns
        on_count = 0
        for i in range(0, mat_N):
            for j in range(0, mat_M):
                if ir_mat[i][j] > self.on_threshold: 
                    on_count += 1
        print("PixelCount", on_count)
        if on_count < self.rock_threshold:
            print("ir_none")
            return "None"
        elif on_count < self.scissors_threshold:
            print("ir_rock")
            return "Rock"
        elif on_count < self.paper_threshold: 
            print("ir_scissor")
            return "Scissors"
        else:
            return "Paper"
        

