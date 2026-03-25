from dataclasses import dataclass


@dataclass(slots=True)
class User:
    id: int
    name: str
    email: str
