import pytest
from app.locker import Locker
from app.primary_locker_robot import PrimaryLockerRobot
from app.smart_locker_robot import SmartLockerRobot
from app.locker_robot_manager import LockerRobotManager
from app.locker_robot_director import LockerRobotDirector


def test_locker_robot_director_exists():
    """Test that the LockerRobotDirector class exists."""
    managers = [LockerRobotManager([Locker(1)], [])]
    director = LockerRobotDirector(managers)
    assert isinstance(director, LockerRobotDirector)


def test_director_with_invalid_managers():
    """Test that the LockerRobotDirector constructor validates manager input."""
    # Test with empty array
    with pytest.raises(ValueError, match="Must provide at least one manager"):
        LockerRobotDirector([])

    # Test with invalid manager type
    with pytest.raises(
        TypeError, match="All items must be LockerRobotManager instances"
    ):
        LockerRobotDirector(["not a manager"])

    # Test with mixed valid and invalid types
    valid_manager = LockerRobotManager([Locker(1)], [])
    with pytest.raises(
        TypeError, match="All items must be LockerRobotManager instances"
    ):
        LockerRobotDirector([valid_manager, "not a manager"])


def test_director_stores_managers():
    """Test that the LockerRobotDirector correctly stores the managers."""
    manager1 = LockerRobotManager([Locker(1)], [])
    manager2 = LockerRobotManager([Locker(2)], [])
    director = LockerRobotDirector([manager1, manager2])

    assert director.managers == [manager1, manager2]


def test_generate_report_with_minimal_manager():
    """Test generating a report with a manager that has minimal storage."""
    # Create a manager with a single locker
    locker = Locker(1)
    manager = LockerRobotManager([locker], [])
    director = LockerRobotDirector([manager])

    # Expected report format:
    # M 1 1
    #     L 1 1
    expected_report = "M 1 1\n    L 1 1\n"

    assert director.generateReport() == expected_report


def test_generate_report_with_manager_with_lockers():
    """Test generating a report with a manager that has lockers but no robots."""
    # Create lockers with different capabilities
    locker1 = Locker(3)  # capability 3, fully available
    locker2 = Locker(5)  # capability 5, fully available

    # Store a bag in locker2
    locker2.store_bag("bag")  # reduces availability to 4

    manager = LockerRobotManager([locker1, locker2], [])
    director = LockerRobotDirector([manager])

    # Expected report format:
    # M 7 8
    #     L 3 3
    #     L 4 5
    expected_report = "M 7 8\n    L 3 3\n    L 4 5\n"

    assert director.generateReport() == expected_report


def test_generate_report_with_manager_with_robots():
    """Test generating a report with a manager that has robots but no direct lockers."""
    # Create lockers for robots
    robot1_locker = Locker(2)
    robot2_locker1 = Locker(3)
    robot2_locker2 = Locker(4)

    # Store bags to change available capability
    robot1_locker.store_bag("bag1")  # reduces to 1
    robot2_locker2.store_bag("bag2")  # reduces to 3

    # Create robots with lockers
    robot1 = PrimaryLockerRobot([robot1_locker])
    robot2 = SmartLockerRobot([robot2_locker1, robot2_locker2])

    # Create manager with robots
    manager = LockerRobotManager([], [robot1, robot2])
    director = LockerRobotDirector([manager])

    # Expected report format:
    # M 7 9
    #     R 1 2
    #         L 1 2
    #     R 6 7
    #         L 3 3
    #         L 3 4
    expected_report = (
        "M 7 9\n    R 1 2\n        L 1 2\n    R 6 7\n        L 3 3\n        L 3 4\n"
    )

    assert director.generateReport() == expected_report


def test_generate_report_with_complex_hierarchy():
    """Test generating a report with multiple managers, each with lockers and robots."""
    # Manager 1 with lockers and robots
    manager1_locker = Locker(2)
    robot1_locker = Locker(3)
    robot1 = PrimaryLockerRobot([robot1_locker])
    manager1 = LockerRobotManager([manager1_locker], [robot1])

    # Manager 2 with only lockers
    manager2_locker1 = Locker(4)
    manager2_locker2 = Locker(5)
    manager2 = LockerRobotManager([manager2_locker1, manager2_locker2], [])

    # Create director with both managers
    director = LockerRobotDirector([manager1, manager2])

    # Expected report format:
    # M 5 5
    #     L 2 2
    #     R 3 3
    #         L 3 3
    # M 9 9
    #     L 4 4
    #     L 5 5
    expected_report = (
        "M 5 5\n    L 2 2\n    R 3 3\n        L 3 3\n" + "M 9 9\n    L 4 4\n    L 5 5\n"
    )

    assert director.generateReport() == expected_report
