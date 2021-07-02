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
def performPCA(csvfile, weightsfile, average=1, start_time=0, end_time=0, bitstart=0, bitend=15, bandstart=13, bandend=115, vidnum=1):

    print(f'csvfile {csvfile}')
    print(f'weightsfile {weightsfile}')
    print(f'average {average}')
    print(f'start_time {start_time}')
    print(f'end_time {end_time}')
    print(f'bitstart {bitstart}')
    print(f'bitend {bitend}')


    # config for which dimensions to start and end for, this value can be narrowed.
    # 13 is the minimum starting point
    # if from dimension 5 is required, add 5 to the START param
    START = bandstart
    # END = bandend
    END = bandend

    df_orig = pd.read_csv(csvfile, header=None)
    df_weight = pd.read_csv(weightsfile, header=None)

    # remove the dimensions we want to cut
    df_cut = df_orig.loc[:, START:END]

    #reduce based on date range
    # set time index so we can cut the range based on the start and end times for each video
    df_orig[3] = df_orig[3].astype(str)
    df_orig['time_dec'] = df_orig[3].str.rsplit(".", 1).str[1]
    df_orig['time_with_dec'] = df_orig[2] + "." + df_orig['time_dec']

    df_cut['time'] = pd.to_datetime(df_orig['time_with_dec'], format="%y/%m/%d %H:%M:%S.%f")
    df_orig['time'] = pd.to_datetime(df_orig['time_with_dec'], format="%y/%m/%d %H:%M:%S.%f")
    df_cut['pixelindex'] = (df_orig[0] % 16)
    df_cut = df_cut.set_index(['time'])
    df_orig = df_orig.set_index(['time'])

    print(f'df_orig {len(df_orig)}')

    #if start_time == 0 then get the default start and end time of the whole datafram
    starttimemicroseconds = 0
    endtimemicroseconds = 0
    if start_time == 0:
        #TODO get the first start time
        start_time = df_orig.iloc[0].name.strftime('%Y-%m-%d %H:%M:%S')
        # start_time = "2020-01-15 14:16:00"
        #TODO get the end time
        end_time = df_orig.iloc[len(df_orig) - 1].name.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]

        # end_time = "2020-01-15 14:20:00"
    else:
        #populate the date with the times
        date = df_cut.iloc[0].name.strftime('%Y-%m-%d')
        start_time = date +" " + start_time
        end_time = date + " " + end_time

    print(f'df_cut {len(df_cut)}')

    df_cut_withpixelindex = df_cut[(df_cut.index >=start_time) & (df_cut.index <=end_time) ]

    print(f'df_cut[(df_cut.index < start_time)]) {len(df_cut[(df_cut.index < start_time)])}')
    print(f'df_cut[(df_cut.index <=end_time)) {len(df_cut[(df_cut.index >end_time)])}')

    print(f'df_cut_withpixelindex {len(df_cut_withpixelindex)}')

    #drop pixelindex for now and add it later
    df_cut_temp = df_cut_withpixelindex.drop(["pixelindex"], axis=1)

    print(f'df_cut_temp {len(df_cut_temp)}')

    #apply moving average:
    if average > 1:
        for column in df_cut_temp.columns:
            # print(column)
            df_cut_temp[column] = df_cut_temp[column].rolling(window=average).mean()

        #remove average rows
        df_cut_withpixelindex = df_cut_withpixelindex.iloc[average-1:]
        df_cut_temp = df_cut_temp.iloc[average-1:]

    print(f'df_cut_temp after average {len(df_cut_temp)}')

    #apply weights
    df_weights_cut = df_weight.loc[:, START:END]
    for index, value in enumerate(df_weights_cut.values[0]):
        # print(index)
        df_cut_temp[START + index] = df_cut_temp[START + index] * value

    print(f'df_cut_temp after weights {len(df_cut_temp)}')

    # construct PCA
    pca = PCA(n_components=3)
    dt = pca.fit_transform(df_cut_temp.iloc[:,:].values)
    df_pca = pd.DataFrame(data=dt)
    columns = [0, 1, 2]
    df_pca.columns = columns

    # normalize
    scaler = MaxAbsScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df_pca), columns=df_pca.columns)

    for i in range(0, 3):
        # for negative values we assign 0>127. for Positive values we assign 128-255
        df_scaled.iloc[:, i] = (df_scaled.iloc[:, i]).apply(lambda x: abs(x) * 127 if x < 0 else (x * 127) + 127)

    #copy pixelindex over
    df_scaled['time'] = df_cut_withpixelindex.index
    df_scaled = df_scaled.set_index(['time'])
    df_scaled['pixelindex'] = df_cut_withpixelindex["pixelindex"]

    print(f'df_scaled {len(df_scaled)}')

    firstindex = 0
    for i in range(0, 16):
        if df_scaled.iloc[i]['pixelindex'] == 0:
            firstindex = i

    # start the image with 0 index because sometimes when you cut, the first row might not be sensor 0
    df_scaled_temp = df_scaled.iloc[firstindex:]

    print(f'df_scaled_temp {len(df_scaled_temp)}')

    # create image
    width = math.ceil(len(df_scaled_temp) / 16)
    rgbArray = np.zeros([16, width, 3], dtype=np.uint8)
    # timeMap = np.chararray([16, width])
    timeMap = [[0 for x in range(width)] for y in range(16)]
    # timeMap= [[0] * width] * 16

    print(f'length of width: {width}')

    t = 0
    # for labels
    x_pos = []
    x_labels = []
    x_pos2 = []
    x_labels2 = []
    position = 0
    # this will be the label for the time
    timelabel = df_scaled_temp.iloc[0].name.strftime('%H:%M:%S')
    labelposition = 0
    print(f'length of df_scaled_temp: {len(df_scaled_temp)}')

    for i in range(0, len(df_scaled_temp), 16):
        # print(i)
        # print(t)
        columns = []
        position = i
        for j in range(0, 16):
            # print(f'j: {j}')
            rgb = []

            #end array check
            if position >= len(df_scaled_temp):
                continue

            #get me the pixelindex
            pixelindex = df_scaled_temp['pixelindex'][position]

            if pixelindex == j:
                for k in range(0, 3):
                    if (position < len(df_scaled_temp)):
                        rgb.append(int(df_scaled_temp[k][position]))
            else:
                #we dont have a pixel for this pixel index make rgb white
                rgbArray[j, t] = [255,255,255]

            if len(rgb) > 0:
                rgbArray[j, t] = rgb
                timeMap[j][t] = df_scaled_temp.iloc[position].name.strftime('%H:%M:%S.%f')[:-5]
                position += 1
            else:
                print(f' Position {position} does not have data')

            if position<len(df_scaled_temp):
                timelabel2 = df_scaled_temp.iloc[position].name.strftime('%H:%M:%S')

        # now get the label if it has changed
        if timelabel != timelabel2:

            if labelposition == 0:
                labelposition = math.ceil(position / 16)
                x_pos.append(labelposition)
                x_labels.append(timelabel2)
                timelabel = timelabel2
            else:
                labelposition = math.ceil(position / 16)
                x_pos.append(labelposition)
                # rgbArray [j, t] = [255,255,255]
                x_labels.append(timelabel2)
                timelabel = timelabel2

        # end loop
        t += 1

        # # every 160 rows we label
        # temp = i / 16
        # if temp % 10 == 0:
        #     x_pos2.append(temp)
        #     x_labels2.append(df_scaled_temp.iloc[i].name.strftime('%H:%M:%S'))

    rgbArray  = rgbArray[bitstart:bitend+1,:,:]
    timeMap = timeMap[bitstart:bitend+1]

    ret_start_time = df_scaled_temp.iloc[0].name.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]

    # create the image without labels
    img2 = Image.fromarray(rgbArray )
    img2.save(f'{vidnum}.png')

    # create figure with labels
    fig, ax = plt.subplots(1, 1)
    ax.set_xticklabels(x_labels)
    ax.set_xticks(x_pos)
    ax.imshow(rgbArray )

    fig.set_size_inches(100, 3.2)
    fig.savefig(f'labelled-{vidnum}.png', dpi=100)

    print(f'length of rgbArray : {len(rgbArray[0])}')
    print(f'length of timeMap : {len(timeMap[0])}')

    print(f'length of x_labels: {len(x_labels)}')
    print(x_labels)
    print(x_pos)
    print(ret_start_time)
    print(end_time)
    print(average)

    return rgbArray , timeMap, x_labels, x_pos, ret_start_time, end_time, average
    # return rgbArray, x_labels, x_pos, ret_start_time, end_time, average



