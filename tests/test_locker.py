import pytest
from app.locker import Locker

def test_locker_exists():
    """Test that the Locker class exists."""
    locker = Locker(1)
    assert isinstance(locker, Locker)

def test_locker_with_valid_capability():
    """Test that the Locker can be instantiated with a valid capability."""
    # Test with a positive integer
    locker = Locker(5)
    assert locker.capability == 5
    
    # Test with a different positive integer
    locker = Locker(10)
    assert locker.capability == 10

def test_locker_with_invalid_capability():
    """Test that the Locker raises an exception when given invalid capability values."""
    # Test with zero
    with pytest.raises(ValueError, match="Capability must be greater than 0"):
        Locker(0)
    
    # Test with negative number
    with pytest.raises(ValueError, match="Capability must be greater than 0"):
        Locker(-5)
        
    # Test with non-integer type
    with pytest.raises(TypeError, match="Capability must be an integer"):
        Locker("5")

def test_store_bag_returns_ticket():
    """Test that storing a bag returns a ticket."""
    locker = Locker(1)
    ticket = locker.store_bag("bag contents")
    assert isinstance(ticket, str)
    assert ticket != ""

def test_store_multiple_bags():
    """Test that multiple bags can be stored and unique tickets are returned."""
    locker = Locker(2)
    ticket1 = locker.store_bag("bag 1 contents")
    ticket2 = locker.store_bag("bag 2 contents")
    assert ticket1 != ticket2

def test_store_bag_at_full_capacity():
    """Test that trying to store a bag when the locker is full raises an error."""
    locker = Locker(1)
    locker.store_bag("bag contents")
    
    with pytest.raises(ValueError, match="Locker is full"):
        locker.store_bag("another bag")

def test_capability_decreases_after_storing():
    """Test that the available capability decreases after storing a bag."""
    locker = Locker(3)
    assert locker.available_capability == 3
    
    locker.store_bag("bag 1")
    assert locker.available_capability == 2
    
    locker.store_bag("bag 2")
    assert locker.available_capability == 1

def test_store_bag_with_invalid_content():
    """Test that storing a bag with non-string content raises an error."""
    locker = Locker(1)
    
    with pytest.raises(TypeError, match="Bag content must be a string"):
        locker.store_bag(123)
        
    with pytest.raises(TypeError, match="Bag content must be a string"):
        locker.store_bag(["item"])
        
    with pytest.raises(TypeError, match="Bag content must be a string"):
        locker.store_bag(None)

def test_retrieve_bag_with_valid_ticket():
    """Test that a bag can be retrieved with a valid ticket."""
    locker = Locker(1)
    content = "test bag content"
    ticket = locker.store_bag(content)
    
    retrieved_content = locker.retrieve_bag(ticket)
    assert retrieved_content == content

def test_retrieve_bag_with_invalid_ticket():
    """Test that retrieving with an invalid ticket raises an error."""
    locker = Locker(1)
    
    with pytest.raises(ValueError, match="Invalid ticket"):
        locker.retrieve_bag("invalid-ticket")
        
    # Store a bag and try a different invalid ticket
    locker.store_bag("content")
    with pytest.raises(ValueError, match="Invalid ticket"):
        locker.retrieve_bag("another-invalid-ticket")

def test_capability_restores_after_retrieval():
    """Test that capability is restored after retrieving a bag."""
    locker = Locker(2)
    
    # Store bags and check capability
    ticket1 = locker.store_bag("bag 1")
    ticket2 = locker.store_bag("bag 2")
    assert locker.available_capability == 0
    
    # Retrieve first bag and check capability is restored
    locker.retrieve_bag(ticket1)
    assert locker.available_capability == 1
    
    # Retrieve second bag and check capability is restored
    locker.retrieve_bag(ticket2)
    assert locker.available_capability == 2

def test_ticket_can_only_be_used_once():
    """Test that a ticket can only be used once for retrieval."""
    locker = Locker(1)
    ticket = locker.store_bag("content")
    
    # First retrieval should work
    locker.retrieve_bag(ticket)
    
    # Second retrieval with same ticket should fail
    with pytest.raises(ValueError, match="Invalid ticket"):
        locker.retrieve_bag(ticket)