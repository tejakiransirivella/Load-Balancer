import json
import multiprocessing
import pickle
import random
import subprocess
import signal
import socket
import threading


def shutdown_components(cleanup_signal, processes: []):
    if cleanup_signal == signal.SIGINT:
        for process in processes:
            process.terminate()


def run_components(args: []):
    """
    Runs the scripts for clients, servers, and load balancer
    :param script: .py file corresponding to the components
    :param args: command-line args for the component to be executed
    :return: None
    """
    script = args[0]
    try:
        subprocess.run(["python", script] + args[1:], check=True)

        if len(args) > 1:
            print(f"started: {script.split('.')[0]} id-{args[1]} port-{args[2]}")
        else:
            print(f"started load-balancer port-{args[1]}")
    except subprocess.CalledProcessError as e:
        print(f"error occurred while executing {script.split('.')[1]}")


def handle_lb_requests(port: int, server_processes: [], server_id_pid: {}, configurations):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', int(port)))
    server_socket.listen()
    print("Controller: listening to the LB")
    while True:
        lb_socket, lb_address = server_socket.accept()
        lb_request = lb_socket.recv(65535)
        deserialize_req = pickle.loads(lb_request)

        if deserialize_req.type == 0:
            server_id, process = add_server(configurations)
            process.start()
            server_id_pid[server_id] = process.pid
            server_processes[process.pid] = process
        else:
            server_processes[server_id_pid[deserialize_req.server_id]].terminate()


def add_server(configurations):
    server_id = random.randint(int(configurations["server"]["start_id"]), int(configurations["server"]["start_id"]) + 1000)
    port = random.randint(int(configurations["server"]["port_range_start"]), int(configurations["server"]["port_range_end"]))
    process = multiprocessing.Process(target=run_components,
                                      args=(["server.py", str(server_id), str(port), configurations["load_balancer"]["server_side_port"],
                                            configurations["server"]["queue_update_interval"]],))
    return server_id, process


def add_client(configurations):
    client_id = random.randint(int(configurations["client"]["start_id"]), int(configurations["client"]["start_id"]) + 1000)
    port = random.randint(int(configurations["client"]["port_range_start"]), int(configurations["client"]["port_range_end"]))
    process = multiprocessing.Process(target=run_components,
                                      args=(["client.py", str(client_id), str(port), configurations["load_balancer"]["client_side_port"]],))

    return process


def main():
    f = open("config.json", 'r')

    configurations = json.load(f)

    server_processes = {}
    client_processes = []

    server_id_pid = {}

    controller_thread = threading.Thread(target=handle_lb_requests, args=(configurations["controller"]["port"], server_processes, server_id_pid, configurations,))
    controller_thread.start()


    # running load balancer
    load_bal_process = multiprocessing.Process(target=run_components,
                                               args=(["loadbalancer.py", configurations["load_balancer"]["client_side_port"],
                                                     configurations["load_balancer"]["server_side_port"],
                                                     configurations["controller"]["port"],
                                                     configurations["load_balancer"]["max_queue_size"]],))
    load_bal_process.start()

    # running servers
    for i in range(int(configurations["server"]["count"])):
        # server_id = random.randint(configurations["server"]["start_id"], configurations["server"]["start_id"] + 1000)
        # port = random.randint(configurations["server"]["port_range_start"], configurations["server"]["port_range_end"])
        # process = multiprocessing.Process(target=run_components,
        #                                   args=(server_id, port, configurations["load_balancer"]["server_side_port"],
        #                                         configurations["server"]["queue_update_interval"],))
        server_id, process = add_server(configurations)
        process.start()
        server_id_pid[server_id] = process.pid
        server_processes[process.pid] = process

    # running clients
    for i in range(int(configurations["client"]["count"])):
        # client_id = random.randint(configurations["client"]["start_id"], configurations["client"]["start_id"] + 1000)
        # port = random.randint(configurations["client"]["port_range_start"], configurations["client"]["port_range_end"])
        # process = multiprocessing.Process(target=run_components,
        #                                   args=(client_id, port, configurations["load_balancer"]["client_side_port"],))
        process = add_client(configurations)
        process.start()
        client_processes.append(process)

    # register the cleanup function for Ctrl+C
    signal.signal(signal.SIGINT, shutdown_components)


    handle_lb_requests(configurations["controller"]["port"], server_processes, server_id_pid, configurations)


if __name__ == '__main__':
    main()