# #
#
# # start time must be in format 14:50:20.1
# #
# def performPCA(csvfile, weightsfile, average=1, start_time=0, end_time=0, bitstart=0, bitend=15, bandstart=13, bandend=220, vidnum=1):
#     # config for which dimensions to start and end for, this value can be narrowed.
#     # 13 is the minimum starting point
#     # if from dimension 5 is required, add 5 to the START param
#     START = bandstart
#     # END = bandend
#     END = 115
#     df_orig = pd.read_csv(csvfile, header=None)
#
#     df_weight = pd.read_csv(weightsfile, header=None)
#
#     # remove the dimensions we want to cut
#     df_cut = df_orig.loc[:, START:END]
#
#     #reduce based on date range
#     # set time index so we can cut the range based on the start and end times for each video
#     df_orig[3] = df_orig[3].astype(str)
#     df_orig['time_dec'] = df_orig[3].str.rsplit(".", 1).str[1]
#     df_orig['time_with_dec'] = df_orig[2] + "." + df_orig['time_dec']
#
#     df_cut['time'] = pd.to_datetime(df_orig['time_with_dec'], format="%y/%m/%d %H:%M:%S.%f")
#     df_orig['time'] = pd.to_datetime(df_orig['time_with_dec'], format="%y/%m/%d %H:%M:%S.%f")
#     df_cut['pixelindex'] = (df_orig[0] % 16)
#     df_cut = df_cut.set_index(['time'])
#     df_orig = df_orig.set_index(['time'])
#
#     #if start_time == 0 then get the default start and end time of the whole datafram
#     starttimemicroseconds = 0
#     endtimemicroseconds = 0
#     if start_time == 0:
#         #TODO get the first start time
#         start_time = df_orig.iloc[0].name.strftime('%Y-%m-%d %H:%M:%S')
#         # start_time = "2020-01-15 14:16:00"
#         #TODO get the end time
#         end_time = df_orig.iloc[len(df_orig) - 1].name.strftime('%Y-%m-%d %H:%M:%S')
#
#         # end_time = "2020-01-15 14:20:00"
#     else:
#         #populate the date with the times
#         date = df_cut.iloc[0].name.strftime('%Y-%m-%d')
#         start_time = date +" " + start_time
#         end_time = date + " " + end_time
#
#
#     df_cut_withpixelindex = df_cut[(df_cut.index >=start_time) & (df_cut.index <=end_time) ]
#     #drop pixelindex for now and add it later
#     df_cut_temp = df_cut_withpixelindex.drop(["pixelindex"], axis=1)
#
#     #apply moving average:
#     if average > 1:
#         for column in df_cut_temp.columns:
#             # print(column)
#             df_cut_temp[column] = df_cut_temp[column].rolling(window=average).mean()
#
#         #remove average rows
#         df_cut_withpixelindex = df_cut_withpixelindex.iloc[average-1:]
#         df_cut_temp = df_cut_temp.iloc[average-1:]
#
#     #apply weights
#     df_weights_cut = df_weight.loc[:, START:END]
#     for index, value in enumerate(df_weights_cut.values[0]):
#         # print(index)
#         df_cut_temp[START + index] = df_cut_temp[START + index] * value
#
#
#     # construct PCA
#     pca = PCA(n_components=3)
#     dt = pca.fit_transform(df_cut_temp.iloc[:,:].values)
#     df_pca = pd.DataFrame(data=dt)
#     columns = [0, 1, 2]
#     df_pca.columns = columns
#
#     # normalize
#     scaler = MaxAbsScaler()
#     df_scaled = pd.DataFrame(scaler.fit_transform(df_pca), columns=df_pca.columns)
#
#     for i in range(0, 3):
#         # for negative values we assign 0>127. for Positive values we assign 128-255
#         df_scaled.iloc[:, i] = (df_scaled.iloc[:, i]).apply(lambda x: abs(x) * 127 if x < 0 else (x * 127) + 127)
#
#     #copy pixelindex over
#     df_scaled['time'] = df_cut_withpixelindex.index
#     df_scaled = df_scaled.set_index(['time'])
#     df_scaled['pixelindex'] = df_cut_withpixelindex["pixelindex"]
#
#     firstindex = 0
#     for i in range(0, 16):
#         if df_scaled.iloc[i]['pixelindex'] == 0:
#             firstindex = i
#
#     # start the image with 0 index because sometimes when you cut, the first row might not be sensor 0
#     df_scaled_temp = df_scaled.iloc[firstindex:]
#
#     # create image
#     width = math.ceil(len(df_scaled_temp) / 16)
#     array2 = np.zeros([16, width, 3], dtype=np.uint8)
#     print(f'length of width: {width}')
#
#     t = 0
#     # for labels
#     x_pos = []
#     x_labels = []
#     x_pos2 = []
#     x_labels2 = []
#     position = 0
#     # this will be the label for the time
#     timelabel = df_scaled_temp.iloc[0].name.strftime('%H:%M:%S')
#     labelposition = 0
#     lastPositionAdded = 0
#     print(f'length of df_scaled_temp: {len(df_scaled_temp)}')
#
#     for i in range(0, len(df_scaled_temp), 16):
#         # print(i)
#         # print(t)
#         columns = []
#         position = i
#         for j in range(0, 16):
#             # print(f'j: {j}')
#             rgb = []
#
#             #end array check
#             if position >= len(df_scaled_temp):
#                 continue
#
#             #get me the pixelindex
#             pixelindex = df_scaled_temp['pixelindex'][position]
#
#             if pixelindex == j:
#                 for k in range(0, 3):
#                     if (position < len(df_scaled_temp)):
#                         rgb.append(int(df_scaled_temp[k][position]))
#             else:
#                 #we dont have a pixel for this pixel index make rgb white
#                 array2[j, t] = [255,255,255]
#
#             if len(rgb) > 0:
#                 array2[j, t] = rgb
#                 position += 1
#             else:
#                 print(f'SOMETHING HAPPENDED HERE position {position}')
#
#             if position<len(df_scaled_temp):
#                 timelabel2 = df_scaled_temp.iloc[position].name.strftime('%H:%M:%S')
#
#
#
#             # now get the label if it has changed
#             if timelabel != timelabel2:
#
#                 if labelposition == 0:
#                     labelposition = math.ceil(position / 16)
#                     x_pos.append(labelposition)
#                     lastPositionAdded=labelposition*16
#                     x_labels.append(timelabel2)
#                     timelabel = timelabel2
#                 else:
#                     labelposition +=4
#                     x_pos.append(labelposition)
#                     lastPositionAdded += 4*16
#                     #for debug make it white
#                     # array2[j, t] = [255,255,255]
#                     x_labels.append(timelabel2)
#                     timelabel = timelabel2
#
#         # end loop
#         t += 1
#
#         #pad one column if we are behind
#         if labelposition > 0 and (lastPositionAdded > position):
#             print(f'mismatch by {lastPositionAdded - position}')
#
#             #how many are we behind
#             behind = lastPositionAdded - position
#             print(f' lastPositionAdded {lastPositionAdded} - current position {position} behind by {behind} ')
#             if behind == 16:
#                 #pad one column
#                 for k in range(0, 16):
#                     array2[k, t] = [255, 255, 255]
#                 #increment column counter
#                 t += 1
#                 #append end array
#                 newSize = len(array2[0]) + 1
#                 temp = np.zeros([16, newSize, 3], dtype=np.uint8)
#                 temp[:, 0:-1, :] = array2[:newSize - 1]
#                 # array2 = np.zeros([16, newSize, 3], dtype=np.uint8)
#                 array2 = temp[:newSize - 1]
#                 #update last position added equal to position
#                 lastPositionAdded = position
#
#             # print(f'position {math.ceil(position / 16)}')
#             # print(f'labelposition {labelposition}')
#             # lastPositionAdded = position
#
#
#         # # every 160 rows we label
#         # temp = i / 16
#         # if temp % 10 == 0:
#         #     x_pos2.append(temp)
#         #     x_labels2.append(df_scaled_temp.iloc[i].name.strftime('%H:%M:%S'))
#
#     array2 = array2[bitstart:bitend+1,:,:]
#     ret_start_time = df_scaled_temp.iloc[0].name.strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]
#
#
#     # create the image without labels
#     img2 = Image.fromarray(array2)
#     img2.save(f'{vidnum}.png')
#
#     # create figure with labels
#     fig, ax = plt.subplots(1, 1)
#     ax.set_xticklabels(x_labels)
#     ax.set_xticks(x_pos)
#     ax.imshow(array2)
#
#     fig.set_size_inches(100, 3.2)
#     fig.savefig(f'labelled-{vidnum}.png', dpi=100)
#
#     print(f'length of array2: {len(array2[0])}')
#     print(f'length of x_labels: {len(x_labels)}')
#     print(x_labels)
#     print(x_pos)
#     print(ret_start_time)
#     print(end_time)
#     print(average)
#
#     return array2, x_labels, x_pos, ret_start_time, end_time, average



