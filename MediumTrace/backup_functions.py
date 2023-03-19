def sampling_time(y):
    data_points = []
    sample_time = 4e-6
    for i,amplitude in enumerate(y):
        data_points.append([sample_time*(i+1),amplitude])
    return data_points


def power_threshold_nodes(datapoints,busy_threshold):
    mean_a = 0
    values_a = []
    i_a = 0
    std_a = 0
    mean_b = 0
    values_b = []
    i_b = 0
    std_b = 0
    mean_c = 0
    values_c =[]
    i_c = 0
    std_c = 0
    mean_ack = 0
    values_ack = []
    i_ack = 0
    std_ack = 0
    for datapoint in datapoints:
        if 0.5164 < datapoint[1] < 0.6:
            mean_a += datapoint[1]
            i_a +=1
            values_a.append(datapoint[1])
        elif 0.012 < datapoint[1] < 0.07:
            mean_b += datapoint[1]
            i_b +=1
            values_b.append(datapoint[1])
        elif busy_threshold < datapoint[1] < 0.017:
            mean_c += datapoint[1]
            i_c +=1
            values_c.append(datapoint[1])
        elif 0.17 < datapoint[1] < 0.27:
            mean_ack += datapoint[1]
            i_ack +=1
            values_ack.append(datapoint[1])
    mean_a = mean_a/i_a
    mean_b = mean_b/i_b
    mean_c = mean_c/i_c
    mean_ack = mean_ack/i_ack
    for i in values_a:
        std_a = std_a + (i - mean_a)**2
    for i in values_b:
        std_b = std_b + (i - mean_b)**2
    for i in values_c:
        std_c = std_c + (i - mean_c)**2
    for i in values_ack:
        std_ack = std_ack + (i - mean_ack)**2
    thrs_a = 8*mean_a+math.sqrt(std_a /(i_a-1))*16
    thrs_b = 8*mean_b+math.sqrt(std_b / (i_b - 1))*16
    thrs_c = 8*mean_c+math.sqrt(std_c / (i_c - 1))*16
    thrs_ack = 8*mean_ack+math.sqrt(std_ack / (i_ack - 1))*16

    return mean_a,mean_ack


def filter_high(datapoints):
    filtered = []
    for datapoint in datapoints:
        if datapoint[1] < 0.1:
            filtered.append([datapoint[0],0])
        else:
            filtered.append(datapoint)
    return filtered


def communication(datapoints,transmitting_time_abusy_threshold,mean_a,mean_ack):
    """Find intervals of communication"""
    tracking_change = []
    for sample in datapoints:
        tracking_change.append(sample)
        if (sum(tracking_change) / len(tracking_change)) > mean_a*0.8:
            pass

def moving(filtered_datapoints):
    amplitudes = []
    for sample in filtered_datapoints:
        amplitudes.append(sample[1])
    window_size = 10
    i = 0
    moving_average = []
    while i < len(amplitudes) - window_size +1:
        window = amplitudes[i : i+window_size]
        window_average = round(sum(window) / window_size,2)
        moving_average.append(window_average)
        i+=1
    plt.plot(moving_average)
    return moving_average