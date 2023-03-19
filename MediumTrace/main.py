import matplotlib.pyplot as plt
import numpy as np
import math


def read_data(path):
    data = []
    with open(path) as file:
        for sample in file:
            dp = sample.strip().split(' ')
            data.append([float(dp[0]),float(dp[1])])
    return data

def calc_amplitude(data):
    amplitudes = []
    for complex_number in data:
        amplitudes.append(math.sqrt((math.pow(complex_number[0],2) + math.pow(complex_number[1],2))))
    return amplitudes


def plot_communication(datapoints,plot=True):
    if plot:
        plt.plot(datapoints)
        plt.show()


def power_threshold_nodes(datapoints):
    mean_a = 0
    values_a = []
    i_a = 0
    mean_ack = 0
    values_ack = []
    i_ack = 0
    for datapoint in datapoints:
        if 0.5164 < datapoint < 0.7:
            mean_a += datapoint
            i_a += 1
            values_a.append(datapoint)
        elif 0.2 < datapoint < 0.33:
            mean_ack += datapoint
            i_ack += 1
            values_ack.append(datapoint)
    mean_a = mean_a / i_a
    mean_ack = mean_ack / i_ack

    return mean_a, mean_ack


def detect_a(data,activation_a,activation_ack, num_samples_a):
    number_of_frames = 0
    number_of_fresh_frames = 0
    number_of_acks_for_a = 0
    number_of_fresh_acks_for_a = 0
    a_sending = 0
    ack_sending = 0
    start_a = 0
    start_ack = 0
    frame_done_now_ack = 0
    ack_done_now = 0
    last_frame_acked = 0
    for idx,sample in enumerate(data):
        if idx == 141500:
            print('')
        if sample > activation_a*0.8 and a_sending == 0 and frame_done_now_ack == 0 and ack_sending == 0:
            """Start sending frame a"""
            start_a = idx
            a_sending = 1
        elif sample < activation_a*0.3 and a_sending == 1:
            """Sending of frame a is done or interrupted"""
            a_sending = 0
            end_a = idx
            time_sending_a = end_a - start_a
            if time_sending_a >= num_samples_a*0.5:
                """attempt to send frame was made"""
                frame_done_now_ack = 1
                number_of_frames += 1
                if ack_done_now == 1:
                    number_of_fresh_frames +=1
                    ack_done_now = 0
                continue

        if frame_done_now_ack == 1 and sample > (activation_ack*0.6) and ack_sending == 0:
            ack_sending = 1
            start_ack = idx
            continue
        elif 0.0075 < sample < activation_ack*0.7 and ack_sending ==1:
            end_ack = idx
            time_sending_ack = end_ack - start_ack
            if time_sending_ack < 20:
                """Very short communication --> we assume an ACK"""
                if last_frame_acked ==1:
                    number_of_fresh_acks_for_a +=1
                    last_frame_acked = 0
                number_of_acks_for_a += 1
                ack_sending = 0
                frame_done_now_ack = 0
                ack_done_now = 1
                last_frame_acked = 1
                continue
            elif time_sending_ack > 100:
                """Not an ack probably a different frame from node A (only one with higher powerspikes then ACK)"""
                number_of_frames+=1
                ack_done_now = 0
                last_frame_acked = 0
                ack_sending = 0
                frame_done_now_ack = 1
        if sample < busy_threshold and data[idx+1] < busy_threshold and frame_done_now_ack==1:
            """Backoff Counter initiated restart process"""
            a_sending = 0
            ack_sending = 0
            start_a = 0
            start_ack = 0
            frame_done_now_ack = 0
            ack_done_now = 0
            last_frame_acked = 0


    print('\n-------------------------------------------------------------------------------')
    print(f'Total number of packets from node A                    :{number_of_frames}')
    print(f'Total number of packets with ACK from node A           :{number_of_acks_for_a}')
    print(f'Total number of fresh packets from node A              :{number_of_fresh_frames}')
    print(f'Total number of fresh packets with ACK from node A     :{number_of_fresh_acks_for_a}')
    print('-------------------------------------------------------------------------------')






if __name__ == '__main__':
    """Parameters"""
    sample_time = 4e-6
    busy_threshold = 0.005
    packet_size = 1500*8
    node_a = 18e+6
    node_b = 12e+6
    node_c = 6e+6
    num_samples_a = math.ceil((packet_size / node_a) / sample_time)
    num_samples_b = (packet_size / node_b) / sample_time
    num_samples_c = (packet_size / node_c) / sample_time

    data = read_data("MAC_testdata2")
    y = calc_amplitude(data)
    plot_communication(y,False)
    activate_a,activate_ack = power_threshold_nodes(y)
    detect_a(y,activate_a,activate_ack,num_samples_a)





