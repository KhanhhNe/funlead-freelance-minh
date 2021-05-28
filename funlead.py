import matplotlib.pyplot as plt
# from matplotlib.pyplot import figure
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from PIL import Image
from sklearn.preprocessing import MaxAbsScaler
from datetime import datetime
import math

#

# start time must be in format 14:50:20.1
#
def performPCA(csvfile, weightsfile, start_time=0, end_time=0, bitstart=0, bitend=15, bandstart=13, bandend=220,vidnum=1):
    # config for which dimensions to start and end for, this value can be narrowed.
    # 13 is the minimum starting point
    # if from dimension 5 is required, add 5 to the START param
    START = bandstart
    END = bandend

    df_orig = pd.read_csv(csvfile, header=None)

    df_weight = pd.read_csv(weightsfile, header=None)

    # remove the dimensions we want to cut
    df_cut = df_orig.loc[:, START:END]
    df_weights_cut = df_weight.loc[:, START:END]

    for index, value in enumerate(df_weights_cut.values[0]):
        # print(index)
        df_cut[START + index] = df_cut[START + index] * value

    # construct PCA
    pca = PCA(n_components=3)
    dt = pca.fit_transform(df_cut.iloc[:, :].values)
    df_pca = pd.DataFrame(data=dt)
    columns = [0, 1, 2]
    df_pca.columns = columns

    # normalize
    scaler = MaxAbsScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df_pca), columns=df_pca.columns)

    for i in range(0, 3):
        # for negative values we assign 0>127. for Positive values we assign 128-255
        df_scaled.iloc[:, i] = (df_scaled.iloc[:, i]).apply(lambda x: abs(x) * 127 if x < 0 else (x * 127) + 127)

    # set time index so we can cut the range based on the start and end times for each video
    df_scaled['time'] = pd.to_datetime(df_orig[2], format="%y/%m/%d %H:%M:%S")
    df_scaled['pixelindex'] = (df_orig[0] % 16)
    df_scaled = df_scaled.set_index(['time'])

    # vidNumber = item['vidNumber']

    #if start_time == 0 then get the default start and end time of the whole datafram
    starttimemicroseconds = 0
    endtimemicroseconds = 0
    if start_time == 0:
        #TODO get the first start time
        start_time = df_scaled.iloc[0].name.strftime('%Y-%m-%d %H:%M:%S')
        # start_time = "2020-01-15 14:16:00"
        #TODO get the end time
        end_time = df_scaled.iloc[len(df_scaled)-1].name.strftime('%Y-%m-%d %H:%M:%S')
        # end_time = "2020-01-15 14:20:00"
    else:
        #populate the date with the times
        date = df_scaled.iloc[0].name.strftime('%Y-%m-%d')

        #remove the decimal from start time and endtime
        start_time, starttimemicroseconds = start_time.split(".",1)
        end_time, endtimemicroseconds = end_time.split(".",1)
        starttimemicroseconds = int(starttimemicroseconds)
        endtimemicroseconds = int(endtimemicroseconds)

        start_time = date +" " + start_time
        end_time = date + " " + end_time

    df_scaled_temp = df_scaled.loc[start_time: end_time]

    if starttimemicroseconds > 0 :
        #get the first row
        firstrow = int(64*(starttimemicroseconds/10))
        lastrow =int(len(df_scaled_temp) - (64*(1-(endtimemicroseconds/10))))

        #cut the dataframe again:
        df_scaled_temp = df_scaled_temp.iloc[firstrow: lastrow]
    # get the first 0 index so we can know which is the first sensor

    firstindex = 0
    for i in range(0, 16):
        if df_scaled_temp.iloc[i]['pixelindex'] == 0:
            firstindex = i

    # start the image with 0 index because sometimes when you cut, the first row might not be sensor 0
    df_scaled_temp = df_scaled_temp.iloc[firstindex:]

    # create image
    width = (len(df_scaled_temp) // 16) + 1
    array2 = np.zeros([16, width, 3], dtype=np.uint8)

    t = 0
    # for labels
    x_pos = []
    x_labels = []
    position = 0
    # this will be the label for the time
    timelabel = df_scaled_temp.iloc[0].name.strftime('%H:%M:%S')
    firstlabel = 0
    for i in range(0, len(df_scaled_temp), 16):
        # print(i)
        # print(t)
        columns = []
        position = i
        for j in range(0, 16):
            rgb = []
            for k in range(0, 3):
                if (position < len(df_scaled_temp)):
                    rgb.append(int(df_scaled_temp[k][position]))

            if len(rgb) > 0:
                array2[j, t] = rgb
                position += 1

            if position<len(df_scaled_temp):
                timelabel2 = df_scaled_temp.iloc[position].name.strftime('%H:%M:%S')

            if timelabel != timelabel2:
                # print(f'timelable 1 {timelabel} timelabel{timelabel2}')
                # print(timelabel2)
                if firstlabel == 0:
                    firstlabel = math.ceil(position / 16)
                    x_pos.append(firstlabel)
                else:
                    firstlabel +=4
                    x_pos.append(firstlabel)

                x_labels.append(timelabel2)
                timelabel = timelabel2
        t += 1

        # # every 160 rows we label
        # temp = i / 16
        # if temp % 4 == 0:
        #     x_pos.append(temp)
        #     x_labels.append(df_scaled_temp.iloc[i].name.strftime('%H:%M:%S'))

    # # create the image without labels
    # img2 = Image.fromarray(array2)
    # img2.save(f'{vidnum}.png')
    #
    # create figure with labels
    # fig, ax = plt.subplots(1, 1)
    # ax.set_xticklabels(x_labels)
    # ax.set_xticks(x_pos)
    # ax.imshow(array2)
    #
    #
    # fig.set_size_inches(100, 3.2)
    # fig.savefig(f'labelled-{vidnum}.png', dpi=100)
    print('\t'.join(x_labels))
    print(''.join(map(lambda p: str(p).ljust(12), x_pos)))

    array2 = array2[bitstart:bitend+1,:,:]

    return array2, x_labels, x_pos, start_time+"."+str(starttimemicroseconds), end_time+"."+str(endtimemicroseconds)



def performPCA2():

    # change the values here for different out put files
    CONFIG = [{'csvfile':'FLT7_dc_20210108.csv',
               'videos':
                  [{'vidNumber':'PalmFlight7-1',
                   'start_time':'2020-01-15 14:16:00',
                   'end_time':'2020-01-15 14:20:00'
                  },
                  {'vidNumber':'PalmFlight7-1b',
                   'start_time':'2020-01-15 14:20:00',
                   'end_time':'2020-01-15 14:25:00'
                  },
                  {'vidNumber':'PalmFlight7-2',
                   'start_time':'2020-01-15 14:25:00',
                   'end_time':'2020-01-15 14:30:00'
                  },
                  {'vidNumber':'PalmFlight7-3',
                   'start_time':'2020-01-15 14:30:00',
                   'end_time':'2020-01-15 14:35:00'
                  },
                  {'vidNumber':'PalmFlight7-3b',
                   'start_time':'2020-01-15 14:35:00',
                   'end_time':'2020-01-15 14:39:23'
                  }]},
              {'csvfile': 'FLT9_dc_20210108.csv',
              'videos':
               [{'vidNumber':'PalmFlight9-1',
                   'start_time':'2020-01-16 12:06:54',
                   'end_time':'2020-01-16 12:11:33'
                  },
                  {'vidNumber':'PalmFlight9-1b',
                   'start_time':'2020-01-16 12:11:33',
                   'end_time':'2020-01-16 12:16:33'
                  },
                  {'vidNumber':'PalmFlight9-NoUse',
                   'start_time':'2020-01-16 12:21:33',
                   'end_time':'2020-01-16 12:26:33'
                  },
                  {'vidNumber':'PalmFlight9-3',
                   'start_time':'2020-01-16 12:26:33',
                   'end_time':'2020-01-16 12:31:33'
                  },
                ]
              }
             ]

    # config for which dimensions to start and end for, this value can be narrowed.
    # 13 is the minimum starting point
    # if from dimension 5 is required, add 5 to the START param
    START=13
    END=115

    print("test")


    # loop for each config file, which is a csv file, there are snippets of csv ranges
    for config in CONFIG:

        df_orig = pd.read_csv(config['csvfile'], header=None)

        # remove the dimensions we want to cut
        df_cut = df_orig.loc[:, START:END]

        # construct PCA
        pca = PCA(n_components=3)
        dt = pca.fit_transform(df_cut.iloc[:, :].values)
        df_pca = pd.DataFrame(data=dt)
        columns = [0, 1, 2]
        df_pca.columns = columns

        # normalize
        scaler = MaxAbsScaler()
        df_scaled = pd.DataFrame(scaler.fit_transform(df_pca), columns=df_pca.columns)

        for i in range(0, 3):
            # for negative values we assign 0>127. for Positive values we assign 128-255
            df_scaled.iloc[:, i] = (df_scaled.iloc[:, i]).apply(lambda x: abs(x) * 127 if x < 0 else (x * 127) + 127)

        # set time index so we can cut the range based on the start and end times for each video
        df_scaled['time'] = pd.to_datetime(df_orig[2], format="%y/%m/%d %H:%M:%S")
        df_scaled['pixelindex'] = (df_orig[0] % 16)
        df_scaled = df_scaled.set_index(['time'])

        for item in config['videos']:
            vidNumber = item['vidNumber']
            start_time = item['start_time']
            end_time = item['end_time']
            df_scaled_temp = df_scaled.loc[start_time: end_time]

            # get the first 0 index so we can know which is the first sensor
            firstindex = 0
            for i in range(0, 15):
                if df_scaled_temp.iloc[i]['pixelindex'] == 0:
                    firstindex = i

            # start the image with 0 index because sometimes when you cut, the first row might not be sensor 0
            df_scaled_temp = df_scaled_temp.iloc[firstindex:]

            # create image
            width = (len(df_scaled_temp) // 16) + 1
            array2 = np.zeros([16, width, 3], dtype=np.uint8)

            t = 0
            # for labels
            x_pos = []
            x_labels = []

            for i in range(0, len(df_scaled_temp), 16):

                columns = []
                position = i
                for j in range(0, 16):
                    rgb = []
                    for k in range(0, 3):
                        if (position < len(df_scaled_temp)):
                            rgb.append(int(df_scaled_temp[k][position]))

                    if len(rgb) > 0:
                        array2[j, t] = rgb
                        position += 1
                t += 1

                # every 160 rows we label
                temp = i / 16
                if temp % 10 == 0:
                    x_pos.append(temp)
                    x_labels.append(df_scaled_temp.iloc[i].name.strftime('%H:%M:%S'))

            # return array2, x_labels, x_pos
            # create the image without labels
            img2 = Image.fromarray(array2)
            img2.save(f'{vidNumber}.png')

            # create figure with labels
            fig, ax = plt.subplots(1, 1)
            ax.set_xticklabels(x_labels)
            ax.set_xticks(x_pos)
            ax.imshow(array2)


            fig.set_size_inches(100, 3.2)
            fig.savefig(f'labelled-{vidNumber}.png', dpi=100)