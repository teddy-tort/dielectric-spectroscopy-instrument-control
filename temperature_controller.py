from communication.devices.lakeshore import Client as Lakeshore
import numpy as np
import time
import os


def run_command_line():
    ls = Lakeshore(331)

    setpoint = None

    """Open Startup text"""
    with open(os.path.join("text", "temperature control startup.txt"), "r") as startup_file:
        print(startup_file.read())

    run = True
    while run:
        commands = input("LS>").upper().split(";")   # wait for command

        for command_str in commands:
            command_str = command_str.strip(' ')
            # print(f"Execute command: {command_str}")
            command = command_str.split(' ')

            if command[0] == "QUIT" or command[0] == "EXIT":
                run = False
                print("Exiting...")
            elif command[0] == "HELP":
                with open(os.path.join("text", "temperature control help.txt"), "r") as help_file:
                    print(help_file.read())

            elif command[0] == "PID?":
                print("P={}; I={}; D={}\n".format(*ls.read_pid()))
            elif command[0] == "PID":
                if len(command) < 4:
                    print('No PID values given; please type "PID X, Y, Z" to set P=X, I=Y, D=Z.\n')
                else:
                    try:
                        p = float(command[1].strip(","))
                    except ValueError:
                        print("Error: Invalid P given.\n")
                    try:
                        i = float(command[2].strip(","))
                    except ValueError:
                        print("Error: Invalid I given.\n")
                    try:
                        d = float(command[3].strip(","))
                    except ValueError:
                        print("Error: Invalid D given.\n")
                    try:
                        ls.set_pid(p, i, d)
                        print("Set P=X, I=Y, D=Z.\n")
                    except NameError:
                        pass

            elif command[0] == "RAMP?":
                print("{} K/min".format(ls.read_ramp_speed()))
            elif command[0] == "RAMP":
                if len(command) == 1:
                    print('No ramp-rate given; please type "RAMP X" to set the ramp-rate to X K/min.\n')
                else:
                    try:
                        ls.set_ramp_speed(float(command[1]))
                        print("Setting ramp-rate to {} K/min".format(command[1]))
                    except ValueError:
                        print("Error: Invalid ramp-rate given.\n")

            elif command[0] == "SP?":
                if setpoint is not None:
                    print("{} K\n".format(setpoint))
                else:
                    print("{} K\n".format(ls.read_setpoint()))
            elif command[0] == "SP":
                if len(command) == 1:
                    print('No temperature given; please type "SP X" to set the set-point to X Kelvin.\n')
                else:
                    try:
                        setpoint = float(command[1])
                        ls.set_setpoint(setpoint)
                        print("Set-point ramping to {} K\n".format(setpoint))
                    except ValueError:
                        print("Error: Invalid set-point given.\n")

            elif command[0] == "RAW":
                if len(command) == 1:
                    print('No message given; please type "RAW [message]" to send [message] to the Lakeshore.\n')
                else:
                    raw_message = " ".join(command[1:]).upper()
                    message_back = ls.write(raw_message)
                    print('Sent "{}" to the LakeShore.\n'.format(raw_message))
                    print('Response: {}\n'.format(message_back))
            
            elif command[0] == "WAIT":
                time.sleep(float(command[1]))

            else:
                print('Invalid command, try "help" for more options.\n')


if __name__ == "__main__":
    run_command_line()
