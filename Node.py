import socket
import sys
import time
import numpy as np
import threading
import pickle

done = threading.Event()

def updateTable(node_distance_vector, data_arr, current_port):
    update = False
    for i in range(len(node_distance_vector)):
        for j in range(len(node_distance_vector)):

            if (node_distance_vector[current_port-3000][i] > node_distance_vector[current_port-3000][j]+data_arr[j][i] and data_arr[current_port-3000][j]+data_arr[j][i]!=0):
                #print("++++")
                node_distance_vector[current_port-3000][i] = node_distance_vector[current_port -
                                                                                    3000][j]+data_arr[j][i]
                update = True
    return update

    

def printResult(current_node, node_distance_vector):
    for i in range(len(node_distance_vector)):
        print(str(current_node) + " -"+str(3000+i)+" | "+str(int(node_distance_vector[current_node-3000][i])))


def listenMessage(node_distance_vector, current_port, updated):
    global done

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
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

                        updated = updateTable(node_distance_vector,
                                    data_arr, current_port)

                        if(updated):
                            done.set()
                            sock.settimeout(5)
                            
                        else:
                            done.clear()
                            
                        
                        
                        continue
                    else:
                        break

            finally:
               
                continue
    except:
        # print("Exiting"+str(current_port))
        sock.close()
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
                sock.close()
                return
        #print("Current port " + str(current_port)+" is CONNECTED to "+str(dest_port))

        try:

            
            message = pickle.dumps(node_distance_vector)
            #print("Sending message from " + str(current_port)+" to "+str(dest_port))
            
            sock.sendall(message)
            
            #print("Message sent from " + str(current_port)+" to "+str(dest_port))

        finally:
            
            sock.close()
            return

    except:
        done.set()
        sock.close()
        return


def communicate(node_distance_vector, current_port, neighbours):
    #print("In " + str(current_port))

    global done
    done.set()
    updated = False
    x = threading.Thread(target=listenMessage, args=(
        node_distance_vector, current_port, updated))
    x.daemon = True

    x.start()
    now = time.time()
   
    while(time.time()<now+5):
        
        for el in neighbours:
            if(done.is_set()):
                now = time.time()
                done.clear()
            sendMessage(
                node_distance_vector, current_port, el, neighbours)
        done.wait(0.01)
        
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
    
    #print(time.asctime( time.localtime(time.time()) ))
    communicate(node_distance_vector, current_port, neighbours)
    time.sleep(0.01*(current_port-3000))
    print("")
    printResult(current_port,node_distance_vector)
    print("")
    print("")
    #print(time.asctime( time.localtime(time.time()) ))

   
