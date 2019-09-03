import pyNN.nest as brain_sim
import csv
import numpy as np
import optparse


class brain(object):
    
    def __init__(self, WEIGHT_RED_TO_ACTOR, WEIGHT_RED_TO_GO_ON, WEIGHT_GREEN_BLUE_TO_ACTOR, WEIGHT_GO_ON_TO_RIGHT_ACTOR): 
        sim = brain_sim
        SENSORPARAMS = {'v_rest': -60.5,
                        'cm': 0.025,
                        'tau_m': 10.,
                        'tau_refrac': 10.0,
                        'tau_syn_E': 2.5,
                        'tau_syn_I': 2.5,
                        'e_rev_E': 0.0,
                        'e_rev_I': -75.0,
                        'v_thresh': -60.0,
                        'v_reset': -60.5}

        GO_ON_PARAMS = {'v_rest': -60.5,
                        'cm': 0.025,
                        'tau_m': 10.0,
                        'e_rev_E': 0.0,
                        'e_rev_I': -75.0,
                        'v_reset': -61.6,
                        'v_thresh': -60.51,
                        'tau_refrac': 10.0,
                        'tau_syn_E': 2.5,
                        'tau_syn_I': 2.5}

        self.population = sim.Population(8, sim.IF_cond_alpha())
        self.population[0:5].set(**SENSORPARAMS)
        self.population[5:6].set(**GO_ON_PARAMS)
        self.population[6:8].set(**SENSORPARAMS)

        syn_params = {'U': 1.0, 'tau_rec': 1.0, 'tau_facil': 1.0}
        DELAY = 1

        # Connect neurons
        CIRCUIT = self.population

        SYN = sim.TsodyksMarkramSynapse(weight=abs(WEIGHT_RED_TO_ACTOR),
                                        delay=DELAY, **syn_params)
        self._p1 = sim.Projection(presynaptic_population=CIRCUIT[2:3], 
                       postsynaptic_population=CIRCUIT[7:8],
                       connector=sim.AllToAllConnector(),
                       synapse_type=SYN,
                       receptor_type='excitatory')
        self._p2 = sim.Projection(presynaptic_population=CIRCUIT[3:4],
                       postsynaptic_population=CIRCUIT[6:7],
                       connector=sim.AllToAllConnector(),
                       synapse_type=SYN,
                       receptor_type='excitatory')


        SYN = sim.TsodyksMarkramSynapse(weight=abs(WEIGHT_RED_TO_GO_ON),
                                        delay=DELAY, **syn_params)
        self._p3 = sim.Projection(presynaptic_population=CIRCUIT[0:2],
                       postsynaptic_population=CIRCUIT[4:5],
                       connector=sim.AllToAllConnector(),
                       synapse_type=SYN,
                       receptor_type='inhibitory')
        self._p4 = sim.Projection(presynaptic_population=CIRCUIT[0:2],
                       postsynaptic_population=CIRCUIT[5:6],
                       connector=sim.AllToAllConnector(),
                       synapse_type=SYN,
                       receptor_type='inhibitory')

        SYN = sim.TsodyksMarkramSynapse(weight=abs(WEIGHT_GREEN_BLUE_TO_ACTOR),
                                        delay=DELAY, **syn_params)
        self._p5 = sim.Projection(presynaptic_population=CIRCUIT[4:5],
                       postsynaptic_population=CIRCUIT[7:8],
                       connector=sim.AllToAllConnector(),
                       synapse_type=SYN,
                       receptor_type='excitatory')

        SYN = sim.TsodyksMarkramSynapse(weight=abs(WEIGHT_GO_ON_TO_RIGHT_ACTOR),
                                        delay=DELAY, **syn_params)
        self._p6 = sim.Projection(presynaptic_population=CIRCUIT[5:6],
                       postsynaptic_population=CIRCUIT[7:8],
                       connector=sim.AllToAllConnector(),
                       synapse_type=SYN,
                       receptor_type='excitatory')

    def get_pop(self):  
        return self.population   
    
    def get_weights(self):
        w1 = self._p1.get('weight', format='array')
        w2 = self._p2.get('weight', format='array')
        w3 = self._p3.get('weight', format='array')
        w4 = self._p4.get('weight', format='array')
        w5 = self._p5.get('weight', format='array')
        w6 = self._p6.get('weight', format='array')
        
        return w1, w2, w3, w4, w5, w6
    
    
    
