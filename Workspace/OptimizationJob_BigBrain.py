import pyNN.nest as brain_sim
import csv
import numpy as np
import optparse


class brain_big(object):
    
    def __init__(self, weight_red_to_actor, weight_red_to_go_on, weight_green_blue_to_actor, weight_go_on_to_right_actor, weight_eval_red, weight_eval_to_red_sensor, weight_eval_to_bg_sensor, weight_red_to_blue_eval):  
        sim = brain_sim

        INPUT_PARAMS = {'a': 4.0,
                        'b': 0.0000805,
                        'delta_T': 2.0,
                        'tau_w': 144.0,
                        'v_spike': 0.0,
                        'cm': .281, # ev. /1000
                        'v_rest': -70.6,
                        'tau_m': 9.3666667,
                        'e_rev_E': 0.0,
                        'e_rev_I': -80.0,
                        'v_reset': -70.6,
                        'v_thresh': -50.4,
                        'tau_refrac': 10.0,
                        'tau_syn_E': 5.,
                        'tau_syn_I': 5.}

        SENSORPARAMS = {'b': 0.0,
                        'tau_w': 10.0,
                        'v_spike': 0.0,
                        'cm': 0.025,
                        'v_rest': -60.5,
                        'tau_m': 10.,
                        'e_rev_E': 0.0,
                        'e_rev_I': -75.0,
                        'v_reset': -60.5,
                        'v_thresh': -60.0,
                        'tau_refrac': 10.0,
                        'tau_syn_E': 2.5,
                        'tau_syn_I': 7.5}

        GO_ON_PARAMS = {'cm': .025,
                        'v_rest': -60.5,
                        'tau_m': 10.,
                        'e_rev_E': 0.0,
                        'e_rev_I': -75.0,
                        'v_reset': -61.6,
                        'v_thresh': -60.51,
                        'tau_refrac': 10.0,
                        'tau_syn_E': 2.5,
                        'tau_syn_I': 7.5}

        INTERMEDIATE_PARAMS = {'a': 4.0,
                               'b': 0.0000805,
                               'delta_T': 2.0,
                               'tau_w': 144.0,
                               'v_spike': 0.0,
                               'cm': .281, # ev. /1000
                               'v_rest': -70.6,
                               'tau_m': 112.4,
                               'e_rev_E': 0.0,
                               'e_rev_I': -80.0,
                               'v_reset': -70.6,
                               'v_thresh': -50.4,
                               'tau_refrac': 10.0,
                               'tau_syn_E': 5.,
                               'tau_syn_I': 5.}


        self.population = sim.Population(709, sim.EIF_cond_alpha_isfa_ista())
        self.population[:600].set(**INPUT_PARAMS)
        self.population[600:605].set(**SENSORPARAMS)
        self.population[605:606].set(**GO_ON_PARAMS)
        self.population[606:608].set(**SENSORPARAMS)
        self.population[608:708].set(**INTERMEDIATE_PARAMS)
        self.population[708:709].set(**GO_ON_PARAMS)

        SYNAPSE_PARAMS = {"delay": 0.1 }

        synapse_red_to_actor = sim.StaticSynapse(weight=weight_red_to_actor, **SYNAPSE_PARAMS)
        synapse_red_to_go_on = sim.StaticSynapse(weight=weight_red_to_go_on, **SYNAPSE_PARAMS)
        synapse_green_blue_to_actor = sim.StaticSynapse(weight=weight_green_blue_to_actor, **SYNAPSE_PARAMS)
        synapse_go_on_to_right_actor = sim.StaticSynapse(weight=weight_go_on_to_right_actor, **SYNAPSE_PARAMS)
        synapse_eval_red = sim.StaticSynapse(weight=weight_eval_red, **SYNAPSE_PARAMS)
        synapse_eval_to_red_sensor = sim.StaticSynapse(weight=weight_eval_to_red_sensor, **SYNAPSE_PARAMS)
        synapse_eval_to_bg_sensor = sim.StaticSynapse(weight=weight_eval_to_bg_sensor, **SYNAPSE_PARAMS)
        synapse_red_to_blue_eval = sim.StaticSynapse(weight=weight_red_to_blue_eval, **SYNAPSE_PARAMS)

        # Connect neurons
        circuit = self.population
        
        sim.Projection(circuit[602:603], circuit[607:608],
                       connector=sim.AllToAllConnector(),
                       synapse_type=synapse_red_to_actor,
                       receptor_type='excitatory')
        sim.Projection(circuit[603:604], circuit[606:607],
                       connector=sim.AllToAllConnector(),
                       synapse_type=synapse_red_to_actor,
                       receptor_type='excitatory')


        sim.Projection(circuit[600:602], circuit[605:606],
                       connector=sim.AllToAllConnector(),
                       synapse_type=synapse_red_to_go_on,
                       receptor_type='inhibitory')


        sim.Projection(circuit[604:605], circuit[607:608],
                       connector=sim.AllToAllConnector(),
                       synapse_type=synapse_green_blue_to_actor,
                       receptor_type='excitatory')


        sim.Projection(circuit[605:606], circuit[607:608],
                       connector=sim.AllToAllConnector(),
                       synapse_type=synapse_go_on_to_right_actor,
                       receptor_type='excitatory')


        # connect the left portion of the detector neurons to the left evaluator and the right portion to the right one
        sim.Projection(circuit[0:300], circuit[608:658],
                       connector=sim.FixedNumberPreConnector(6),
                       synapse_type=synapse_eval_red,
                       receptor_type='excitatory')

        sim.Projection(circuit[300:600], circuit[658:708],
                       connector=sim.FixedNumberPreConnector(6),
                       synapse_type=synapse_eval_red,
                       receptor_type='excitatory')


        sim.Projection(circuit[608:658], circuit[600:601],
                       connector=sim.AllToAllConnector(),
                       synapse_type=synapse_eval_to_red_sensor,
                       receptor_type='excitatory')
        sim.Projection(circuit[608:658], circuit[602:603],
                       connector=sim.AllToAllConnector(),
                       synapse_type=synapse_eval_to_red_sensor,
                       receptor_type='excitatory')
        sim.Projection(circuit[658:708], circuit[601:602],
                       connector=sim.AllToAllConnector(),
                       synapse_type=synapse_eval_to_red_sensor,
                       receptor_type='excitatory')
        sim.Projection(circuit[658:708], circuit[603:604],
                       connector=sim.AllToAllConnector(),
                       synapse_type=synapse_eval_to_red_sensor,
                       receptor_type='excitatory')


        sim.Projection(circuit[600:602], circuit[604:605],
                       connector=sim.AllToAllConnector(),
                       synapse_type=synapse_red_to_blue_eval,
                       receptor_type='inhibitory')

        sim.Projection(circuit[708:709], circuit[604:605],
                       connector=sim.OneToOneConnector(),
                       synapse_type=synapse_eval_to_bg_sensor,
                       receptor_type='excitatory')  # connect the "blue green evaluator" to the blue green sensor
        
        sim.initialize(circuit, v=circuit.get('v_reset'))
        
        self.sensor_red_left   = circuit[0:300]
        self.sensor_red_right  = circuit[300:600]
        self.sensor_green_blue = circuit[708]
        self.actor_left        = circuit[606]
        self.actor_right       = circuit[607]
        
    
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
    
    def __init__(self, sensor_red_left, sensor_red_right, sensor_green_blue):
        params_source=  {'start': 0.0, 'duration': float("inf"), 'rate': 0.0}
        params_connec= {'weight':0.00015, 'receptor_type':'excitatory','delay':0.1}
        
        self.ssp_red_left_eye = brain_sim.create(brain_sim.SpikeSourcePoisson,  params_source)
        self.ssp_red_right_eye = brain_sim.create(brain_sim.SpikeSourcePoisson,  params_source)
        self.ssp_green_blue_eye = brain_sim.create(brain_sim.SpikeSourcePoisson,  params_source)
        
        brain_sim.connect(self.ssp_red_left_eye, sensor_red_left, **params_connec)
        brain_sim.connect(self.ssp_red_right_eye, sensor_red_right, **params_connec)
        brain_sim.connect(self.ssp_green_blue_eye, sensor_green_blue, **params_connec)
        
    def set_rates_from_ratios(self, red_left_rate, red_right_rate, non_red_rate):
        try:
            self.ssp_red_left_eye.set(rate=red_left_rate)
            self.ssp_red_right_eye.set(rate=red_right_rate)
            self.ssp_green_blue_eye.set(rate=non_red_rate)
        except StopIteration:
            pass
       
      
