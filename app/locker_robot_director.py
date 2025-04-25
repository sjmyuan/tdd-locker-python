from app.locker_robot_manager import LockerRobotManager


class LockerRobotDirector:
    """
    A director that coordinates multiple LockerRobotManager instances.

    Args:
        managers (list): A list of LockerRobotManager instances to be directed.

    Raises:
        ValueError: If no managers are provided.
        TypeError: If any item in the list is not a LockerRobotManager instance.
    """

    def __init__(self, managers):
        # Validate inputs
        if not managers:
            raise ValueError("Must provide at least one manager")

        # Validate that all items are LockerRobotManager instances
        if not all(isinstance(manager, LockerRobotManager) for manager in managers):
            raise TypeError("All items must be LockerRobotManager instances")

        self.managers = managers

    def generateReport(self):
        """
        Generate a report of the current status of all managers, robots, and lockers.

        Returns:
            str: A formatted report string with the format:
            M <manager available capability> <manager max capability>
                L <locker available capability> <locker max capability>
                R <robot available capability> <robot max capability>
                    L <locker available capability> <locker max capability>
                ...
        """
        report = ""

        for manager in self.managers:
            # Calculate manager's total available and maximum capability
            manager_available = 0
            manager_max = 0

            # Calculate capability from manager's direct lockers
            for locker in manager.lockers:
                manager_available += locker.available_capability
                manager_max += locker.capability

            # Calculate capability from manager's robots
            for robot in manager.robots:
                robot_stats = self._calculate_robot_capability(robot)
                manager_available += robot_stats["available"]
                manager_max += robot_stats["max"]

            # Add manager line to report
            report += f"M {manager_available} {manager_max}\n"

            # Add manager's direct lockers to report
            for locker in manager.lockers:
                report += f"    L {locker.available_capability} {locker.capability}\n"

            # Add manager's robots to report
            for robot in manager.robots:
                robot_stats = self._calculate_robot_capability(robot)
                report += f"    R {robot_stats['available']} {robot_stats['max']}\n"

                # Add robot's lockers to report
                for locker in robot.lockers:
                    report += (
                        f"        L {locker.available_capability} {locker.capability}\n"
                    )

        return report

    def _calculate_robot_capability(self, robot):
        """
        Helper method to calculate the total available and maximum capability for a robot.

        Args:
            robot: A robot object with lockers.

        Returns:
            dict: A dictionary with 'available' and 'max' capability values.
        """
        available = 0
        max_capability = 0

        for locker in robot.lockers:
            available += locker.available_capability
            max_capability += locker.capability

        return {"available": available, "max": max_capability}
