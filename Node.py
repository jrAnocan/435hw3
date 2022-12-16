import socket
import sys
import time
import numpy as np
import threading
import pickle

def updateTable(node_distance_vector, data_arr, current_port):

    for i in range(len(node_distance_vector)):
        for j in range(len(node_distance_vector)):

            if (node_distance_vector[current_port-3000][i] > node_distance_vector[current_port-3000][j]+data_arr[j][i] and data_arr[current_port-3000][j]+data_arr[j][i]!=0):
                #print("++++")
                node_distance_vector[current_port-3000][i] = node_distance_vector[current_port -
                                                                                    3000][j]+data_arr[j][i]

    return node_distance_vector


def printResult(current_node, node_distance_vector):
    for i in range(len(node_distance_vector)):
        print(str(current_node) + " -"+str(3000+i)+" | "+str(int(node_distance_vector[current_node-3000][i])))


def listenMessage(node_distance_vector, current_port, neighbours):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        server_address = ('localhost', current_port)
        sock.bind(server_address)

        sock.listen()
        while True:
            
            connection, client_address = sock.accept()
            try:

                
                while True:
                    data = connection.recv(4096)
                    if data:
                        data_arr = pickle.loads(data)
                        
                        node_distance_vector = updateTable(node_distance_vector,
                                    data_arr, current_port)

                        continue
                    else:
                        break

            finally:
               
                continue
    except:
        # print("Exiting"+str(current_port))
       
        exit(0)


def sendMessage(node_distance_vector, current_port, dest_port, neighbours):

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = ('localhost', dest_port)

        #print("Current port " + str(current_port)+" is connecting to "+str(dest_port))

        while True:
            try:
                sock.connect(server_address)
                break
            except:
                continue
        #print("Current port " + str(current_port)+" is CONNECTED to "+str(dest_port))

        try:

            
            message = pickle.dumps(node_distance_vector)
            #print("Sending message from " + str(current_port)+" to "+str(dest_port))
            
            sock.sendall(message)
            
            #print("Message sent from " + str(current_port)+" to "+str(dest_port))

        finally:
            
            sock.close()

    except:
        exit(0)


def communicate(node_distance_vector, current_port, neighbours):
    #print("In " + str(current_port))

    x = threading.Thread(target=listenMessage, args=(
        node_distance_vector, current_port, neighbours))

    x.start()

    for i in range(len(node_distance_vector)+100):

        for el in neighbours:

            y = threading.Thread(target=sendMessage, args=(
                node_distance_vector, current_port, el, neighbours))
            y.start()
            y.join()
    x.join()

def updateInitial(node_distance_vector, current_port, Lines):
    for el in Lines[1:]:
        node_distance_vector[current_port -
                             3000][int(el[0:4])-3000] = int(el[5:len(el)])
    for i in range(len(node_distance_vector)):
        if(node_distance_vector[current_port-3000][i]==0 and (current_port-3000)!=i):
            node_distance_vector[current_port-3000][i] = 999999999


if __name__ == "__main__":
    args = sys.argv

    current_port = int(args[1])
    fileName = str(current_port) + ".costs"

    file_temp = open(fileName, 'r')
    Lines = file_temp.readlines()

    node_amount = int(Lines[0])
    node_distance_vector = np.zeros((node_amount, node_amount))

    neighbours = []

    for el in Lines[1:]:

        neighbours.append(int(el[0:4]))

    updateInitial(node_distance_vector, current_port, Lines)
    
    communicate(node_distance_vector, current_port, neighbours)

    printResult(current_port,node_distance_vector)