class SpikeGenerator(object):
    """the class handles the input for the brain"""
    
    def __init__(self, population, interval=20.0, count_red_left=1/3, count_red_right=1/3, count_non_red=1/3):
        params_source=  {'start': 0.0, 'duration': float("inf"), 'rate': 0.0}
        params_connec= {'weight':0.00015, 'receptor_type':'excitatory','delay':0.1}
        self.ssp_red_left_eye = brain_sim.create(brain_sim.SpikeSourcePoisson,  params_source)
        self.ssp_red_right_eye = brain_sim.create(brain_sim.SpikeSourcePoisson,  params_source)
        self.ssp_green_blue_eye = brain_sim.create(brain_sim.SpikeSourcePoisson,  params_source)
        brain_sim.connect(self.ssp_red_left_eye, population[slice(0, 3, 2)], **params_connec)
        brain_sim.connect(self.ssp_red_right_eye, population[slice(1, 4, 2)], **params_connec)
        brain_sim.connect(self.ssp_green_blue_eye, population[4], **params_connec)
        
    def set_rates_from_ratios(self, red_left_rate, red_right_rate, non_red_rate):
        try:
            self.ssp_red_left_eye.set(rate=red_left_rate)
            self.ssp_red_right_eye.set(rate=red_right_rate)
            self.ssp_green_blue_eye.set(rate=non_red_rate)
        except StopIteration:
            pass
        
        
        
class OutputGenerator(object):
    def __init__(self, population):
        LI_create = {'v_thresh': float('inf'),'cm': 1.0,'tau_m': 10.0,'tau_syn_E': 2.,
            'tau_syn_I': 2.,'v_rest': 0.0,'v_reset': 0.0,'tau_refrac': 0.1,}
        LI_connect = {'weight':0.00015, 'receptor_type':'excitatory','delay':0.1}
        self.left = brain_sim.create(brain_sim.IF_curr_alpha, LI_create)
        self.right = brain_sim.create(brain_sim.IF_curr_alpha, LI_create)
        brain_sim.connect(population[6], self.left, **LI_connect)
        brain_sim.connect(population[7], self.right,  **LI_connect)
        brain_sim.initialize(self.left, v=self.left.get('v_rest'))
        brain_sim.initialize(self.right, v=self.right.get('v_rest'))
        self.left.record('v')
        self.right.record('v')
    
    def get_current_voltage(self):
        return self._get_current_voltage(self.left), self._get_current_voltage(self.right)
    
    def _get_current_voltage(self, cell):
        return cell.get_data('v', clear=True).segments[0].filter(name="v")[0][-1,0].item()
    
    
def step(*ratio):
    
    timestep_ms = 7
    
    # Set the rates from the image
    spike_generator.set_rates_from_ratios(*ratio)
    
    # Run one step in the brain simulation
    brain_sim.run(timestep_ms)
        
    # Get the current voltage of the output neurons
    voltage_left, voltage_right = output_generator.get_current_voltage() #10ms    
    
    return voltage_left, voltage_right


# Read weights from args
parser = optparse.OptionParser()
options, args = parser.parse_args()
WEIGHT_RED_TO_ACTOR = float(args[0])
WEIGHT_RED_TO_GO_ON = float(args[1])
WEIGHT_GREEN_BLUE_TO_ACTOR = float(args[2])
WEIGHT_GO_ON_TO_RIGHT_ACTOR = float(args[3])

brain_sim.setup(timestep=0.1,min_delay=0.1,max_delay=4.0)
b = brain(WEIGHT_RED_TO_ACTOR, WEIGHT_RED_TO_GO_ON, WEIGHT_GREEN_BLUE_TO_ACTOR, WEIGHT_GO_ON_TO_RIGHT_ACTOR)
population=b.get_pop()
brain_sim.initialize(population, v=population.get('v_rest'))
spike_generator = SpikeGenerator(population)
output_generator = OutputGenerator(population)

output = []
voltage_left_error = 0
voltage_right_error = 0


with open('output1.csv', 'r') as f:
    reader = csv.reader(f)
    logging_information_list = list(reader)

    
    
# Convert to numpy array 
logging_information = np.asarray(logging_information_list, dtype=np.double)

for row in logging_information:

    # Get logging information from csv file
    age, voltage_left1, voltage_right1, red_left_rate, red_right_rate, non_red_rate = row

    # Simulate
    voltage_left2, voltage_right2 = step(red_left_rate, red_right_rate, non_red_rate)

    # Calculate errors
    voltage_left_diff = abs(voltage_left2 - voltage_left1)
    voltage_left_error += voltage_left_diff
    voltage_right_diff = abs(voltage_right2 - voltage_right1)
    voltage_right_error += voltage_right_diff

    # Write into output array
    output.append([voltage_left2, voltage_right2])

error = voltage_left_error + voltage_right_error

print([WEIGHT_RED_TO_ACTOR, WEIGHT_RED_TO_GO_ON, WEIGHT_GREEN_BLUE_TO_ACTOR, WEIGHT_GO_ON_TO_RIGHT_ACTOR])
print("fitness = " + str(error) )