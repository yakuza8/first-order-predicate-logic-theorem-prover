from abc import ABCMeta, abstractmethod
from typing import Optional


class FirstOrderPredicateLogicEntity(metaclass=ABCMeta):

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @staticmethod
    @abstractmethod
    def build(value: str) -> Optional['FirstOrderPredicateLogicEntity']:
        pass