class OutputGenerator(object):
    def __init__(self, actor_left, actor_right):
        LI_create = {'v_thresh': float('inf'),'cm': 1.0,'tau_m': 10.0,'tau_syn_E': 2.,
            'tau_syn_I': 2.,'v_rest': 0.0,'v_reset': 0.0,'tau_refrac': 0.1,}
        LI_connect = {'weight':0.00015, 'receptor_type':'excitatory','delay':0.1}
        
        self.left = brain_sim.create(brain_sim.IF_curr_alpha, LI_create)
        self.right = brain_sim.create(brain_sim.IF_curr_alpha, LI_create)
        
        brain_sim.connect(actor_left, self.left, **LI_connect)
        brain_sim.connect(actor_right, self.right,  **LI_connect)
        
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
weight_red_to_actor = float(args[0])
weight_red_to_go_on = float(args[1])
weight_green_blue_to_actor = float(args[2])
weight_go_on_to_right_actor = float(args[3])
weight_eval_red = float(args[4])
weight_eval_to_red_sensor = float(args[5])
weight_eval_to_bg_sensor = float(args[6])
weight_red_to_blue_eval = float(args[7])

brain_sim.setup(timestep=0.1,min_delay=0.1,max_delay=4.0)
b = brain_big(weight_red_to_actor, weight_red_to_go_on, weight_green_blue_to_actor, weight_go_on_to_right_actor, weight_eval_red, weight_eval_to_red_sensor, weight_eval_to_bg_sensor, weight_red_to_blue_eval)
spike_generator = SpikeGenerator(b.sensor_red_left, b.sensor_red_right, b.sensor_green_blue)
output_generator = OutputGenerator(b.actor_left, b.actor_right)

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

print([weight_red_to_actor, weight_red_to_go_on, weight_green_blue_to_actor, weight_go_on_to_right_actor, weight_eval_red, weight_eval_to_red_sensor, weight_eval_to_bg_sensor, weight_red_to_blue_eval])
print("fitness = " + str(error) )