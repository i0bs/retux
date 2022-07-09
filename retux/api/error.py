class HTTPException(Exception):
    """An error occured trying to run an HTTP request through the REST API."""

    payload: dict
    """The error trace stack of the exception."""
    message: str
    """The message body of the exception."""
    code: int
    """The error code to correlate the exception to."""
    severity: int
    """The severity level to correlate the exception to. This is treated for logging purposes."""

    def __init__(self, payload: dict, severity: int = 0):
        """
        Creates a new exception for HTTP requests.

        Parameters
        ----------
        payload : `str`
            The error trace stack of the exception.
        severity : `int`, optional
            The severity level to correlate the exception to. This is treated for logging purposes.
        """
        self.payload = payload
        self.message = self.payload.get("message")
        self.code = self.payload.get("code")
        self.severity = severity

        self._parse()

    def _parse(self):
        """Parses the contents of the error given and prepares for printout."""

        # TODO: Figure out a way to make the error payload appear as a -> tree from
        # the dictionary keys, and exclude _errors.
        # ex: activities -> 0 -> platform -> Value must be one of ('desktop', 'android', 'ios'). (err. 50035, Invalid Form Body)

        path_to_err = f"{self.payload.get('code')} -> {self.payload.get('message')}"
        self._printout(path_to_err)

    def _printout(self, content: str):
        """Prints out the content given and raises as an exception.

        Parameters
        ----------
        content : `str`
            The content of the exception.

        Raises: `HTTPException`
        """
        super().__init__(content)
