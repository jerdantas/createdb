from enum import IntEnum


class TokenType(IntEnum):
    INVALID = 0
    EOT = 1
    WORD = 2
    INT = 3
    LPAR = 4
    RPAR = 5
    LT = 6
    LE = 7
    EQ = 8
    GE = 9
    GT = 10
    NE = 11
    NUMBER = 12
    AND = 13
    OR = 14
    NOT = 15
    STAR = 16
    REAL = 17
    SKIP = 50
    XVL = 100  # ('t', 'f')
