from abc import ABCMeta, abstractmethod
from typing import Optional, List


class FirstOrderPredicateLogicEntity(metaclass=ABCMeta):

    @abstractmethod
    def __repr__(self):
        """
        Representation of the entity
        """

    @abstractmethod
    def __str__(self):
        """
        String representation of the entity
        """

    @abstractmethod
    def __eq__(self, other):
        """
        Equality check operator for the entity
        :param other: Other object instance to check equality
        :return: Boolean value representing equality of this instance with respect to the given parameter
        """

    @abstractmethod
    def __contains__(self, item):
        """
        Elementwise containment check operator for the entity
        :param item: Item which will be exposed to IN check in the current entity
        :return: Boolean flag representing whether the given item is in the current element
        """

    @abstractmethod
    def get_name(self) -> str:
        """
        Get name property of the current entity
        :return: Name of the current entity as a string value
        """

    @abstractmethod
    def has_child(self) -> bool:
        """
        Check procedure of existence of children of the current entity
        :return: Boolean flag representing if the current entity has children or not
        """

    @abstractmethod
    def get_child(self) -> Optional[List['FirstOrderPredicateLogicEntity']]:
        """
        Obtainment functionality of children of the current entity
        :return: Children of the current entity if they exist otherwise None will be returned
        """

    @abstractmethod
    def find_variable_and_apply_substitution(self, substitute: 'FirstOrderPredicateLogicEntity',
                                             variable: 'FirstOrderPredicateLogicEntity'):
        """
        Method to apply substitution to an entity
        :param substitute: Substitution to be applied
        :param variable: Variable to be replaced
        """

    @abstractmethod
    def is_less_specific(self, other: 'FirstOrderPredicateLogicEntity') -> bool:
        """
        Method to check specificness of entities
        :param other: Other entity instance of FirstOrderPredicateLogicEntity
        :return: Boolean flag if the current entity is more specific than the other entity
        """

    @staticmethod
    @abstractmethod
    def build(value: str) -> Optional['FirstOrderPredicateLogicEntity']:
        """
        Builder functionality for each different entity type
        :param value: String representation of the target entity
        :return: Built entity if it is possible otherwise None will be returned
        """
