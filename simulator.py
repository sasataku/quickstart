#!/usr/bin/env python3

import binascii
import io
import socket
import sys
from struct import unpack_from
from struct import pack_into
from threading import Thread
from time import sleep

def send_tm(simulator, tm):
    tm_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    simulator.tm_counter = 1
    apid = 100
    seq = 0
    data_length = 117
    header_length = 6
    tlm_data = bytearray(data_length)
    header = bytearray(header_length)

    while True:
        # Telemetry Data
        pack_into(">f2I22f17B", tlm_data, 0,
                  tm.EpochUSNO,
                  tm.OrbitNumberCumulative,
                  tm.ElapsedSeconds,
                  tm.A,
                  tm.Height,
                  tm.Position_X,
                  tm.Position_y,
                  tm.Position_z,
                  tm.Velocity_x,
                  tm.Velocity_y,
                  tm.Velocity_z,
                  tm.Latitude,
                  tm.Longitude,
                  tm.Battery1_Voltage,
                  tm.Battery2_Voltage,
                  tm.Battery1_Temp,
                  tm.Battery2_Temp,
                  tm.Magnetometer_x,
                  tm.Magnetometer_y,
                  tm.Magnetometer_z,
                  tm.Sunsensor,
                  tm.Gyro_x,
                  tm.Gyro_y,
                  tm.Gyro_z,
                  tm.Detector_Temp,
                  tm.Shadow,
                  tm.Contact_Golbasi_GS,
                  tm.Contact_Svalbard,
                  tm.Payload_Status,
                  tm.Payload_Error_Flag,
                  tm.ADCS_Error_Flag,
                  tm.CDHS_Error_Flag,
                  tm.COMMS_Error_Flag,
                  tm.EPS_Error_Flag,
                  tm.COMMS_Status,
                  tm.CDHS_Status,
                  tm.Mode_Night,
                  tm.Mode_Day,
                  tm.Mode_Payload,
                  tm.Mode_XBand,
                  tm.Mode_SBand,
                  tm.Mode_Safe)

        # CCSDS Primary Header
        seq += 1
        length = data_length + header_length - 7
        pack_into(">HHH", header, 0, apid, seq, length)

        packet = header + tlm_data

        tm_socket.sendto(packet, ('127.0.0.1', 10015))
        simulator.tm_counter += 1

        sleep(1)


def receive_tc(simulator):
    tc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tc_socket.bind(('127.0.0.1', 10025))
    while True:
        data, _ = tc_socket.recvfrom(4096)
        simulator.last_tc = data
        simulator.tc_counter += 1


class SpacecraftTelemetry:

    def __init__(self):
        self.EpochUSNO = 57388.9
        self.OrbitNumberCumulative = 1
        self.ElapsedSeconds = 2
        self.A = 7186.999
        self.Height = 808.14453
        self.Position_X = 2443.6577
        self.Position_y = 6758.0093
        self.Position_z = 22.090302
        self.Velocity_x = 1.0445765
        self.Velocity_y = -0.4018111
        self.Velocity_z = 7.3634105
        self.Latitude = 0.2048504
        self.Longitude = 330.22125
        self.Battery1_Voltage = 3.3
        self.Battery2_Voltage = 15.0
        self.Battery1_Temp = 25.0
        self.Battery2_Temp = 24.8
        self.Magnetometer_x = 1204.2902
        self.Magnetometer_y = 1505.3628
        self.Magnetometer_z = 2599.9917
        self.Sunsensor = 1.2999668
        self.Gyro_x = 6.10262
        self.Gyro_y = 4.8820963
        self.Gyro_z = 5.695779
        self.Detector_Temp = 0
        self.Shadow = 0
        self.Contact_Golbasi_GS = 0
        self.Contact_Svalbard = 0
        self.Payload_Status = 0
        self.Payload_Error_Flag = 0
        self.ADCS_Error_Flag = 0
        self.CDHS_Error_Flag = 0
        self.COMMS_Error_Flag = 0
        self.EPS_Error_Flag = 0
        self.COMMS_Status = 0
        self.CDHS_Status = 0
        self.Mode_Night = 0
        self.Mode_Day = 0
        self.Mode_Payload = 0
        self.Mode_XBand = 0
        self.Mode_SBand = 0
        self.Mode_Safe = 1


class Simulator():

    def __init__(self):
        self.tm_counter = 0
        self.tc_counter = 0
        self.tm_thread = None
        self.tc_thread = None
        self.last_tc = None

    def start(self, tm):
        self.tm_thread = Thread(target=send_tm, args=(self,tm))
        self.tm_thread.daemon = True
        self.tm_thread.start()
        self.tc_thread = Thread(target=receive_tc, args=(self,))
        self.tc_thread.daemon = True
        self.tc_thread.start()

    def print_status(self):
        cmdhex = None
        if self.last_tc:
            cmdhex = binascii.hexlify(self.last_tc).decode('ascii')
        return 'Sent: {} packets. Received: {} commands. Last command: {}'.format(
                         self.tm_counter, self.tc_counter, cmdhex)


if __name__ == '__main__':
    tm = SpacecraftTelemetry()
    simulator = Simulator()
    simulator.start(tm)

    try:
        prev_status = None
        while True:
            status = simulator.print_status()
            if status != prev_status:
                sys.stdout.write('\r')
                sys.stdout.write(status)
                sys.stdout.flush()
                prev_status = status
            sleep(0.5)
    except KeyboardInterrupt:
        sys.stdout.write('\n')
        sys.stdout.flush()
