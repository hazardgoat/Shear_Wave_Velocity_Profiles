'''
Plots velocity profiles and calculates VS30 for selected station stations from the Yong et al. 2013 ARRA report.
'''

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


class Data_Processing():

    def __init__(self, df_stations, attributes):
        self.df_stations = df_stations
        self.attributes = attributes
    

    # calculates VS30 for the data set
    def Calulate_VS30(self, filtered_depth, combined_dict):
        # attempts to calculate the thickness of each layer. In the vent of a failure due to no station data, it subsitues zeros
        try:
            # makes empty array of zeros in the length of how many depth values there are
            thickness = np.zeros(len(filtered_depth))
            # adds the thickness of the first layer to the first position of the array
            thickness[0] = filtered_depth[0]
            # iterates over the rest of the depths and calculates the thickness of each layer. It then adds the thickness to the array
            for i in range(1,len(filtered_depth)):
                thickness[i] = filtered_depth[i]-filtered_depth[i-1]

            # holds the ratios of depth/velocity for the data set
            vs_ratios = []

            # iterates through the thickness and velocity values to calculate the depth/velocity for the data set
            for d, vs, in zip(thickness, combined_dict.values()):
                ratio = d/vs
                vs_ratios.append(ratio)
            # calculates VS30 for the data set
            VS30 = 30/(sum(vs_ratios))
            self.attributes[3].append(VS30)
        except:
            # if there is no data for a station in the data set, an empty array is made for thickness and VS30 is set to 0
            thickness = np.zeros(len(filtered_depth))
            VS30 = 0
            self.attributes[3].append(VS30)
    
        return VS30


    # determines the NEHRP site class for the data set
    def NEHRP_site_class(self, VS30):
        if VS30 < 180:
            siteclass = 'E'
        elif VS30 <= 360:
            siteclass = 'D'
        elif VS30 <= 760:
            siteclass = 'C'
        elif VS30 <= 1500:
            siteclass = 'B'
        else:
            siteclass = 'A'
    
        return siteclass


    # This function iterates through the data set and determines the points nessisary to get a step shaped velocity profile graph.
    # Additionally, it calculates VS30 and the NEHRP site class for the data set.
    def Process_Datasets(self):
        print('Processing data sets...')
        for col in self.df_stations.columns:
            if 'Vs' in col:
                # adds the column name of the previous column (station name) to the names list of the data set
                self.attributes[0].append(self.df_stations.columns[np.argwhere(self.df_stations.columns == col)[0][0]-1])
                # picks out the velocity values of the velocity column and makes them float numbers
                vs = self.df_stations[col].values[1:].astype(float)
                vs = list(vs)

            if 'Depth' in col:
                # picks out the depth values of the depth column and makes them float numbers
                depth = self.df_stations[col].values[1:].astype(float)
                depth = list(depth)
                # creates a dictionary of depth and velocity values
                combined_dict = dict(zip(depth, vs))
                # holds depths and velocities of only the top 30 meters
                filtered_dict = {}
                flag = False
                
                # iterates through the depth/velocity dictionary to capture only values within 30 m of the surface. In the event that a velocity reading jumps from < 30 m to > 30 m, it keeps the final values that contains 30 m
                for d, vs in combined_dict.items():
                    if d < 30:
                        filtered_dict[d] = vs
                    elif d == 30:
                        filtered_dict[d] = vs
                        flag = True
                    elif d > 30 and flag == False:
                        filtered_dict[30] = vs
                        flag = True
                    else:
                        pass

                filtered_depth = list(filtered_dict.keys())

                VS30 = self.Calulate_VS30(filtered_depth, combined_dict)

                # determines the NEHRP site class for the data set
                siteclass = self.NEHRP_site_class(VS30)

                self.attributes[4].append(siteclass)

                # marks the begining of the velocity profile (surface), as the data needs to be 
                flag == False
                
                # empty array to hold velocity values
                arr_vs = np.empty([])
                # array that holds the full, "padded" velocity values
                padded_vs = ''

                # empty array to hold depth values
                arr_depth = np.empty([])
                # array that holds the full, "padded" depth values
                padded_depth = ''

                # gate for cmaking when it is the first layer down from the surface
                start_flag = True
                # holds the "padding" depth
                pad_d = ''


                # iterates over each depth/velocity pair to generate the extra "padding" values needed to plot a step shaped velocity profile
                for d, vs in filtered_dict.items():
                    if start_flag == False:
                        # adds a "padding" velocity to the velocity array so that it can be matched up the the "padding" depth
                        padded_vs = np.hstack((padded_vs, vs))
                        # adds the next "real" velocity to the velocity array
                        padded_vs = np.hstack((padded_vs, vs))

                        # adds a "padding" depth (depth of previous previous iteration) to the depth array so that a step shaped velocity profile can be plotted
                        padded_depth = np.hstack((padded_depth, pad_d))
                        # adds the next "real" depth to the depth array
                        padded_depth = np.hstack((padded_depth, d))

                        # saves the depth so that in the next iteration it can be used as the "padding" value, so that the step shaped graph can be plotted
                        pad_d = d

                    # runs if it is the first layer down from the surface
                    if start_flag == True:
                        # appends the velocity of the first layer to the empty velocity array
                        padded_vs = np.hstack((arr_vs, vs))
                        # removes the first value (zero) from the velocity array, as it is an artifact introduced by appending the velocity to an empty array
                        padded_vs[:1] = vs

                        # appends the depth of the first layer to the empty depth array. The first value (zero) from the depth array is kept because it is desired for the velocity profile to start at the surface
                        padded_depth = np.hstack((arr_depth, d))

                        # saves the depth so that in the next iteration it can be used as the "padding" value, so that the step shaped graph can be plotted
                        pad_d = d
                        start_flag = False

                self.attributes[1].append(padded_depth)
                self.attributes[2].append(padded_vs)

        return self.attributes



