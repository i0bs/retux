from ...const import MISSING, NotNeeded


class Factory:
    """A base factory for parsing Gateway events into resource dataclasses."""

    @classmethod
    def define(cls, name: str, data: NotNeeded[dict] = MISSING):
        """
        Defines an event for entrypoint to the main factory.

        Parameters
        ----------
        name : `str`
            The name of the Gateway event.
        data : `dict`, optional
            The supplied payload data from the event.

            If we couldn't find any data to supply
            with it, we mark it out as `MISSING`.
        """
        event = cls.events.get(name, [])
        event.append(data)
        cls.events[name] = event
        return cls
