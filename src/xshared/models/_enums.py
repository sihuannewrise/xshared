from enum import Enum


class CounterpartyType(str, Enum):
    LEGAL = "LEGAL"
    INDIVIDUAL = "INDIVIDUAL"


class EntityStatus(str, Enum):
    ACTIVE = "ACTIVE"
    LIQUIDATING = "LIQUIDATING"
    LIQUIDATED = "LIQUIDATED"
    BANKRUPT = "BANKRUPT"
    REORGANIZING = "REORGANIZING"


class CounterpartyBranch(str, Enum):
    MAIN = "MAIN"
    BRANCH = "BRANCH"
