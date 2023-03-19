import IPython.lib.display
import matplotlib.pyplot as plt
import numpy as np
import math
import pandas as pd


def BinaryToDecimalData(binary):
    decimal, i, n = 0, 0, 0
    while (binary != 0):
        dec = binary % 10
        decimal = decimal + dec * pow(2, i)
        binary = binary // 10
        i += 1
    return (decimal)


def unpack_txt_file(file):
    with open(file, "r") as f:
        lines = f.read().splitlines()
    return lines


def create_plot(lines, interval, plot):
    time = []
    amplitude = []
    for idx, line in enumerate(lines):
        time_large = interval * (idx + 1)
        time_rounded = float(format(time_large, '.6f'))
        time.append(time_rounded)
        amplitude.append(float(line))
    if plot:
        plt.plot(time, amplitude)
        plt.xlabel('time')
        plt.ylabel('Amplitude')
        plt.show()  # Last Pulse at 3.862592
    return time, amplitude


def calculate_threshold(time, amplitude, samples_beginning=10000):
    start_noise_x = time[0:samples_beginning]
    start_noise_y = amplitude[0:samples_beginning]
    """ Mean """
    summation = 0
    for value in start_noise_y:
        summation = summation + value
    mean = summation / len(start_noise_y)
    """Variance"""
    square_deviation = 0
    for value in start_noise_y:
        square_deviation = square_deviation + (value - mean) ** 2
    variance = square_deviation / (len(start_noise_y) - 1)
    """Standart deviaten"""
    standard_deviation = math.sqrt(variance)
    """Threshold --> from here on we measure the symbol"""
    threshold = 4 * mean + standard_deviation * 8
    return threshold


def get_beginningidx_endidx(amplitude, threshold):
    """Find point where Preamble starts"""
    communication_start_index = 0
    for y_value in amplitude:
        if y_value >= threshold:
            communication_start_index = amplitude.index(y_value)
            break
    """Let Communication beginn a couple microseconds earlier"""
    communication_start_index = communication_start_index - 8
    """Find point where last Pulse ends"""
    communication_end_index = 0
    for y_value in reversed(amplitude):
        if y_value >= threshold:
            communication_end_index = amplitude.index(y_value)
            break
    """Let Communication end a couple microseconds later"""
    communication_end_index = communication_end_index + 8
    return communication_start_index, communication_end_index


def get_boundaries(amplitude, time, communication_start_index, communication_end_index, interval,
                   number_of_sample_per_symbol):
    """Define boundaries"""
    boundary_time = []
    symbol_lasting = interval * number_of_sample_per_symbol
    needed_boundaries = math.ceil(((len(amplitude[communication_start_index:communication_end_index])) / 100))
    counter = 0
    for x in range(0, needed_boundaries):
        start_point = time[communication_start_index]
        start_point = float(format(start_point + symbol_lasting * counter, '.6f'))
        boundary_time.append(start_point)
        counter = counter + 1
    return boundary_time, needed_boundaries


def analog_to_digital(needed_boundaries, boundary_time, time, amplitude, threshold, number_of_samples_per_symbol):
    """Get the binary data - Analog to digital signal"""
    binary = []
    idx = 0
    for rg in range(0, needed_boundaries):
        if rg >= (needed_boundaries - 1):
            break
        x_axis = boundary_time[idx:(idx + 2)]
        y_axis = amplitude[time.index(x_axis[0]):time.index(x_axis[1])]
        idx = idx + 1
        for cross_over in y_axis:
            if cross_over >= threshold:
                index = y_axis.index(cross_over)
                if index <= (number_of_samples_per_symbol / 2 - 1):
                    binary.append(0)
                    break
                else:
                    binary.append(1)
                    break
    return binary


def bits_to_byte(binary):
    """ Remove Preamble and Take first 4 bits and discard the remaining 3 bits"""
    all_bits_without_preamble = binary[8:]
    length = len(all_bits_without_preamble) / 7
    information_bits = []
    end = int(len(all_bits_without_preamble))
    first_four_bits = []
    for new_symbol in range(0, end, 7):
        information_bits = all_bits_without_preamble[new_symbol:(new_symbol + 7)]
        first_four_bits.append(information_bits[0:4])
    """Concatenate two 4 bit pairs to one byte """
    byte_list = []
    for list in range(0, int(len(first_four_bits)), 2):
        byte_list.append(first_four_bits[list] + first_four_bits[list + 1])
    return byte_list


