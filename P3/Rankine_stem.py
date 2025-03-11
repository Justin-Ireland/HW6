#region imports
from Steam_stem import steam
import numpy as np
#endregion imports


class rankine():
    def __init__(self, p_low=8, p_high=8000, t_high=None, name='Rankine Cycle'):
        '''
                Constructor for rankine power cycle.  If t_high is not specified, the State 1
                is assigned x=1 (saturated steam @ p_high).  Otherwise, use t_high to find State 1.
                :param p_low: the low pressure isobar for the cycle in kPa
                :param p_high: the high pressure isobar for the cycle in kPa
                :param t_high: optional temperature for State1 (turbine inlet) in degrees C
                :param name: a convenient name
        '''
        self.p_low = p_low
        self.p_high = p_high
        self.t_high = t_high
        self.name = name
        #below are initialized at zero
        self.efficiency = None
        self.turbine_work = 0
        self.pump_work = 0
        self.heat_added = 0
        self.state1 = None
        self.state2 = None
        self.state3 = None
        self.state4 = None

    def calc_efficiency(self):
        """This function calculates each of the four states by calling
        the steam function with given parameters.
        Outputs values for inlet,outlet for both turbine and pump"""
        #state 1: turbine inlet (p_high, t_high) superheated or saturated vapor
        if self.t_high is None:
            self.state1 = steam(self.p_high, x=1, name='Turbine Inlet')
        #instantiate a steam object with conditions of state 1 as saturated steam, named 'Turbine Inlet'
        else:
            self.state1 = steam(self.p_high, T=self.t_high, name='Turbine Inlet')
        #instantiate a steam object with conditions of state 1 at t_high, named 'Turbine Inlet'
        #state 2: turbine exit (p_low, s=s_turbine inlet) two-phase
        self.state2 = steam(self.p_low, s=self.state1.s, name='Turbine Exit')
        #instantiate a steam object with conditions of state 2, named 'Turbine Exit'
        #state 3: pump inlet (p_low at x=0) saturated liquid
        self.state3 = steam(self.p_low, x=0, name='Pump Inlet')
        #instantiate a steam object with conditions of state 3 as saturated liquid, named 'Pump Inlet'
        #state 4: pump exit (p_high, s=s_pump_inlet) saturated liquid
        self.state4 = steam(self.p_high, s=self.state3.s, name='Pump Exit') #instantiate steam object of state for named 'pump exit'
        self.state4.h = self.state3.h + self.state3.v * (self.p_high - self.p_low) / 1000.0  #kJ/kg conversion

        #work & heat terms
        self.turbine_work = self.state1.h - self.state2.h #turbine work
        self.pump_work = self.state4.h - self.state3.h #pump work
        self.heat_added = self.state1.h - self.state4.h #find heat added

        self.efficiency = 100.0 * (self.turbine_work - self.pump_work) / self.heat_added #equation efficiency of work
        return self.efficiency #return calculation

    def print_summary(self):
        """print summary is used to firstly display the total results
        for the cycle for both the turbine and the pump. Then each property for
        each state is printed for viewing
        Cycle Summary:
        eff:
        turbine work:
        pump work:
        heat added:

        state 1-4 all properties:"""
        if self.efficiency is None:
            self.calc_efficiency() #double checks that efficiency is calculated before all outputs are printed
        print('Cycle Summary for: ', self.name) #header for cycle summary
        print('\tEfficiency: {:0.3f}%'.format(self.efficiency)) #print total efficiency
        print('\tTurbine Work: {:0.3f} kJ/kg'.format(self.turbine_work)) #print turbine work
        print('\tPump Work: {:0.3f} kJ/kg'.format(self.pump_work)) #print pump work
        print('\tHeat Added: {:0.3f} kJ/kg'.format(self.heat_added)) #print heat added for cycle
        #following 4 lines display all properties for each state
        self.state1.print() #turbine inlet
        self.state2.print() #turbine exit
        self.state3.print() #pump in.
        self.state4.print() #pump ex.


def main():
    try:
        superheat_temp = 1.7 * steam(8000, x=1).T  #make sure t_high is properly extracted
        rankine1 = rankine(p_high=8000, p_low=8, t_high=superheat_temp, name='Superheated Rankine Cycle')
        #instantiate ranking object (just 1) to test functionality of Rankine_stem
        eff = rankine1.calc_efficiency() #assign cycle 1 efficiency calculation to 'eff'
        print(eff) #print efficiency of rankine1
        rankine1.print_summary() #call print summary to print example of cycle 1
    except Exception as e:
        print(f"Error encountered: {e}") #print out possible errors on CLI


if __name__ == "__main__":
    main()


