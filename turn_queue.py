import heapq  # NOTE LOOK UP
from typing import Any, List, NamedTuple, Iterable, Iterator


class Ticket(NamedTuple):
    time: int
    uid: int
    value: Any


class TurnQueue(Iterable[Ticket]):
    def __init__(
            self,
            time: int = 0,
            next_uid: int = 0,
            heap: Iterable[Ticket] = (),
    ) -> None:
        self.time = time
        self.next_uid = next_uid
        # Priority queue of events mainted by heapq
        self.heap: List[Ticket] = list(heap)
        heapq.heapify(self.heap)

    def schedule(self, interval: int, value: Any) -> Ticket:
        """Schedule and return a new ticket for `value` after `interval` time.
        `interval` must be an integer, or else precision will be permanently lost.
        """
        ticket = Ticket(self.time + interval, self.next_uid, value)
        heapq.heappush(self.heap, ticket)
        self.next_uid += 1
        return ticket

    def next(self) -> Ticket:
        """Pop and return the next scheduled ticket."""
        ticket = heapq.heappop(self.heap)
        self.time = ticket.time
        return ticket

    def __iter__(self) -> Iterator[Ticket]:
        """Return an iterator that exhaust the tickets in the queue.
        New tickets can be scheduled during iteration.
        """
        while self.heap:
            yield self.next()

    def __repr__(self) -> str:
        """A string representation of thsi instance, including all tickets."""
        return "%s(time=%r, next_uid=%r, heap=%r" % (
            self.__class__.__name__,
            self.time,
            self.next_uid,
            self.heap,
        )


__all__ = (
    "Ticket",
    "TurnQueue",
)
