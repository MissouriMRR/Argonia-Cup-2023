"""Class to contain setters and getters for settings in various flight states"""

class StateSettings:
    """
    Initialize settings for state machine
    Methods
    -------
        __init__
            Sets preliminary values for SUAS overheads
        @Property
        run_title() -> str
            Sets the name of the current flight for logging
        run_description() -> str
            Sets the description of current flight mission
        @Setters
        run_title() -> None
            Enables access to description of current flight mission
        run_description() -> None
            Enables access to description of current flight mission
    Attributes
    ----------
        __competition_waypoints: bool
            Determines if the flight should use competition waypoints or not. If false, will use golf course waypoints.
        __run_title: str
            Title of Competition
        __run_description: str
            Description for Competition
    """
    def __init__(self, competition_waypoints: bool, title: str, description: str) -> None:
        """
        Default constructor results in default settings
        Parameters
        ----------
        competition_waypoints: bool
            Determines if the flight should use competition waypoints or not. If false, will use golf course waypoints.
        __run_title: str
            Title of current flight mission, for logging purposes
        __run_description: str
            Description of current flight mission, for logging purposes
        Returns
        -------
            None
        """
        self.competition_waypoints = competition_waypoints
        self.__run_title = title
        self.__run_description = description
    
    # ---- Other settings ---- #
    @property
    def run_title(self) -> str:
        """
        Set a title for the run/test to be output in logging
        Parameters
        ----------
            N/A
        Returns
        -------
            str
                Created title for flight mission
        """
        return self.__run_title

    @run_title.setter
    def run_title(self, title: str) -> None:
        """
        Sets the title of the flight mission for logging
        Parameters
        ----------
            title: str
                Desired title for the flight
        Returns
        -------
            None
        """
        self.__run_title = title

    @property
    def run_description(self) -> str:
        """
        Set a description for the run/test to be output in logging
        Parameters
        ----------
            N/A
        Returns
        -------
            str
                Desired description for flight mission
        """
        return self.__run_description

    @run_description.setter
    def run_description(self, description: str) -> None:
        """
        Sets a description of the flight mission
        Parameters
        ----------
            description: str
                Written description for flight mission for logs
        Returns
        -------
            None
        """
        self.__run_description = description