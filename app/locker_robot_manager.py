from app.locker import Locker
import inspect


class LockerRobotManager:
    """
    A manager that coordinates multiple lockers and robots for bag storage and retrieval.

    The manager prefers to store bags in robots first, then in its own lockers if all robots are full.

    Args:
        lockers (list): A list of Locker instances to be managed directly by this manager.
        robots (list): A list of robot objects (PrimaryLockerRobot, SmartLockerRobot, etc.) to be managed.

    Raises:
        ValueError: If both lockers and robots lists are empty.
        TypeError: If any item in lockers is not a Locker instance or if any robot doesn't support
                  the required interface (store_bag and retrieve_bag methods).
    """

    def __init__(self, lockers, robots):
        # Validate inputs
        if not lockers and not robots:
            raise ValueError("Must provide at least one locker or one robot")

        # Validate lockers
        if lockers and not all(isinstance(locker, Locker) for locker in lockers):
            raise TypeError("All items in lockers must be Locker instances")

        # Validate robots - check they have the required callable methods
        for robot in robots:
            if (
                not hasattr(robot, "store_bag")
                or not callable(getattr(robot, "store_bag", None))
                or not hasattr(robot, "retrieve_bag")
                or not callable(getattr(robot, "retrieve_bag", None))
            ):
                raise TypeError(
                    "All items in robots must have store_bag and retrieve_bag methods"
                )

        self.lockers = lockers
        self.robots = robots

    def store_bag(self, content):
        """
        Store a bag, preferring to use robots first, then direct lockers if all robots are full.

        Args:
            content (str): The contents of the bag to store.

        Returns:
            str: A ticket for retrieving the bag.

        Raises:
            TypeError: If content is not a string.
            ValueError: If all lockers and robots are full.
        """
        if not isinstance(content, str):
            raise TypeError("Bag content must be a string")

        # Try to store in robots first
        for robot in self.robots:
            try:
                return robot.store_bag(content)
            except ValueError:
                # Robot is full, try the next one
                continue

        # If we get here, all robots are full or there are no robots
        # Try to store in our own lockers
        for locker in self.lockers:
            if locker.available_capability > 0:
                return locker.store_bag(content)

        # If we get here, all lockers are full too
        raise ValueError("All lockers are full")

    def retrieve_bag(self, ticket):
        """
        Retrieve a bag using a ticket.

        The manager will check all robots and its direct lockers for the ticket.

        Args:
            ticket (str): The ticket issued when storing the bag.

        Returns:
            str: The content of the retrieved bag.

        Raises:
            ValueError: If the ticket is invalid or not found in any locker or robot.
        """
        # Try to retrieve from robots first
        for robot in self.robots:
            try:
                return robot.retrieve_bag(ticket)
            except ValueError:
                # Not found in this robot, try the next one
                continue

        # Try to retrieve from our own lockers
        for locker in self.lockers:
            try:
                return locker.retrieve_bag(ticket)
            except ValueError:
                # Not found in this locker, try the next one
                continue

        # If we get here, the ticket wasn't found anywhere
        raise ValueError("Invalid ticket")
