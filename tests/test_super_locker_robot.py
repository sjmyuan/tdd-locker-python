import pytest
from app.locker import Locker
from app.super_locker_robot import SuperLockerRobot


def test_super_locker_robot_exists():
    """Test that the SuperLockerRobot class exists."""
    lockers = [Locker(1)]
    robot = SuperLockerRobot(lockers)
    assert isinstance(robot, SuperLockerRobot)


def test_super_locker_robot_with_invalid_lockers():
    """Test that the SuperLockerRobot constructor validates locker input."""
    # Test with empty array
    with pytest.raises(ValueError, match="Must provide at least one locker"):
        SuperLockerRobot([])

    # Test with invalid locker type
    with pytest.raises(TypeError, match="All items must be Locker instances"):
        SuperLockerRobot(["not a locker"])

    # Test with mixed valid and invalid types
    with pytest.raises(TypeError, match="All items must be Locker instances"):
        SuperLockerRobot([Locker(1), "not a locker"])


def test_super_locker_robot_stores_lockers():
    """Test that the SuperLockerRobot correctly stores the lockers."""
    locker1 = Locker(1)
    locker2 = Locker(2)
    robot = SuperLockerRobot([locker1, locker2])

    assert robot.lockers == [locker1, locker2]


def test_store_bag_returns_ticket():
    """Test that the SuperLockerRobot's store_bag method returns a valid ticket."""
    locker = Locker(1)
    robot = SuperLockerRobot([locker])

    ticket = robot.store_bag("bag content")
    assert isinstance(ticket, str)
    assert ticket != ""


def test_store_bag_in_locker_with_max_vacancy_rate():
    """Test that the robot stores a bag in the locker with maximum vacancy rate."""
    # Create lockers with different capabilities and vacancy rates
    locker1 = Locker(2)  # vacancy rate = 2/2 = 1.0 (100%)
    locker2 = Locker(3)  # vacancy rate = 3/3 = 1.0 (100%)

    # Reduce availability in locker2
    locker2.store_bag("existing bag")  # Now vacancy rate = 2/3 = 0.67 (67%)

    robot = SuperLockerRobot([locker1, locker2])

    # Store a bag - should go to locker1 as it has higher vacancy rate (100% vs 67%)
    robot.store_bag("test bag")

    # Check that locker1's capability decreased
    assert locker1.available_capability == 1
    assert locker2.available_capability == 2


def test_store_bag_with_equal_vacancy_rates():
    """Test that when vacancy rates are equal, it picks the first locker found."""
    locker1 = Locker(2)  # vacancy rate = 2/2 = 1.0 (100%)
    locker2 = Locker(4)  # vacancy rate = 4/4 = 1.0 (100%)

    robot = SuperLockerRobot([locker1, locker2])

    # Store a bag - should go to locker1 as both have 100% vacancy but locker1 comes first
    robot.store_bag("test bag")

    # Check that locker1's capability decreased
    assert locker1.available_capability == 1
    assert locker2.available_capability == 4


def test_store_multiple_bags_prioritizes_max_vacancy_rate():
    """Test that storing multiple bags always uses the locker with max vacancy rate."""
    locker1 = Locker(2)  # vacancy rate = 2/2 = 1.0 (100%)
    locker2 = Locker(4)  # vacancy rate = 4/4 = 1.0 (100%)

    robot = SuperLockerRobot([locker1, locker2])

    # First bag should go to locker1 (both have 100%, but locker1 is first)
    robot.store_bag("bag 1")
    # Now locker1 has vacancy rate = 1/2 = 0.5 (50%)
    # and locker2 has vacancy rate = 4/4 = 1.0 (100%)

    # Second bag should go to locker2 (higher vacancy rate now)
    robot.store_bag("bag 2")
    # Now locker1 has vacancy rate = 1/2 = 0.5 (50%)
    # and locker2 has vacancy rate = 3/4 = 0.75 (75%)

    # Check capabilities reflect this
    assert locker1.available_capability == 1
    assert locker2.available_capability == 3


def test_store_bag_when_all_lockers_are_full():
    """Test that the robot raises an error when all lockers are full."""
    locker1 = Locker(1)
    locker2 = Locker(1)
    robot = SuperLockerRobot([locker1, locker2])

    # Fill up both lockers
    robot.store_bag("bag 1")
    robot.store_bag("bag 2")

    # Try to store another bag
    with pytest.raises(ValueError, match="All lockers are full"):
        robot.store_bag("bag 3")


def test_store_bag_with_invalid_content():
    """Test that storing a bag with non-string content raises an error."""
    robot = SuperLockerRobot([Locker(1)])

    with pytest.raises(TypeError, match="Bag content must be a string"):
        robot.store_bag(123)

    with pytest.raises(TypeError, match="Bag content must be a string"):
        robot.store_bag(["item"])

    with pytest.raises(TypeError, match="Bag content must be a string"):
        robot.store_bag(None)


def test_retrieve_bag_with_valid_ticket():
    """Test that the robot can retrieve a bag with a valid ticket."""
    locker = Locker(1)
    robot = SuperLockerRobot([locker])

    content = "test bag content"
    ticket = robot.store_bag(content)

    retrieved_content = robot.retrieve_bag(ticket)
    assert retrieved_content == content


def test_retrieve_bag_from_correct_locker():
    """Test that the robot retrieves bags from the correct locker."""
    locker1 = Locker(2)  # 100% vacancy rate
    locker2 = Locker(3)
    locker2.store_bag("existing bag")  # 67% vacancy rate

    robot = SuperLockerRobot([locker1, locker2])

    content = "bag content"
    ticket = robot.store_bag(content)  # Should go to locker1 due to higher vacancy rate

    # Verify the bag was stored in locker1
    assert locker1.available_capability == 1

    # Retrieve the bag
    retrieved_content = robot.retrieve_bag(ticket)
    assert retrieved_content == content

    # Verify capability was restored in the correct locker
    assert locker1.available_capability == 2


def test_retrieve_bag_with_invalid_ticket():
    """Test that the robot raises an error when given an invalid ticket."""
    robot = SuperLockerRobot([Locker(1)])

    with pytest.raises(ValueError, match="Invalid ticket"):
        robot.retrieve_bag("invalid-ticket")


def test_retrieve_bag_after_storing_multiple_bags():
    """Test retrieving multiple bags stored across different lockers."""
    locker1 = Locker(2)  # 100% vacancy rate initially
    locker2 = Locker(4)  # 100% vacancy rate initially

    robot = SuperLockerRobot([locker1, locker2])

    # Store bags in different lockers (based on vacancy rate)
    content1 = "bag 1"
    content2 = "bag 2"
    content3 = "bag 3"

    # First bag should go to locker1 (both have 100%, but locker1 is first)
    ticket1 = robot.store_bag(content1)

    # Second bag should go to locker2 (higher vacancy rate now)
    ticket2 = robot.store_bag(content2)

    # Third bag should also go to locker2 (still higher vacancy rate)
    ticket3 = robot.store_bag(content3)

    # Retrieve bags in different order and verify contents
    assert robot.retrieve_bag(ticket2) == content2
    assert robot.retrieve_bag(ticket1) == content1
    assert robot.retrieve_bag(ticket3) == content3

    # Verify capabilities are restored correctly
    assert locker1.available_capability == 2
    assert locker2.available_capability == 4