def byte_to_hex(noisy_data,hamming_data):
    str_data_n = r''
    str_data_h = r''
    for single_byte in noisy_data:
        bin_string = int(''.join(str(x) for x in single_byte))
        decimal_Data = BinaryToDecimalData(bin_string)
        str_data_n = str_data_n + chr(decimal_Data)
    for sgl_byte in hamming_data:
        bin_string_h = int(''.join(str(x) for x in sgl_byte))
        decimal_Data_h = BinaryToDecimalData(bin_string_h)
        str_data_h = str_data_h + chr(decimal_Data_h)
    return print(f"Noisy string: {repr(str_data_n)}\nDenoised with Hamming code string: {str_data_h}")


"""Project 2 Code"""


def rm_preamble_split_by_seven(binary):
    all_bits_without_preamble = binary[8:]
    information_bits = []
    end = int(len(all_bits_without_preamble))
    for new_symbol in range(0, end, 7):
        information_bits.append(all_bits_without_preamble[new_symbol:(new_symbol + 7)])
    information_bits[-1].append(0)
    return information_bits


def possibilities():
    bin = [0, 1]
    matrix_4 = [[w, x, y, z] for w in bin for x in bin for y in bin for z in bin]
    matrix_7 = add_parity_bits(matrix_4)
    return matrix_7


def add_parity_bits(matrix_4):
    matrix_7 = []
    for info_bits in matrix_4:
        c4 = calculate_parity(info_bits, [0, 1, 2])
        c5 = calculate_parity(info_bits, [1, 2, 3])
        c6 = calculate_parity(info_bits, [0, 1, 3])
        parsity_bits = [int(c4), int(c5), int(c6)]
        matrix_7.append(info_bits + parsity_bits)
    return matrix_7


def calculate_parity(list, indices):
    to_string = map(str, list)
    string = ''.join(to_string)
    sub = ''
    for bit in indices:
        sub += string[bit]
    return str(str.count(sub, '1') % 2)


def find_errors(bytes,Generator):
    min_distance_idx = 0
    for idx, point in enumerate(Generator):
        distance = 0
        for i in range(len(point)):
            if point[i] != bytes[i]:
                distance += 1
        if distance <= 1:
            min_distance_idx = idx
    return Generator[min_distance_idx][0:4]


def recreate_8bits(signal):
    first_four_bits = []
    for new_symbol in signal:
        new_symbol = new_symbol[0:4]
        first_four_bits.append(new_symbol)

    """Concatenate two 4 bit pairs to one byte """
    byte_list = []
    for list in range(0, int(len(first_four_bits)), 2):
        byte_list.append(first_four_bits[list] + first_four_bits[list + 1])
    return byte_list


def get_sum(signal, noise):
    noise = ([float(nv) for nv in noise])
    signal = ([float(sig) for sig in signal])
    sum = []
    for i in range(len(noise)):
        sum.append(signal[i] + noise[i])
    return sum


if __name__ == "__main__":
    file = "/Users/calvinsmyk/Desktop/project1/test_r/proj1_testsignal2"
    noise_file = "/Users/calvinsmyk/Desktop/project1/test_r/proj2_noisesignal2"
    interval = 0.000002
    number_of_samples_a_symbol = 100
    Generator = possibilities()
    lines = unpack_txt_file(file)
    noise_values = unpack_txt_file(noise_file)
    signal_noise = get_sum(lines, noise_values)
    time, amplitude = create_plot(signal_noise, interval, False)
    threshold = calculate_threshold(time, amplitude)
    start, end = get_beginningidx_endidx(amplitude, threshold)
    boundary_time, boundaries = get_boundaries(amplitude, time, start, end, interval, number_of_samples_a_symbol)
    bin_data_string = analog_to_digital(boundaries, boundary_time, time, amplitude, threshold,
                                        number_of_samples_a_symbol)
    byte_data = bits_to_byte(bin_data_string)
    bit_data = rm_preamble_split_by_seven(bin_data_string)
    corrected_bytes = []
    for byte in bit_data:
        corrected_bytes.append(find_errors(byte,Generator))
    cs_b = recreate_8bits(corrected_bytes)
    byte_to_hex(byte_data,cs_b)
