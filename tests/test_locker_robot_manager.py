import pytest
from app.locker import Locker
from app.primary_locker_robot import PrimaryLockerRobot
from app.smart_locker_robot import SmartLockerRobot
from app.super_locker_robot import SuperLockerRobot
from app.locker_robot_manager import LockerRobotManager


def test_locker_robot_manager_exists():
    """Test that the LockerRobotManager class exists."""
    lockers = [Locker(1)]
    robots = [PrimaryLockerRobot([Locker(1)])]
    manager = LockerRobotManager(lockers, robots)
    assert isinstance(manager, LockerRobotManager)


def test_locker_robot_manager_with_invalid_parameters():
    """Test that the LockerRobotManager constructor validates input."""
    # Valid case
    lockers = [Locker(1)]
    robots = [PrimaryLockerRobot([Locker(1)])]
    manager = LockerRobotManager(lockers, robots)

    # Test with invalid locker types
    with pytest.raises(
        TypeError, match="All items in lockers must be Locker instances"
    ):
        LockerRobotManager(["not a locker"], robots)

    # Test with invalid robot types
    with pytest.raises(
        TypeError,
        match="All items in robots must have store_bag and retrieve_bag methods",
    ):
        LockerRobotManager(lockers, ["not a robot"])

    # Empty lockers should be allowed (only robots required)
    manager = LockerRobotManager([], robots)

    # Empty robots should be allowed (only lockers required)
    manager = LockerRobotManager(lockers, [])

    # Both empty not allowed
    with pytest.raises(
        ValueError, match="Must provide at least one locker or one robot"
    ):
        LockerRobotManager([], [])


def test_store_bag_in_robots_first():
    """Test that bags are stored in robots first."""
    # Create lockers and robots
    manager_locker = Locker(1)
    robot_locker = Locker(1)
    robot = PrimaryLockerRobot([robot_locker])

    manager = LockerRobotManager([manager_locker], [robot])

    # Store a bag - should go to robot
    ticket = manager.store_bag("bag content")

    # Check that the bag was stored in the robot's locker, not manager's locker
    assert robot_locker.available_capability == 0
    assert manager_locker.available_capability == 1


def test_store_bag_in_lockers_when_robots_full():
    """Test that bags are stored in lockers when robots are full."""
    # Create a locker and a robot with a full locker
    manager_locker = Locker(1)
    robot_locker = Locker(1)
    robot_locker.store_bag("existing bag")  # Fill the robot's locker
    robot = PrimaryLockerRobot([robot_locker])

    manager = LockerRobotManager([manager_locker], [robot])

    # Store a bag - should go to manager's locker since robot is full
    ticket = manager.store_bag("new bag")

    # Check that the bag was stored in the manager's locker
    assert robot_locker.available_capability == 0
    assert manager_locker.available_capability == 0


def test_store_bag_error_when_all_lockers_full():
    """Test that an error is raised when all lockers are full."""
    # Create full lockers and robots
    manager_locker = Locker(1)
    manager_locker.store_bag("existing bag in manager")

    robot_locker = Locker(1)
    robot_locker.store_bag("existing bag in robot")
    robot = PrimaryLockerRobot([robot_locker])

    manager = LockerRobotManager([manager_locker], [robot])

    # Try to store a bag when all lockers are full
    with pytest.raises(ValueError, match="All lockers are full"):
        manager.store_bag("new bag")


def test_retrieve_bag_from_robot():
    """Test retrieving a bag that was stored in a robot."""
    manager_locker = Locker(1)
    robot_locker = Locker(1)
    robot = PrimaryLockerRobot([robot_locker])

    manager = LockerRobotManager([manager_locker], [robot])

    # Store a bag in the robot
    content = "bag in robot"
    ticket = manager.store_bag(content)

    # Retrieve the bag
    retrieved_content = manager.retrieve_bag(ticket)
    assert retrieved_content == content


def test_retrieve_bag_from_locker():
    """Test retrieving a bag that was stored in the manager's locker."""
    # Create a locker and a robot with a full locker
    manager_locker = Locker(1)
    robot_locker = Locker(1)
    robot_locker.store_bag("existing bag")  # Fill the robot's locker
    robot = PrimaryLockerRobot([robot_locker])

    manager = LockerRobotManager([manager_locker], [robot])

    # Store a bag in the manager's locker
    content = "bag in manager locker"
    ticket = manager.store_bag(content)

    # Retrieve the bag
    retrieved_content = manager.retrieve_bag(ticket)
    assert retrieved_content == content


def test_retrieve_bag_with_invalid_ticket():
    """Test that an error is raised when retrieving with an invalid ticket."""
    manager = LockerRobotManager([Locker(1)], [PrimaryLockerRobot([Locker(1)])])

    with pytest.raises(ValueError, match="Invalid ticket"):
        manager.retrieve_bag("invalid-ticket")


def test_store_bag_with_invalid_content():
    """Test that storing a bag with non-string content raises an error."""
    manager = LockerRobotManager([Locker(1)], [PrimaryLockerRobot([Locker(1)])])

    with pytest.raises(TypeError, match="Bag content must be a string"):
        manager.store_bag(123)


def test_multiple_robots_store_preference():
    """Test that when multiple robots are available, it uses the first one with availability."""
    # Create fully occupied robot and another with space
    full_robot_locker = Locker(1)
    full_robot_locker.store_bag("existing bag")
    full_robot = PrimaryLockerRobot([full_robot_locker])

    available_robot_locker = Locker(1)
    available_robot = SmartLockerRobot([available_robot_locker])

    manager = LockerRobotManager([Locker(1)], [full_robot, available_robot])

    # Store a bag - should use the available robot
    manager.store_bag("test bag")

    # Check it was stored in the second robot
    assert full_robot_locker.available_capability == 0
    assert available_robot_locker.available_capability == 0