# def performPCAPhase1():
#
#     # change the values here for different out put files
#     CONFIG = [{'csvfile':'FLT7_dc_20210108.csv',
#                'videos':
#                   [{'vidNumber':'PalmFlight7-1',
#                    'start_time':'2020-01-15 14:16:00',
#                    'end_time':'2020-01-15 14:20:00'
#                   },
#                   {'vidNumber':'PalmFlight7-1b',
#                    'start_time':'2020-01-15 14:20:00',
#                    'end_time':'2020-01-15 14:25:00'
#                   },
#                   {'vidNumber':'PalmFlight7-2',
#                    'start_time':'2020-01-15 14:25:00',
#                    'end_time':'2020-01-15 14:30:00'
#                   },
#                   {'vidNumber':'PalmFlight7-3',
#                    'start_time':'2020-01-15 14:30:00',
#                    'end_time':'2020-01-15 14:35:00'
#                   },
#                   {'vidNumber':'PalmFlight7-3b',
#                    'start_time':'2020-01-15 14:35:00',
#                    'end_time':'2020-01-15 14:39:23'
#                   }]},
#               {'csvfile': 'FLT9_dc_20210108.csv',
#               'videos':
#                [{'vidNumber':'PalmFlight9-1',
#                    'start_time':'2020-01-16 12:06:54',
#                    'end_time':'2020-01-16 12:11:33'
#                   },
#                   {'vidNumber':'PalmFlight9-1b',
#                    'start_time':'2020-01-16 12:11:33',
#                    'end_time':'2020-01-16 12:16:33'
#                   },
#                   {'vidNumber':'PalmFlight9-NoUse',
#                    'start_time':'2020-01-16 12:21:33',
#                    'end_time':'2020-01-16 12:26:33'
#                   },
#                   {'vidNumber':'PalmFlight9-3',
#                    'start_time':'2020-01-16 12:26:33',
#                    'end_time':'2020-01-16 12:31:33'
#                   },
#                 ]
#               }
#              ]
#
#     # config for which dimensions to start and end for, this value can be narrowed.
#     # 13 is the minimum starting point
#     # if from dimension 5 is required, add 5 to the START param
#     START=13
#     END=115
#
#     # loop for each config file, which is a csv file, there are snippets of csv ranges
#     for config in CONFIG:
#
#         df_orig = pd.read_csv(config['csvfile'], header=None)
#
#         # remove the dimensions we want to cut
#         df_cut = df_orig.loc[:, START:END]
#
#         # construct PCA
#         pca = PCA(n_components=3)
#         dt = pca.fit_transform(df_cut.iloc[:, :].values)
#         df_pca = pd.DataFrame(data=dt)
#         columns = [0, 1, 2]
#         df_pca.columns = columns
#
#         # normalize
#         scaler = MaxAbsScaler()
#         df_scaled = pd.DataFrame(scaler.fit_transform(df_pca), columns=df_pca.columns)
#
#         for i in range(0, 3):
#             # for negative values we assign 0>127. for Positive values we assign 128-255
#             df_scaled.iloc[:, i] = (df_scaled.iloc[:, i]).apply(lambda x: abs(x) * 127 if x < 0 else (x * 127) + 127)
#
#         # set time index so we can cut the range based on the start and end times for each video
#         df_scaled['time'] = pd.to_datetime(df_orig[2], format="%y/%m/%d %H:%M:%S")
#         df_scaled['pixelindex'] = (df_orig[0] % 16)
#         df_scaled = df_scaled.set_index(['time'])
#
#         for item in config['videos']:
#             vidNumber = item['vidNumber']
#             start_time = item['start_time']
#             end_time = item['end_time']
#             df_scaled_temp = df_scaled.loc[start_time: end_time]
#
#             # get the first 0 index so we can know which is the first sensor
#             firstindex = 0
#             for i in range(0, 15):
#                 if df_scaled_temp.iloc[i]['pixelindex'] == 0:
#                     firstindex = i
#
#             # start the image with 0 index because sometimes when you cut, the first row might not be sensor 0
#             df_scaled_temp = df_scaled_temp.iloc[firstindex:]
#
#             # create image
#             width = (len(df_scaled_temp) // 16) + 1
#             array2 = np.zeros([16, width, 3], dtype=np.uint8)
#
#             t = 0
#             # for labels
#             x_pos = []
#             x_labels = []
#
#             for i in range(0, len(df_scaled_temp), 16):
#
#                 columns = []
#                 position = i
#                 for j in range(0, 16):
#                     rgb = []
#                     for k in range(0, 3):
#                         if (position < len(df_scaled_temp)):
#                             rgb.append(int(df_scaled_temp[k][position]))
#
#                     if len(rgb) > 0:
#                         array2[j, t] = rgb
#                         position += 1
#                 t += 1
#
#                 # every 160 rows we label
#                 temp = i / 16
#                 if temp % 10 == 0:
#                     x_pos.append(temp)
#                     x_labels.append(df_scaled_temp.iloc[i].name.strftime('%H:%M:%S'))
#
#             # return array2, x_labels, x_pos
#             # create the image without labels
#             img2 = Image.fromarray(array2)
#             img2.save(f'{vidNumber}.png')
#
#             # create figure with labels
#             fig, ax = plt.subplots(1, 1)
#             ax.set_xticklabels(x_labels)
#             ax.set_xticks(x_pos)
#             ax.imshow(array2)
#
#
#             fig.set_size_inches(100, 3.2)
#             fig.savefig(f'labelled-{vidNumber}.png', dpi=100)