class Singleton:
    """ Class that can be used as a decorator to enforce the Singleton design pattern."""

    def __init__(self, decorated):
        """ Default constructor."""
        self._decorated = decorated
        self._instance = None

    def instance(self, *args):
        """ method that creates the (only) instance ever available. """
        if not self._instance:
            self._instance = self._decorated(*args)
        return self._instance

    def __call__(self):
        """ Method to enfornce that a Singleton object can be only created by calling `instance()`. """
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        """ Method that can be used to check whether the object is of the expected type.
        Args:
            inst: The instance that should be checked
        Returns:
            true if the parameter `inst` is of the same type, false if otherwise
        """
        return isinstance(inst, self._decorated)
