import pytest
from app.locker import Locker
from app.smart_locker_robot import SmartLockerRobot


def test_smart_locker_robot_exists():
    """Test that the SmartLockerRobot class exists."""
    lockers = [Locker(1)]
    robot = SmartLockerRobot(lockers)
    assert isinstance(robot, SmartLockerRobot)


def test_smart_locker_robot_with_invalid_lockers():
    """Test that the SmartLockerRobot constructor validates locker input."""
    # Test with empty array
    with pytest.raises(ValueError, match="Must provide at least one locker"):
        SmartLockerRobot([])

    # Test with invalid locker type
    with pytest.raises(TypeError, match="All items must be Locker instances"):
        SmartLockerRobot(["not a locker"])

    # Test with mixed valid and invalid types
    with pytest.raises(TypeError, match="All items must be Locker instances"):
        SmartLockerRobot([Locker(1), "not a locker"])


def test_smart_locker_robot_stores_lockers():
    """Test that the SmartLockerRobot correctly stores the lockers."""
    locker1 = Locker(1)
    locker2 = Locker(2)
    robot = SmartLockerRobot([locker1, locker2])

    assert robot.lockers == [locker1, locker2]


def test_store_bag_returns_ticket():
    """Test that the SmartLockerRobot's store_bag method returns a valid ticket."""
    locker = Locker(1)
    robot = SmartLockerRobot([locker])

    ticket = robot.store_bag("bag content")
    assert isinstance(ticket, str)
    assert ticket != ""


def test_store_bag_in_locker_with_max_capability():
    """Test that the robot stores a bag in the locker with maximum available capability."""
    # Create lockers with different capabilities
    locker1 = Locker(1)  # capability 1
    locker2 = Locker(3)  # capability 3
    locker3 = Locker(2)  # capability 2

    robot = SmartLockerRobot([locker1, locker2, locker3])

    # Store a bag - should go to locker2 as it has the highest capability (3)
    robot.store_bag("bag content")

    # Check that locker2's capability decreased
    assert locker2.available_capability == 2
    assert locker1.available_capability == 1
    assert locker3.available_capability == 2


def test_store_multiple_bags_prioritizes_max_capability():
    """Test that storing multiple bags always uses the locker with max capability."""
    locker1 = Locker(2)  # capability 2
    locker2 = Locker(3)  # capability 3
    locker3 = Locker(1)  # capability 1

    robot = SmartLockerRobot([locker1, locker2, locker3])

    # First bag should go to locker2 (capability 3)
    robot.store_bag("bag 1")
    assert locker2.available_capability == 2
    assert locker1.available_capability == 2
    assert locker3.available_capability == 1

    # Second bag should still go to locker1 (now capability 2, tied with locker2)
    # But locker1 should be preferred as it was found first with max capability
    robot.store_bag("bag 2")
    assert locker2.available_capability == 2
    assert locker1.available_capability == 1
    assert locker3.available_capability == 1

    # Third bag should go to locker2 (now has max capability 2)
    robot.store_bag("bag 3")
    assert locker2.available_capability == 1
    assert locker1.available_capability == 1
    assert locker3.available_capability == 1


def test_store_bag_when_all_lockers_are_full():
    """Test that the robot raises an error when all lockers are full."""
    locker1 = Locker(1)
    locker2 = Locker(1)
    robot = SmartLockerRobot([locker1, locker2])

    # Fill up both lockers
    robot.store_bag("bag 1")
    robot.store_bag("bag 2")

    # Try to store another bag
    with pytest.raises(ValueError, match="All lockers are full"):
        robot.store_bag("bag 3")


def test_store_bag_with_invalid_content():
    """Test that storing a bag with non-string content raises an error."""
    robot = SmartLockerRobot([Locker(1)])

    with pytest.raises(TypeError, match="Bag content must be a string"):
        robot.store_bag(123)

    with pytest.raises(TypeError, match="Bag content must be a string"):
        robot.store_bag(["item"])

    with pytest.raises(TypeError, match="Bag content must be a string"):
        robot.store_bag(None)


def test_retrieve_bag_with_valid_ticket():
    """Test that the robot can retrieve a bag with a valid ticket."""
    locker = Locker(1)
    robot = SmartLockerRobot([locker])

    content = "test bag content"
    ticket = robot.store_bag(content)

    retrieved_content = robot.retrieve_bag(ticket)
    assert retrieved_content == content


def test_retrieve_bag_from_correct_locker():
    """Test that the robot retrieves bags from the correct locker."""
    locker1 = Locker(1)
    locker2 = Locker(3)  # This will be chosen for storage due to higher capability
    robot = SmartLockerRobot([locker1, locker2])

    content = "bag content"
    ticket = robot.store_bag(content)

    # Verify the bag was stored in locker2 (it has higher capability)
    assert locker2.available_capability == 2

    # Retrieve the bag
    retrieved_content = robot.retrieve_bag(ticket)
    assert retrieved_content == content

    # Verify capability was restored in the correct locker
    assert locker2.available_capability == 3


def test_retrieve_bag_with_invalid_ticket():
    """Test that the robot raises an error when given an invalid ticket."""
    robot = SmartLockerRobot([Locker(1)])

    with pytest.raises(ValueError, match="Invalid ticket"):
        robot.retrieve_bag("invalid-ticket")


def test_retrieve_bag_after_storing_multiple_bags():
    """Test retrieving multiple bags stored across different lockers."""
    locker1 = Locker(2)
    locker2 = Locker(3)
    robot = SmartLockerRobot([locker1, locker2])

    # Store bags in different lockers (based on max capability)
    content1 = "bag 1"
    content2 = "bag 2"
    content3 = "bag 3"

    # This should go to locker2 (highest capability)
    ticket1 = robot.store_bag(content1)

    # This should also go to locker2
    ticket2 = robot.store_bag(content2)

    # This should go to locker1 (now both have capability 1)
    ticket3 = robot.store_bag(content3)

    # Retrieve bags and verify contents
    assert robot.retrieve_bag(ticket1) == content1
    assert robot.retrieve_bag(ticket3) == content3
    assert robot.retrieve_bag(ticket2) == content2

    # Verify capabilities are restored
    assert locker1.available_capability == 2
    assert locker2.available_capability == 3
