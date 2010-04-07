# -*- coding: utf-8 -*-

"""
Implementación de la clase base de los clientes TagFS.
"""

import threading

import Zeroconf
import Pyro.core

from tagfs.common import ZEROCONF_SERVICE_TYPE


class TagFSClient(object):
    """
    Clase base de los clientes de TagFS.
    """
    
    def __init__(self, address):
        """
        Inicializa una instancia de un cliente TagFS.
        
        Solamente debe existir una instancia de esta clase en cada proceso
        ejecutando un cliente TagFS, debido a restricciones relacionadas con 
        las bibliotecas utilizadas para implementar el descubrimiento 
        automático de los servidores TagFS disponibles en la red.
        
        @type address: C{str}
        @param address: Dirección IP de la interfaz de red que se debe utilizar
           para comunicarse con los servidores TagFS.
        """
        self._address = address
        self.init_autodiscovery()
        
    def init_autodiscovery(self):
        """
        Inicializa el descubrimiento automático de los servidores.
        """
        self._servers = {}
        self._servers_mutex = threading.Lock()                
        self.addService = self.server_added
        self.removeService = self.server_removed
        self._zeroconf = Zeroconf.Zeroconf(self._address)
        self._zeroconf_browser = Zeroconf.ServiceBrowser(self._zeroconf, ZEROCONF_SERVICE_TYPE, self)
        
    def terminate(self):
        """
        Termina la ejecución del client TagFS. Despues de ejecutado este método 
        no se debe hacer ningún llamado a los métodos de esta instancia.
        """
        self._zeroconf.close()
        
    def server_added(self, zeroconf, service_type, service_name):
        """
        Método ejecutado cuando se descubre un nuevo servidor TagFS.
        
        @type zeroconf: C{Zeroconf}
        @param zeroconf: Instancia del servidor implementando la comunicación
            mediante Zeroconf Multicast DNS Service Discovery.
        
        @type service_type: C{str}
        @param service_type: Nombre completamente calificado del tipo
            de servicio que fue descubierto.
        
        @type service_name: C{str}
        @param service_name: Nombre completamente calificado del nombre 
            del servicio que fue descubierto.
        """
        with self._servers_mutex:
            pyro_uri = service_name[:-(len(service_type) + 1)]
            pyro_proxy = Pyro.core.getProxyForURI(pyro_uri)
            self._servers[pyro_uri] = pyro_proxy
        
    def server_removed(self, zeroconf, service_type, service_name):
        """
        Método ejecutado cuando un servidor TagFS deja de estar disponible.
        
        @type zeroconf: C{Zeroconf}
        @param zeroconf: Instancia del servidor implementando la comunicación
            mediante Zeroconf Multicast DNS Service Discovery.
            
        @type service_type: C{str}
        @param service_type: Nombre completamente calificado del tipo
            de servicio que fue descubierto.
        
        @type service_name: C{str}
        @param service_name: Nombre completamente calificado del nombre 
            del servicio que fue descubierto.                    
        """
        with self._servers_mutex:
            pyro_uri = service_name[:-(len(service_type) + 1)]
            del self._servers[pyro_uri]
