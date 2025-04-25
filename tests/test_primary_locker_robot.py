import pytest
from app.locker import Locker
from app.primary_locker_robot import PrimaryLockerRobot

def test_primary_locker_robot_exists():
    """Test that the PrimaryLockerRobot class exists."""
    lockers = [Locker(1)]
    robot = PrimaryLockerRobot(lockers)
    assert isinstance(robot, PrimaryLockerRobot)

def test_primary_locker_robot_with_invalid_lockers():
    """Test that the PrimaryLockerRobot constructor validates locker input."""
    # Test with empty array
    with pytest.raises(ValueError, match="Must provide at least one locker"):
        PrimaryLockerRobot([])
        
    # Test with invalid locker type
    with pytest.raises(TypeError, match="All items must be Locker instances"):
        PrimaryLockerRobot(["not a locker"])
        
    # Test with mixed valid and invalid types
    with pytest.raises(TypeError, match="All items must be Locker instances"):
        PrimaryLockerRobot([Locker(1), "not a locker"])

def test_store_bag_in_first_available_locker():
    """Test that the robot stores a bag in the first locker with available capability."""
    locker1 = Locker(1)
    locker2 = Locker(1)
    robot = PrimaryLockerRobot([locker1, locker2])
    
    content = "bag content"
    ticket = robot.store_bag(content)
    
    # Verify ticket format
    assert isinstance(ticket, str)
    assert ticket != ""
    
    # Verify first locker was used (capability decreased)
    assert locker1.available_capability == 0
    assert locker2.available_capability == 1

def test_store_bag_in_second_locker_when_first_is_full():
    """Test that the robot stores in the second locker when the first is full."""
    locker1 = Locker(1)
    locker2 = Locker(1)
    robot = PrimaryLockerRobot([locker1, locker2])
    
    # Fill up the first locker
    locker1.store_bag("bag 1")
    
    # Store another bag
    content = "bag 2"
    ticket = robot.store_bag(content)
    
    # Verify second locker was used
    assert locker1.available_capability == 0
    assert locker2.available_capability == 0

def test_store_bag_when_all_lockers_are_full():
    """Test that the robot raises an error when all lockers are full."""
    locker1 = Locker(1)
    locker2 = Locker(1)
    robot = PrimaryLockerRobot([locker1, locker2])
    
    # Fill up both lockers
    locker1.store_bag("bag 1")
    locker2.store_bag("bag 2")
    
    # Try to store another bag
    with pytest.raises(ValueError, match="All lockers are full"):
        robot.store_bag("bag 3")

def test_retrieve_bag_with_valid_ticket():
    """Test that the robot can retrieve a bag with a valid ticket from any locker."""
    locker1 = Locker(1)
    locker2 = Locker(1)
    robot = PrimaryLockerRobot([locker1, locker2])
    
    # Store a bag directly in the first locker
    content1 = "bag in first locker"
    ticket1 = locker1.store_bag(content1)
    
    # Store a bag directly in the second locker
    content2 = "bag in second locker"
    ticket2 = locker2.store_bag(content2)
    
    # Retrieve from first locker
    retrieved1 = robot.retrieve_bag(ticket1)
    assert retrieved1 == content1
    
    # Retrieve from second locker
    retrieved2 = robot.retrieve_bag(ticket2)
    assert retrieved2 == content2

def test_retrieve_bag_with_invalid_ticket():
    """Test that the robot raises an error when given an invalid ticket."""
    locker1 = Locker(1)
    locker2 = Locker(1)
    robot = PrimaryLockerRobot([locker1, locker2])
    
    with pytest.raises(ValueError, match="Invalid ticket"):
        robot.retrieve_bag("invalid-ticket")

def test_store_and_retrieve_bag_through_robot():
    """Test the full flow of storing and retrieving a bag through the robot."""
    locker1 = Locker(1)
    locker2 = Locker(1)
    robot = PrimaryLockerRobot([locker1, locker2])
    
    content = "test bag content"
    ticket = robot.store_bag(content)
    
    retrieved = robot.retrieve_bag(ticket)
    assert retrieved == content
    
    # Verify capability was restored
    assert locker1.available_capability == 1

def test_store_bag_with_invalid_content():
    """Test that storing a bag with non-string content raises an error."""
    locker1 = Locker(1)
    locker2 = Locker(1)
    robot = PrimaryLockerRobot([locker1, locker2])
    
    with pytest.raises(TypeError, match="Bag content must be a string"):
        robot.store_bag(123)
        
    with pytest.raises(TypeError, match="Bag content must be a string"):
        robot.store_bag(["item"])
        
    with pytest.raises(TypeError, match="Bag content must be a string"):
        robot.store_bag(None)