"""
Simple healthcheck.
"""


from collections import defaultdict
import json
from typing import Dict, Optional, Set


class BaseHealthCheck():
    """
    Health check core.
    Application has 'components', at least one, you can call it 'main'.
    Every component can be healthy or unhealthy.
    If all components are healthy, then app is healthy.
    If any component is not healthy the app is not healthy.
    """

    def __init__(self) -> None:
        self.__healthy: Set[str] = set()
        self.__not_healthy: Set[str] = set()
        self.__msg: Dict[str, Optional[str]] = defaultdict(str)

    def set_healthy(self, component: str, msg: str = None) -> None:
        """
        Sets component healthy and leaves an optional description message
        """
        if component in self.__not_healthy:
            self.__not_healthy.remove(component)
        self.__healthy.add(component)
        self.__msg[component] = msg

    def set_not_healthy(self, component: str, msg: str) -> None:
        """
        Sets component unhealthy and adds mandatory description message
        """
        if component in self.__healthy:
            self.__healthy.remove(component)
        self.__not_healthy.add(component)
        self.__msg[component] = msg

    def get_status(self) -> tuple[bool, str]:
        """
        Returns current health status as boolean. True - healthy, False - not healthy.
        If any component is not healthy, status is False.
        String description provides information on components.
        """
        status = len(self.__not_healthy) == 0
        descr = json.dumps({
            "healthy": { component: self.__msg[component] for component in self.__healthy },
            "not healthy": { component: self.__msg[component] for component in self.__not_healthy }
        })
        return status, descr
