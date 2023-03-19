def get_data():
    with open("ACK_GOOD_2", 'r') as acknowledgements:
        acks = acknowledgements.read().strip().splitlines()

    with open("DATA_GOOD_2", 'r') as d:
        datas = d.read().strip().splitlines()
    return datas,acks


def goBackNARQ(data,acknowlegements,delay,window_size,timeout):
    sequ_ack = 0
    sequ_frame = 0
    sender_frame = 0
    ack_frame = 0
    sender_window = [0, window_size - 1]
    good_transmission_sender = []
    bad_transmission_sender = []
    good_transmission_receiver = []
    bad_transmission_receiver = []
    discard_timings = []
    temp_frame = []
    timeout_timer = 10000
    timeout_state_window = 0
    actual_nr_frames = 0
    for timer in range(0,1000):
        if timer == 69:
            print("")
        if timer == 0:
            print(f'time {timer}: sender got ACK0, window {sender_window}')

        for tuple_gr in good_transmission_receiver:
            if timer == tuple_gr[0]:
                sender_window = [tuple_gr[1],tuple_gr[1]+6]
                print(f'time {timer}: sender got ACK {tuple_gr[1]}, window {sender_window}')
                good_transmission_receiver.remove(tuple_gr)

        for tuple_gs in good_transmission_sender:
            if timer == tuple_gs[0]:
                if int(acknowlegements[ack_frame]) == 1:
                    if any(timer in check for check in discard_timings if isinstance(check,list)):
                        sequ_ack = sequ_ack
                    elif len(discard_timings) != 0 and timer <= max(discard_timings)[0]:
                        sequ_ack = sequ_ack
                    elif timer <= timeout_timer:
                        sequ_ack = sequ_ack +1
                    print(f'time {timer}: receiver got frame {tuple_gs[1]}, transmitting ACK{sequ_ack}, good transmission')
                    good_transmission_receiver.append([timer+3,sequ_ack])
                    good_transmission_sender.remove(tuple_gs)
                    ack_frame = ack_frame +1
                    actual_nr_frames -=1
                elif int(acknowlegements[ack_frame]) == 0:
                    if any(timer in check for check in discard_timings if isinstance(check,list)):
                        sequ_ack = sequ_ack
                    elif  len(discard_timings) != 0 and timer <= max(discard_timings)[0]:
                        sequ_ack = sequ_ack
                    elif timer <= timeout_timer:
                        sequ_ack = sequ_ack +1
                    print(f'time {timer}: receiver got frame {tuple_gs[1]}, transmitting ACK{sequ_ack}, bad transmission')
                    bad_transmission_receiver.append([timer+delay+1,sequ_ack,tuple_gs[1]])
                    ack_frame = ack_frame+1
                    actual_nr_frames -= 1

        for tuple_bs in bad_transmission_sender:
            if timer == tuple_bs:
                sequ_frame = sender_window[0]
                timeout_timer = 10000
                timeout_state_window = 0
                for frame in good_transmission_sender:
                    if frame[1] in range(sender_window[0],sender_window[1]+1):
                        discard_timings.append(frame)
                bad_transmission_sender.clear()
                bad_transmission_receiver.clear()
                #bad_transmission_sender.remove(tuple_bs)

        for tuple_br in bad_transmission_receiver:
            if timer == tuple_br[0] and sender_window[0] <= tuple_br[2] < sequ_frame:
                temp_frame.append(tuple_br)
                #timeout_timer= 10000
                bad_transmission_receiver.remove(tuple_br)
        if sequ_frame in range(sender_window[0],sender_window[1]+1) or len(temp_frame)>=1:
            if int(data[sender_frame]) == 1:
                if len(temp_frame) >= 1:
                    print(f'time {timer}: sender window {sender_window}, transmitting frame {temp_frame[0][2]}, good transmission')
                    good_transmission_sender.append([timer + 4, temp_frame[0][2]])
                    temp_frame.remove(temp_frame[0])
                    sender_frame = sender_frame + 1
                    actual_nr_frames +=1
                else:
                    print(f'time {timer}: sender window {sender_window}, transmitting frame {sequ_frame}, good transmission')
                    good_transmission_sender.append([timer+4,sequ_frame])
                    sequ_frame = sequ_frame+1
                    sender_frame = sender_frame+1
                    actual_nr_frames += 1
            elif int(data[sender_frame]) == 0:
                if len(temp_frame) >= 1:
                    print(f'time {timer}: sender window {sender_window}, transmitting frame {temp_frame[0][2]}, good transmission')
                    bad_transmission_sender.append(timer+(timeout+1))
                    if timeout_state_window == 0:
                        timeout_timer = timer+delay
                        timeout_state_window = 1
                    sender_frame = sender_frame+1
                    actual_nr_frames += 1
                else:
                    print(f'time {timer}: sender window {sender_window}, transmitting frame {sequ_frame}, bad transmission')
                    bad_transmission_sender.append(timer+(timeout+1))
                    sequ_frame = sequ_frame+1
                    if timeout_state_window == 0:
                        timeout_timer = timer+delay
                        timeout_state_window = 1
                    sender_frame = sender_frame+1
                    actual_nr_frames += 1


if __name__ == "__main__":
    d,a = get_data()
    goBackNARQ(d,a,3,7,7)