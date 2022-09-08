"""
Simple healthcheck.
"""


from collections import defaultdict
import json
from typing import Dict, Optional, Set, Union


class Checker:
    """
    Checker tracks components, every component can be healthy or unhealthy.
    If all components are healthy, then checker is healthy.
    If any component is not healthy then checker is not healthy.
    """

    def __init__(self) -> None:
        """
        It is encouraged to always use HealthChecking.getChecker for creating instances, 
        you will be able to get particular checker by name anywhere.
        """
        self.__healthy: Set[str] = set()
        self.__not_healthy: Set[str] = set()
        self.__msg: Dict[str, Optional[str]] = defaultdict(str)

    def set_healthy(self, component: str, msg: str = "") -> None:
        """
        Sets component healthy and stores an optional description message
        """
        if component in self.__not_healthy:
            self.__not_healthy.remove(component)
        self.__healthy.add(component)
        self.__msg[component] = msg

    def set_not_healthy(self, component: str, msg: str) -> None:
        """
        Sets component unhealthy and stores mandatory description message
        """
        if component in self.__healthy:
            self.__healthy.remove(component)
        self.__not_healthy.add(component)
        self.__msg[component] = msg

    def get_status(self) -> tuple[bool, str]:
        """
        Returns current health status and description in JSON.
        True - healthy, False - not healthy.
        If any component is not healthy, status is False.
        Description provides information on all components and their stored messages.
        """
        status = len(self.__not_healthy) == 0
        descr = json.dumps({
            "healthy": { component: self.__msg[component] for component in self.__healthy },
            "not healthy": { component: self.__msg[component] for component in self.__not_healthy }
        })
        return status, descr


class HealthChecking:
    """
    Access to instances of HealthChecker
    """
    __map: Dict[Union[str, None], Checker] = defaultdict(Checker)

    @staticmethod
    def getChecker(name: str = None) -> Checker:  
        """
        Returns instance of HealthChecker by name, creates new if it doesn't exist.
        """
        return HealthChecking.__map[name]