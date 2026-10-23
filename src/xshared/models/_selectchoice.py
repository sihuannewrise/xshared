from enum import Enum

import pydantic.json


class EnumByName(Enum):
    """
    A custom Enum type for pydantic to validate by name.
    """
    pydantic.json.ENCODERS_BY_TYPE[Enum] = lambda e: e.name

    @classmethod
    def __get_validators__(cls):
        yield cls._validate

    @classmethod
    def __modify_schema__(cls, schema):
        """Override pydantic using Enum.name for schema enum values"""
        schema['enum'] = list(cls.__members__.keys())

    @classmethod
    def _validate(cls, v):
        try:
            if v in cls:
                return v
        except TypeError:
            pass

        try:
            return cls[v]
        except KeyError:
            name = cls.__name__
            expected = list(cls.__members__.keys())
            raise ValueError(
                f'{v} not found for enum {name}. Expected one of: {expected}')


class CounterpartyType(str, EnumByName):
    LEGAL = 'юридическое лицо'
    INDIVIDUAL = 'индивидуальный предприниматель'


class EntityStatus(str, EnumByName):
    ACTIVE = 'действующая'
    LIQUIDATING = 'ликвидируется'
    LIQUIDATED = 'ликвидирована'
    BANKRUPT = 'банкротство'
    REORGANIZING = ('в процессе присоединения к другому юрлицу, '
                    'с последующей ликвидацией')


class CounterpartyBranch(str, EnumByName):
    MAIN = 'головная организация'
    BRANCH = 'обособленное подразделение'
