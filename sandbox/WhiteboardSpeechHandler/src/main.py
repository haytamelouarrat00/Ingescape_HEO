import signal

import getopt

import time

from pathlib import Path

import ingescape as igs

import sys



from WhiteboardSpeechHandler import WhiteboardSpeechAgent



port = 5670

agent_name = "whiteboard_speech"

device = "WiFi 2"

verbose = False

is_interrupted = False



short_flag = "hvip:d:n:"

long_flag = ["help", "verbose", "interactive_loop", "port=", "device=", "name="]





def print_usage():

    print("Usage example: ", agent_name, " --verbose --port 5670 --device device_name")

    print("\nthese parameters have default value (indicated here above):")

    print("--verbose : enable verbose mode in the application (default is disabled)")

    print("--port port_number : port used for autodiscovery between agents (default: 31520)")

    print("--device device_name : name of the network device to be used (useful if several devices available)")

    print("--name agent_name : published name for this agent (default: ", agent_name, ")")

    print("--interactive_loop : enables interactive loop to pass commands in CLI (default: false)")





def print_usage_help():

    print("Available commands in the terminal:")

    print("    /quit : quits the agent")

    print("    /help : displays this message")

    print("    /start : starts voice recognition")

    print("    /stop : stops voice recognition")





def signal_handler(signal_received, frame):

    global is_interrupted

    print("\n", signal.strsignal(signal_received), sep="")

    is_interrupted = True





# Input callbacks

def start_listening_callback(io_type, name, value_type, value, my_data):

    agent = my_data

    assert isinstance(agent, WhiteboardSpeechAgent)

    agent.start_listening()





def stop_listening_callback(io_type, name, value_type, value, my_data):

    agent = my_data

    assert isinstance(agent, WhiteboardSpeechAgent)

    agent.stop_listening()





def command_text_callback(io_type, name, value_type, value, my_data):

    agent = my_data

    assert isinstance(agent, WhiteboardSpeechAgent)

    agent._handle_speech(value)





if __name__ == "__main__":

    # catch SIGINT handler before starting agent

    signal.signal(signal.SIGINT, signal_handler)

    interactive_loop = False



    try:

        opts, args = getopt.getopt(sys.argv[1:], short_flag, long_flag)

    except getopt.GetoptError as err:

        igs.error(err)

        sys.exit(2)

    for o, a in opts:

        if o == "-h" or o == "--help":

            print_usage()

            exit(0)

        elif o == "-v" or o == "--verbose":

            verbose = True

        elif o == "-i" or o == "--interactive_loop":

            interactive_loop = True

        elif o == "-p" or o == "--port":

            port = int(a)

        elif o == "-d" or o == "--device":

            device = a

        elif o == "-n" or o == "--name":

            agent_name = a

        else:

            assert False, "unhandled option"



    # Initialize Ingescape

    igs.agent_set_name(agent_name)

    igs.log_set_console(verbose)

    igs.log_set_file(True, None)

    igs.log_set_stream(verbose)

    igs.set_command_line(sys.executable + " " + " ".join(sys.argv))



    # Device selection

    if device is None:

        list_devices = igs.net_devices_list()

        list_addresses = igs.net_addresses_list()

        if len(list_devices) == 1:

            device = list_devices[0].decode('utf-8')

            igs.info("using %s as default network device (this is the only one available)" % str(device))

        elif len(list_devices) == 2 and (list_addresses[0] == "127.0.0.1" or list_addresses[1] == "127.0.0.1"):

            if list_addresses[0] == "127.0.0.1":

                device = list_devices[1].decode('utf-8')

            else:

                device = list_devices[0].decode('utf-8')

            print("using %s as default network device (this is the only one available that is not the loopback)" % str(

                device))

        else:

            if len(list_devices) == 0:

                igs.error("No network device found: aborting.")

                exit(1)

            else:

                igs.error("No network device passed as command line parameter and several are available.")

                print("Please use one of these network devices:")

                for device in list_devices:

                    print("    ", device)

                print_usage()

                exit(1)


    agent = WhiteboardSpeechAgent()


    igs.observe_input("start_listening", start_listening_callback, agent)

    igs.observe_input("stop_listening", stop_listening_callback, agent)

    igs.observe_input("command_text", command_text_callback, agent)




    igs.start_with_device(device, port)

    signal.signal(signal.SIGINT, signal_handler)



    if interactive_loop:

        print_usage_help()

        while True:

            command = input()

            if command == "/quit":

                break

            elif command == "/help":

                print_usage_help()

            elif command == "/start":

                agent.start_listening()

            elif command == "/stop":

                agent.stop_listening()

    else:



        agent.start_listening()

        while (not is_interrupted) and igs.is_started():

            time.sleep(0.1)



    # Cleanup

    agent.cleanup()

    if igs.is_started():

        igs.stop()