# plots the velocity profiles
def Plot_VS_Profiles():
    print('Graphing velocity profiles...')

    # iterates for each station in the data set
    for i in range(len(name)):
        
        # established a figure and subfigure (ax), with a figure size of 8.5 by 11 inches
        fig, ax = plt.subplots(figsize=(8.5,11))
        ax = ax
        
        # sets the text font
        font = 'Arial'


        # data for the x-axis of the plot
        x = velocity_data[i]
        # data for the y axis of the plot
        y = depth_data[i]

        # plots the velocity profile <x-axis data><y-axis data><color+line style><line width><legend text>
        ax.plot(x, y,'k-',lw=2,label=r'{}, $V_{{S30}}$ = {} m/s, Site Class: {}'.format(name[i], round(VS30[i]), siteclass[i]))


        # inverts the y-axis
        plt.gca().invert_yaxis()
        # turns off the grid that normally plots in the figure
        plt.grid(False)
        

        # establishes the max velocity
        vmax = max(velocity_data[i])

        # establishes the min velocity
        vmin = min(velocity_data[i])

        # rounds the min and max velocities to the nearest hundred (e.g. 100, 200, 300). This is done so that the x-axis can scale with the velocity profiles, but maintain a mostly consistant tick spacing/numbering
        r_vmax = int(round(vmax, -2))
        r_vmin = int(round(vmin, -2))


        # This next bit adds a buffer to each side of the velocity profile so that it is easier to see

        # if the difference between min and max velocity is very low, it gives the velocity profile a modest 50 m/s buffer, else the buffer is set to half the difference
        if (r_vmax-r_vmin) <= 0:
            buffer = 50
        else:
            buffer = (r_vmax-r_vmin)/2
        
        # If the buffer around the x-axis min would put it to < 0, it sets it to 0 instead, else the min x-axis value is set to the buffer
        if (vmin-buffer) <= 0:
            xmin = 0
        else:
            xmin = vmin-buffer

        # sets the max x-axis value sto the buffer
        xmax = vmax+buffer
        # sets the number of minor ticks between each major tick
        tick_spacing = 5
        
        # sets the min and max x-axis values on the graph
        ax.set_xlim((xmin), (xmax))
        # sets the spacing of the major ticks to the buffer, while minor ticks are to the spacing
        xstep_major, xstep_minor = buffer, (buffer/tick_spacing)

        # sets x-axis tick frequency for the major ticks (numbered)
        ax.xaxis.set_major_locator(MultipleLocator(xstep_major))
        # sets x-axis tick frequency for the minor ticks (no numbers)
        ax.xaxis.set_minor_locator(MultipleLocator(xstep_minor))
        # sets x-axis tick label font size
        plt.xticks(fontsize=12)

        # sets y-axis tick frequency for the major ticks (numbered)
        ax.yaxis.set_major_locator(MultipleLocator(5))
        # sets y-axis tick frequency for the minor ticks (no numbers)
        ax.yaxis.set_minor_locator(MultipleLocator(1))
        # sets y-axis tick label font size
        plt.yticks(fontsize=12, fontname=font)

        # Sets the tick parameters for major and minor ticks <axi to plot ticks><which type of ticks><directioon of ticks><tick length><tick width><space between numbers and graph><axis of graph to plot additional ticks>
        ax.tick_params(axis='both', which='major', direction="in", length=10, width=1, pad=8, right=True, top=True)
        ax.tick_params(axis='both', which='minor', direction="in", length=5, width=1, pad=8, right=True, top=True)

        # forces the ticks to go all the way to the plot margins
        plt.margins(0, 0)

        ### AXIS LABELS ----------------------------------------------
        # sets y-axis label
        plt.ylabel(r'Depth, $z$ (m)', fontsize=14, fontname=font)
        # sets x-axis label
        plt.xlabel(r'Shear Wave Velocity, $V_S$ (m/s)', fontsize=14, fontname=font)
        
        ### LEGEND ---------------------------------------------- https://www.geeksforgeeks.org/change-the-legend-position-in-matplotlib/
        # establishes a legend
        ax.legend()
        # sets legend position and offset <position><offset>
        ax.legend(loc='upper right', bbox_to_anchor=(0.98, 0.98))
        #ax.legend(loc='lower left', bbox_to_anchor=(0.02, 0.02))

        save_file = os.path.join(main_dir, 'Results', 'Vs_Plot_{}.png'.format(name[i]))
        plt.savefig(save_file)
        #plt.show()



# main directory path
main_dir = r'/home/USER/Desktop/Station_VP_Plots'

# velocity profile data set
stations = os.path.join(main_dir, 'Data', 'Selected_Stations_Yong2013.csv')
# reads the velocity profile data set CSV file into a dataframe
df_stations = pd.read_csv(stations, sep=',')
# holds the staion names within the data set
name = []
# holds depths from the data set, as well as the "padding" points necessary to draw the step shape of a velocity profile graph
depth_data = []
# holds shear wave velocities from the data set, as well as the "padding" points necessary to draw the step shape of a velocity profile graph
velocity_data = []
# holds calculated VS30s for the data set
VS30 = []
# holds determined NEHRP site classes for the data set
siteclass = []

attributes = [name, depth_data, velocity_data, VS30, siteclass]


print('Starting...')
data = Data_Processing(df_stations, attributes)
attributes = data.Process_Datasets()
Plot_VS_Profiles()
print('Complete!')
