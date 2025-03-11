# region imports
from Rankine_stem import rankine
from Steam_stem import steam
#endregion imports

#main region
def main():
    """
    Main function to test Rankine cycle analysis for two different cases:
    1) Saturated steam enters the turbine (assumed by default)
    2) Superheated steam enters the turbine (T1=1.7 * Tsat)
    """
    p_high = 8000  #kPa high end (inlet)
    p_low = 8  #kPa low end (outlet)

    #case 1: saturated vapor turbine inlet
    rankine1 = rankine(p_high=p_high, p_low=p_low, name="Rankine Cycle with Saturated Steam") #run rankine for sat_turbine
    efficiency1 = rankine1.calc_efficiency() #efficiency of saturated

    print("\n" + "=" * 25) #prints 25 '=' for a visual line break heading
    print(" Rankine Cycle Analysis: Saturated Steam") #header
    print("=" * 25) #line break
    rankine1.print_summary() #print ranking cycle for sat_steam

    #case 2: superheated steam turbine (inlet, T1=1.7 * Tsat) for Tsat at p_high
    sat_steam = steam(p_high, x=1)  #saturated steam at p_high
    T1_superheated = 1.7 * sat_steam.T  #Superheated temperature

    rankine2 = rankine(p_high=p_high, p_low=p_low, t_high=T1_superheated, name="Rankine Cycle with Superheated Steam")
    #run ranking function (cycle) for SHV
    efficiency2 = rankine2.calc_efficiency() #finds efficiency of SHV

    print("\n" + "=" * 25) #separation (25x '=') to indicate SH output section
    print(" Rankine Cycle Analysis: Superheated Steam") #header
    print("=" * 25) #line break
    rankine2.print_summary() #prints rankine cycle for SHV


# endregion

#call main to display rankine test
if __name__ == "__main__":
    main()
# endregion
