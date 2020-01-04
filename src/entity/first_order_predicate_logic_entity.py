from abc import ABCMeta, abstractmethod


class FirstOrderPredicateLogicEntity(metaclass=ABCMeta):

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @staticmethod
    @abstractmethod
    def validate(value: str) -> bool:
        pass
