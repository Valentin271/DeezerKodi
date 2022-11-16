"""
This module contains the application's router.
"""
from lib.helpers.logger import Logger


class Router(object):
    """
    The Router class holds the application's available routes.
    Given a path it can determine where to go.
    """

    def __init__(self, location):
        Logger.info("Initializing router with location {}".format(location))
        self.__location = location
        self.__routes = {}

    def add(self, route, action):
        """
        Registers a new route associated with an action.

        :param str route: The route to add
        :param typing.Callable action:
        """
        self.__routes[route] = action

    def route(self, app):
        """
        Call the route action corresponding to the current location in the application.

        :param src.app.Application app: Application's arguments
        :return: a list of items to display
        """
        location = self.__location.split('/')
        action = None

        for route, act in self.__routes.items():
            parts = route.split('/')
            parameters = {}

            if len(location) != len(parts):
                continue

            for i, part in enumerate(parts):
                if part.startswith('{') and part.endswith('}'):
                    parameters[part[1:-1]] = location[i]
                elif location[i] != part:
                    action = None
                    break

                action = act

            if action is not None:
                # Get the action's class, giving it app arguments
                action.__self__.app = app
                return action(**parameters)

        return None
