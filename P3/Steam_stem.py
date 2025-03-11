# region imports
import numpy as np
from scipy.interpolate import griddata
# endregion

#region class
class steam():
    """
    The steam class is used to find thermodynamic properties of steam along an isobar.
    The Gibbs phase rule tells us we need two independent properties in order to find
    all the other thermodynamic properties. Hence, the constructor requires pressure of
    the isobar and one other property.
    """

    def __init__(self, pressure, T=None, x=None, v=None, h=None, s=None, name=None):
        '''
        Constructor for steam
        :param pressure: pressure in kPa
        :param T: Temperature in degrees C
        :param x: quality of steam x=1 is saturated vapor, x=0 is saturated liquid
        :param v: specific volume in m^3/kg
        :param h: specific enthalpy in kJ/kg
        :param s: specific entropy in kJ/(kg*K)
        :param name: a convenient identifier
        '''
        #arguments for our class properties
        self.p = pressure  #pressure - kPa
        self.T = T  #temperature - degrees C
        self.x = x  #quality
        self.v = v  #specific volume - m^3/kg
        self.h = h  #specific enthalpy - kJ/kg
        self.s = s  #entropy - kJ/(kg*K)
        self.name = name  #identiier
        self.region = None  #will be designated as either 'superheated' or 'saturated' or 'two-phase'

        if T is None and x is None and v is None and h is None and s is None:
            return #run after initializing
        else:
            self.calc() #calculate data after values are filled

    def calc(self):
        '''
        The Rankine cycle operates between two isobars (i.e., p_high (Turbine inlet state 1) & p_low (Turbine exit state 2).
        So, given a pressure, we need to determine if the other given property puts
        us in the saturated or superheated region.
        :return: nothing returned, just set the properties
        '''

        #load saturated water table
        """I used np.genfromtxt with delimiter and filling to fill a column recognized as empty by pycharm with NaN values
         as a recommended solution from ChatGPT due to formatting issues from the text files. 
        It happened to expect 9 columns, but receive 8 for sat_water, this also resolves the issue by skipping the 
         column headers (T, p, hf, hg, vf, vg, etc.)."""
        sat_data = np.genfromtxt(
            "C:/Users/justi/PycharmProjects/HW6/P3/sat_water_table.txt",
            delimiter=None,  #reads spaces and tabs
            skip_header=1, #skips header to avoid reading non-numeric values
            dtype=float, #reads float-numeric type data
            invalid_raise=False,  #allows rows with missing values to fill w/ Nan
            filling_values=np.nan  # replaces the missing values with NaN
        )

        #load superheated water table
        sh_data = np.genfromtxt(
            "C:/Users/justi/PycharmProjects/HW6/P3/superheated_water_table.txt",
            #although in same HW6 folder, I still called the path directly
            delimiter=None, #read spaces and tabs
            skip_header=1, #header skip
            dtype=float, #recognize float data types
            invalid_raise=False, #allow empty columns
            filling_values=np.nan #replace empty w/ NaN
        )

        #assign columns for saturated data so sat_data.T
        ts, ps, hfs, hgs, sfs, sgs, vfs, vgs = sat_data.T

        #assign columns for superheated data
        tcol, hcol, scol, pcol = sh_data.T

        R = 8.314 / (18 / 1000)  #ideal gas constant for water [J/(mol K)]/[kg/mol]
        Pbar = self.p / 100  #convert pressure (kpa) to bar

        #use griddata to interpolate for saturated properties to find exact value for each column (argument) in sat_water
        Tsat = float(griddata(ps, ts, Pbar, method='linear'))
        hf = float(griddata(ps, hfs, Pbar, method='linear'))
        hg = float(griddata(ps, hgs, Pbar, method='linear'))
        sf = float(griddata(ps, sfs, Pbar, method='linear'))
        sg = float(griddata(ps, sgs, Pbar, method='linear'))
        vf = float(griddata(ps, vfs, Pbar, method='linear'))
        vg = float(griddata(ps, vgs, Pbar, method='linear'))

        self.hf = hf  #creating member variable for the class that can be accessed from an object for enthalpy

        #find which of the second properties are given
        if self.T is not None:
            if self.T > Tsat:  #interpolate with griddata
                self.region = 'Superheated'
                self.h = float(griddata((tcol, pcol), hcol, (self.T, self.p), method='linear'))
                self.s = float(griddata((tcol, pcol), scol, (self.T, self.p), method='linear'))
                self.x = 1.0 #assign at x1=1
                TK = self.T + 273.14  #temperature conversion to kelvin
                self.v = R * TK / (self.p * 1000)  #finds ideal gas approximation for the volume
        elif self.x is not None:  #manually interpolates through saturated region
            self.region = 'Saturated'
            self.T = Tsat
            self.h = hf + self.x * (hg - hf)
            self.s = sf + self.x * (sg - sf)
            self.v = vf + self.x * (vg - vf)
        elif self.h is not None:
            self.x = (self.h - hf) / (hg - hf)
            if self.x <= 1.0:  #manual interpolation for saturated region vals
                self.region = 'Saturated'
                self.T = Tsat
                self.s = sf + self.x * (sg - sf)
                self.v = vf + self.x * (vg - vf)
            else:  #interpolate by using griddata in SHV
                self.region = 'Superheated'
                self.T = float(griddata((hcol, pcol), tcol, (self.h, self.p), method='linear'))
                self.s = float(griddata((hcol, pcol), scol, (self.h, self.p), method='linear'))
        elif self.s is not None:
            self.x = (self.s - sf) / (sg - sf)
            if self.x <= 1.0:  #manual interpolation
                self.region = 'Saturated'
                self.T = Tsat
                self.h = hf + self.x * (hg - hf)
                self.v = vf + self.x * (vg - vf)
            else:  #interpolate with griddata for SHV
                self.region = 'Superheated'
                self.T = float(griddata((scol, pcol), tcol, (self.s, self.p), method='linear'))
                #use griddata to interpolate with s & P the superheated table
                self.h = float(griddata((scol, pcol), hcol, (self.s, self.p), method='linear'))
                #use griddata to interpolate with s & P the superheated table
        #endregion

    def print(self):
        """
        This prints a nicely formatted report of the steam properties.
        :return: nothing, just prints to screen
        """
        print('Name: ', self.name)
        if self.x < 0.0:
            print('Region: compressed liquid')
        else:
            print('Region: ', self.region)
        print('p = {:0.2f} kPa'.format(self.p))
        if self.x >= 0.0:
            print('T = {:0.1f} degrees C'.format(self.T))
        print('h = {:0.2f} kJ/kg'.format(self.h))
        if self.x >= 0.0:
            print('s = {:0.4f} kJ/(kg K)'.format(self.s))
            if self.region == 'Saturated':
                print('v = {:0.6f} m^3/kg'.format(self.v))
                print('x = {:0.4f}'.format(self.x))
        print()


# endregion

# region function definitions
def main():
    """Display an example of steam calls and calculations to prove
    functionality to user before progessing. This is done by creating
    scenarios to calculate properties at inlet and outlet for turbine and pump"""
    inlet = steam(7350, name='Turbine Inlet')  #not enough information to calculate
    inlet.x = 0.9  #90 percent quality (q)
    inlet.calc() #calculate each property for inlet with given pressure
    inlet.print() #print output by calling print function

    h1 = inlet.h #store vals of h and s as h1 and s1 to calculate for outlet
    s1 = inlet.s
    print(h1, s1, '\n')

    outlet = steam(100, s=inlet.s, name='Turbine Exit')
    #call steam for outlet, then calculate and print properties at exit
    outlet.print()
    #repeat for pump inlet given pressure and enthalpy
    another = steam(8575, h=2050, name='State 3')
    another.print()
    #repeat for pump outlet
    yetanother = steam(8575, h=3125, name='State 4')
    yetanother.print()


# endregion

# region function calls
if __name__ == "__main__":
    main()
# endregion
