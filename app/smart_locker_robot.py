from app.locker import Locker


class SmartLockerRobot:
    """
    A smart robot that manages multiple lockers for bag storage and retrieval.

    Args:
        lockers (list): A list of Locker instances to be managed by the robot.

    Raises:
        ValueError: If an empty list of lockers is provided.
        TypeError: If any item in the list is not a Locker instance.
    """

    def __init__(self, lockers):
        if not lockers:
            raise ValueError("Must provide at least one locker")

        if not all(isinstance(locker, Locker) for locker in lockers):
            raise TypeError("All items must be Locker instances")

        self.lockers = lockers

    def store_bag(self, content):
        """
        Store a bag in the locker with maximum available capability.

        Args:
            content (str): The contents of the bag to store.

        Returns:
            str: A ticket for retrieving the bag.

        Raises:
            TypeError: If content is not a string.
            ValueError: If all lockers are full.
        """
        if not isinstance(content, str):
            raise TypeError("Bag content must be a string")

        # Find the locker with maximum available capability
        max_capability_locker = None
        max_capability = 0

        for locker in self.lockers:
            if (
                locker.available_capability > 0
                and locker.available_capability > max_capability
            ):
                max_capability = locker.available_capability
                max_capability_locker = locker

        if max_capability_locker is None:
            raise ValueError("All lockers are full")

        # Store the bag in the selected locker and return the ticket
        return max_capability_locker.store_bag(content)

    def retrieve_bag(self, ticket):
        """
        Retrieve a bag using a ticket.

        The robot will check all its lockers for the ticket.

        Args:
            ticket (str): The ticket issued when storing the bag.

        Returns:
            str: The content of the retrieved bag.

        Raises:
            ValueError: If the ticket is invalid or not found in any locker.
        """
        for locker in self.lockers:
            try:
                return locker.retrieve_bag(ticket)
            except ValueError:
                continue

        raise ValueError("Invalid ticket")
