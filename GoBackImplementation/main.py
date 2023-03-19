def get_data():
    with open("ACK_GOOD", 'r') as acknowledgements:
        acks = acknowledgements.read().splitlines()

    with open("DATA_GOOD", 'r') as d:
        datas = d.read().splitlines()
    return datas,acks

def Go_Back_N(d,a,ws):
    total_time = len(d)
    pointing_idx_s = 0
    pointing_idx_r = 1
    window_size = [0,ws]
    receiver_receiving_frame = []
    sender_receiving_ack = []
    print(f'time 0: sender got ACK0, window {window_size}')
    for time in range(0,total_time):
        value_r, receiver_receiving_frame = receiver(a,pointing_idx_r,receiver_receiving_frame,time,d)
        if value_r:
            sender_receiving_ack.append([time+3,pointing_idx_r,time])
            pointing_idx_r = pointing_idx_r + 1
        value_s,sender_receiving_ack = sender_read(d,pointing_idx_s,sender_receiving_ack,time,a,window_size)
        if value_s:
            window_size = update_window(window_size)

        sender_send(d,pointing_idx_s,sender_receiving_ack,time,a,window_size)
        receiver_receiving_frame.append([time+4,pointing_idx_s,time])
        pointing_idx_s = pointing_idx_s+1

        if timeout_watcher_s(sender_receiving_ack,time):
            pointing_idx_r = window_size[0]
        if timeout_watcher_r(receiver_receiving_frame, time):
            pointing_idx_r = window_size[0]
        time = time+1

def sender_send(d,idx,receiving_list,time,acks,window_size):
    datapoint = int(d[idx])
    print(f'time {time}: sender window {window_size}, transmitting new frame {idx}, {transmission_status(datapoint)}')


def sender_read(d,idx,receiving_list,time,acks,window_size):
    for indice,awaiting in enumerate(receiving_list):
        if awaiting[0] == time:
            if int(acks[awaiting[1]]) ==1:
                print(f'time {time}: sender got ACK{awaiting[1]}, window {[window_size[0]+1, window_size[1]+1]}')
                receiving_list.remove(awaiting)
                return True, receiving_list
    else:
        return False,receiving_list


def transmission_status(bin):
    if bin == 1:
        return 'good transmission'
    elif bin == 0:
        return 'bad transmission'


def receiver(a,idx,information,time,d):
    for awaiting in information:
        if awaiting[0] == time:
            if int(d[awaiting[1]]) == 1:
                print(f'time {time}: receiver got frame {awaiting[1]}, transmitting ACK{idx}, {transmission_status(int(a[idx]))}')
                information.remove(awaiting)
                return True, information
    else:
        return False,information


def update_window(window_size):
    return [window_size[0]+1, window_size[1]+1]


def timeout_watcher_r(watcher_receiver,time):
    for check_lost_data in watcher_receiver:
        if check_lost_data[2]+7 <= time:
            print("Lost Data --> Retransmitting Window!")
            return True

def timeout_watcher_s(watcher_sender,time):
    for check_lost_data in watcher_sender:
        if check_lost_data[2]+7 <= time:
            print("Lost ACK --> Retransmitting Window!")
            return True



if __name__ == "__main__":
    """NOT THE WOKRING FILE USE goBACKNARQ.py"""
    #d,a = get_data()
    #Go_Back_N(d,a,6)

