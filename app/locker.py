import uuid

class Locker:
    """
    A Locker class implementation.
    
    Args:
        capability (int): The capacity of the locker. Must be a positive integer.
        
    Raises:
        TypeError: If capability is not an integer.
        ValueError: If capability is less than or equal to 0.
    """
    def __init__(self, capability):
        if not isinstance(capability, int):
            raise TypeError("Capability must be an integer")
        
        if capability <= 0:
            raise ValueError("Capability must be greater than 0")
            
        self.capability = capability
        self.available_capability = capability
        self.stored_bags = {}
        
    def store_bag(self, content):
        """
        Store a bag in the locker and return a ticket for retrieval.
        
        Args:
            content (str): The contents of the bag to store.
            
        Returns:
            str: A unique ticket ID for bag retrieval.
            
        Raises:
            TypeError: If content is not a string.
            ValueError: If the locker is at full capacity.
        """
        if not isinstance(content, str):
            raise TypeError("Bag content must be a string")
            
        if self.available_capability <= 0:
            raise ValueError("Locker is full")
            
        # Generate a unique ticket ID
        ticket = str(uuid.uuid4())
        
        # Store the bag content with the ticket as the key
        self.stored_bags[ticket] = content
        
        # Reduce available capability
        self.available_capability -= 1
        
        return ticket

    def retrieve_bag(self, ticket):
        """
        Retrieve a bag from the locker using a ticket.
        
        Args:
            ticket (str): The ticket issued when storing the bag.
            
        Returns:
            str: The content of the retrieved bag.
            
        Raises:
            ValueError: If the ticket is invalid or has already been used.
        """
        # Check for valid ticket format and existence in one conditional
        if not isinstance(ticket, str) or ticket not in self.stored_bags:
            raise ValueError("Invalid ticket")
            
        # Get the bag content
        content = self.stored_bags[ticket]
        
        # Remove the bag from storage
        del self.stored_bags[ticket]
        
        # Restore capability
        self.available_capability += 1
        
        return content