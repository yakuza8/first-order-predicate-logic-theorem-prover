from abc import ABCMeta, abstractmethod
from typing import Optional, List


class FirstOrderPredicateLogicEntity(metaclass=ABCMeta):

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def has_child(self) -> bool:
        pass

    @abstractmethod
    def get_child(self) -> Optional[List['FirstOrderPredicateLogicEntity']]:
        pass

    @staticmethod
    @abstractmethod
    def build(value: str) -> Optional['FirstOrderPredicateLogicEntity']:
        pass
