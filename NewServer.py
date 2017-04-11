# TCP server program that upper cases text sent from the clientfrom socket import *import sysimport selectimport threadingimport pickle# Default port number server will listen onserverPort = 12001class user():    def __init__(self, alias, socket):        self.alias = alias        self.socket = socket        self.sala_activa = None        self.own_rooms = []        self.guest_rooms = []        self.private_rooms = []    def intro_sala_propia(self, sala):        self.own_rooms.append(sala)    def get_own_rooms(self):        return self.own_rooms    def salas_invitado(self, sala):        self.guest_rooms.append(sala)    def ensala(self, sala):        e = False        if self.own_rooms.count(sala) != 0 or self.guest_rooms.count(sala) != 0 or self.private_rooms.count(sala) !=0:            e = True        return e    def es_propia(self,sala):        i = False        if self.own_rooms.count(sala) != 0:            i = True        return i    def es_privada(self,sala):        i = False        if self.private_rooms.count(sala) != 0:            i = True        return i    def es_guest(self,sala):        i = False        if self.guest_rooms.count(sala) != 0:            i = True        return i    def get_activa(self):        return self.sala_activa    def set_activa(self,parametro):        self.sala_activa = parametro    def get_alias(self):        return self.alias    def get_socket(self):        return self.socket    def guest_room_remove(self,s):        self.guest_rooms.remove(s)    def private_room_remove(self,s):        self.private_rooms.remove(s)    def salir_sala(self,sala):        if self.es_privada(sala):            self.private_rooms.remove(sala)        elif self.es_guest(sala):            self.guest_rooms.remove(sala)    def get_guest_rooms(self):        return self.guest_rooms    def append_private_rooms(self,user):        self.private_rooms.append(user)    def get_private_rooms(self):        return self.private_rooms    def salas_servidor(self,ls):        for s in self.private_rooms:            if ls.count(s) != 0:                ls.remove(s)        for s in self.own_rooms:            if ls.count(s) != 0:                ls.remove(s)        for s in self.guest_rooms:            if ls.count(s) != 0:                ls.remove(s)        return lsclass clase_sala():    def __init__(self, nombre, user):        self.nombre = None        self.propietari = user        self.participant.append(user)    def sala_participant(self, alias):        self.participant.append(alias)    def set_name(self, nombre):        self.nombre = nombreclass server(threading.Thread):    def __init__(self, serverPort, host='localhost'):        self.llista_clients = []        self.llista_alias = []        self.llista_salas = []        # Optional server port number        if (len(sys.argv) > 1):            serverPort = int(sys.argv[1])        # Request IPv4 and TCP communication        self.serverSocket = socket(AF_INET, SOCK_STREAM)        # The welcoming port that clients first use to connect        self.serverSocket.bind(('', serverPort))        # Start listening on the welcoming port        self.serverSocket.listen(10)    def get_user(self,parametro):        user = None        for i in self.llista_clients:            if i.alias == parametro:                user = i        return user    def enviar_mensaje(self, sock, mensaje):        sock.send(mensaje)    def enviar_llista(self, sock, llista):        sock.send(pickle.dumps(llista))    def recibir_mensaje(self, sock):        mensaje = sock.recv(2048)        return mensaje    def lista_usuarios(self, sala):        d = []        for i in self.llista_clients:            if i.ensala(sala):                d.append(i.get_alias())        return d    def lista_sockets_destino(self, sala):        d = []        for i in self.llista_clients:            if i.ensala(sala):                d.append(i.get_socket())        return d    def quitar_todos(self,sala):        for c in self.llista_clients:            self.enviar_llista(c.get_socket(),"alias")            self.enviar_llista(c.get_socket(),"server@!!!>S'ha eliminat la sala " + sala)            for s in c.get_guest_rooms():                if s == sala:                    c.guest_room_remove(s)                    if c.get_activa() == sala:                        c.set_activa(None)            for s in c.get_private_rooms():                if s == sala:                    c.private_room_remove(s)                    if c.get_activa == sala:                        c.set_activa(None)    def msg_user_exit(self,sala,alias):        for c in self.llista_clients:            for s in c.get_guest_rooms():                if s == sala:                     self.enviar_llista(c.get_socket(),"server@!!!>L'usuari " + alias + " ha deixat la sala " + sala )            for s in c.get_own_rooms():                if s == sala:                     self.enviar_llista(c.get_socket(),"server@!!!>L'usuari " + alias + " ha deixat la sala " + sala )    def is_client(self, parameter):        b = False        for i in self.llista_clients:            if i.alias == parameter:                b = True        return b    def alias_repetido(self,alias):        r = False        if self.llista_alias.count(alias) != 0:            r = True        return r    def sala_repetida(self,sala):        r = False        if self.llista_salas.count(sala) != 0:            r = True        return r    def tratar_cliente(self, connectionSocket, addr):        # Asignacion del alias        self.enviar_llista(connectionSocket, self.llista_alias)        alias = self.recibir_mensaje(connectionSocket)        while self.alias_repetido(alias):            self.enviar_llista(connectionSocket, "alias_repetit")            alias = self.recibir_mensaje(connectionSocket)        self.enviar_llista(connectionSocket, "alias_ok")        self.llista_alias.append(alias)        # Creacion del objeto para el usuario        objUser = user(alias, connectionSocket)        # Introduccion en el listado de objetos de tipo usuario        self.llista_clients.append(objUser)        # El thread de cada cliente queda a la espera de recibir los mensajes        respuesta = self.recibir_mensaje(connectionSocket)        if respuesta == "read_to_listen":            self.enviar_llista(connectionSocket, self.llista_salas)        sentence = ""        while sentence != "desconectando cliente":            sentence = self.recibir_mensaje(connectionSocket)            cmd = ""            sala = ""            if len(sentence.split(" ",1)) > 1:                cmd = sentence.split(" ",1)[0]                sala = sentence.split(" ",1)[1]            elif len(sentence.split(" ",1)) == 1:                cmd = sentence.split(" ",1)[0]            # Desconecta del servidor            if cmd == "/bye":                sentence = "desconectando cliente"                print "Usuari " + objUser.get_alias() + " desconectat"                self.enviar_llista(connectionSocket,"bye")            # Crea una sala nueva en caso de no existir            elif cmd == "/cs":                if self.sala_repetida(sala):                    self.enviar_llista(connectionSocket,"server@!!!>Ja existeix una sala amb aquest nom")                else:                    self.enviar_llista(connectionSocket,"ok")                    objUser.set_activa(sala)                    objUser.intro_sala_propia(sala)                    self.llista_salas.append(sala)                    print "S'ha afegit la sala " + sala            elif cmd == "/cp":                #alias = self.recibir_mensaje(connectionSocket)/ds                if self.is_client(sala):                    sala_privada = objUser.get_alias() + "->" + sala                    print "Nova sala privada entre " + objUser.get_alias() + " i " + sala                    objUser.append_private_rooms(sala_privada)                    objUser.set_activa(sala_privada)                    i = self.llista_clients.index(self.get_user(sala))                    self.llista_clients[i].append_private_rooms(sala_privada)                    self.llista_clients[i].set_activa(sala_privada)                    socket_obj = self.llista_clients[i].get_socket()                    self.enviar_llista(socket_obj,"privada")                    self.enviar_llista(socket_obj,sala_privada)                    self.enviar_llista(connectionSocket,"privada")                    self.enviar_llista(connectionSocket,sala_privada)                    self.enviar_llista(socket_obj,"server@!!!>L'usuari " + objUser.get_alias() + " ha iniciat un chat privat amb tu")                    self.enviar_llista(connectionSocket,"ok")                else:                    print "L'usuari " + sala + " no existeix"                    self.enviar_llista(connectionSocket, "server@!!!>L'usuari " + sala + " no existeix")            # Anade el usuario a la sala y la establece como sala activa            elif cmd == "/us":                if sala in self.llista_salas:                    if objUser.es_propia(sala) or objUser.es_guest(sala):                        sent = "server@!!!>Ja et trobes dins de la sala " + sala                        self.enviar_llista(connectionSocket,sent)                    else:                        self.enviar_llista(connectionSocket,"ok")                        objUser.set_activa(sala)                        objUser.salas_invitado(sala)                        room_users = self.lista_usuarios(sala)                        print "L'usuari " + objUser.get_alias() + " s'ha unit a la sala " + sala                elif objUser.es_privada(sala):                    sent = "server@!!!>Ja et trobes dins de la sala privada" + sala                    self.enviar_llista(connectionSocket,sent)                else:                    print "La sala que es vol unir el usuari " + objUser.get_alias() + " no existeix"                    sent = "server@!!!>La sala " + sala + " no existeix"                    self.enviar_llista(connectionSocket, sent)            elif cmd == "/ds":                if objUser.es_propia(sala):                    self.enviar_llista(connectionSocket,"server@!!!>No pots sortir d'una sala on ets propietari. Usa la comanda /es per eliminarla")                elif objUser.es_privada(sala):                    self.enviar_llista(connectionSocket,"server@!!!>No pots sortir d'una sala privada. Usa la comanda /es per eliminarla")                elif sala in objUser.get_guest_rooms() or sala in objUser.get_private_rooms():                    objUser.salir_sala(sala)                    if objUser.get_activa() == sala:                        objUser.set_activa(None)                        self.enviar_llista(connectionSocket,"alias")                    else:                        self.enviar_llista(connectionSocket,"ok")                    self.msg_user_exit(sala,objUser.get_alias())                    print "L'usuari " +  objUser.get_alias() + " ha sortit de la sala " + sala                elif self.llista_salas.count(sala) == 0 and objUser.get_private_rooms().count(sala) == 0:                    print "la sala "  + sala + "no existeix"                    self.enviar_llista(connectionSocket, "Aquesta sala no existeix")                else:                    self.enviar_llista(connectionSocket,"server@!!!>No et trobes dins d'aquesta sala")            elif cmd == "/sa":                if objUser.es_propia(sala) or sala in objUser.get_guest_rooms() or sala in objUser.get_private_rooms():                    objUser.set_activa(sala)                    self.enviar_llista(connectionSocket,"ok")                else:                    self.enviar_llista(connectionSocket,"server@!!!>No et trobes dins d'aquesta sala")            elif cmd == "/es" and sala != "":                if objUser.es_propia(sala) or objUser.es_privada(sala):                    self.quitar_todos(sala)                    if objUser.es_propia(sala):                        self.llista_salas.remove(sala)                    elif objUser.es_privada(sala):                        objUser.private_room_remove(sala)                    if objUser.get_activa() == sala:                        objUser.set_activa(None)                        self.enviar_llista(connectionSocket,"alias")                    else:                        self.enviar_llista(connectionSocket,"ok")                    print "La sala " + sala + " s'ha eliminat"                if self.llista_salas.count(sala) == 0 and objUser.get_private_rooms().count(sala) == 0:                    print "la sala "  + sala + "no existeix"                    self.enviar_llista(connectionSocket, "Aquesta sala no existeix")                else:                    print "L'usuari " + objUser.get_alias() + " no te privilegis per eliminar la sala"                    self.enviar_llista(connectionSocket, "No pots eliminar la sala, no ets el propietari")            elif cmd == "/ls":                self.enviar_llista(connectionSocket,"listas")                lista_privada = objUser.get_private_rooms()                lista_privada.sort()                lista_invitada = objUser.get_guest_rooms()                lista_invitada.sort()                lista_own = objUser.get_own_rooms()                lista_own.sort()                ss = list(self.llista_salas)                salas_servidor = objUser.salas_servidor(ss)                salas_servidor.sort()                todas = []                todas.append(lista_privada)                todas.append(lista_invitada)                todas.append(lista_own)                todas.append(salas_servidor)                self.enviar_llista(connectionSocket,todas)            elif cmd == "/lu":                us = list(self.lista_usuarios(objUser.get_activa()))                us.remove(objUser.get_alias())                us.sort()                self.enviar_llista(connectionSocket,"users")                self.enviar_llista(connectionSocket,us)            elif objUser.get_activa() != None:                #sentence = "Mensaje de " + str(objUser.get_alias() + " desde " + str(objUser.get_activa()) + " :" + str(sentence))                sentence = str(str(objUser.get_activa()) +  "@" +  objUser.get_alias() + ":>" + str(sentence))                print sentence                sockets = self.lista_sockets_destino(objUser.get_activa())                sread, swrite, serror = select.select([], sockets, [], 0)                for sock in swrite:                    if sock != self.serverSocket and sock != connectionSocket:                        self.enviar_llista(sock, sentence)        connectionSocket.close()    def acceptar(self):        while 1:            # Establecimiento de conexion y creacion del socket para cada cliente            # Cada cliente es tratado en un thread a parte            connectionSocket, addr = self.serverSocket.accept()            t = threading.Thread(target=self.tratar_cliente, args=(connectionSocket, addr))            t.start()if __name__ == '__main__':    objServer = server(serverPort)    objServer.acceptar()    print 'The server is ready to receive'