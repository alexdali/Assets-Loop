import re
import subprocess
from time import sleep

import requests
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller


class Tor:
    """
    This class  sets up a Tor proxy on a running Tor host and initializes a
    request session with the proxy.

    Attributes:
        TOR_HOSTNAME (str): Hostname docker container Tor.
    """
    TOR_HOSTNAME: str = "tor_proxy"

    def __init__(self) -> None:
        """
        Initializes the Tor class by setting the container IP address and
        creating a new Tor session.
        """
        self.container_ip: str = self.__get_tor_ip()
        self.session: requests.sessions.Session = self.__get_tor_session()

    def __get_tor_session(self) -> requests.sessions.Session:
        """
        Set up a proxy for http and https on the running Tor host: port 9050
        and initialize the request session.
        """
        with requests.session() as session:
            session.proxies = {'http': f'socks5h://{self.TOR_HOSTNAME}:9050',
                               'https': f'socks5h://{self.TOR_HOSTNAME}:9050'}
            session.headers = {'User-Agent': UserAgent().chrome}
            return session

    def __get_tor_ip(self) -> str:
        """
        Retrieves the IP address of the running Tor host.
        """
        cmd = f'ping -c 1 {self.TOR_HOSTNAME}'
        output = subprocess.check_output(cmd, shell=True).decode().strip()
        return re.findall(r'\(.*?\)', output)[0][1:-1]

    def renew_connection(self) -> None:
        """
        Renews the connection with the running Tor host by sending a signal to
        the Tor control port and creating a new Tor session with a new IP
        address.
        """
        with Controller.from_port(address=self.container_ip) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            sleep(controller.get_newnym_wait())
            self.session = self.__get_tor_session()
