from typing import List
import re
from lex.token import Token
from lex.token_type import TokenType

_keywords = {'and': 'AND', 'or': 'OR', 'not': 'NOT'}
_token_specification = [
    ('REAL', r'\d+\.\d*'),
    ('INT', r'\d+'),
    ('LPAR', r'\('),
    ('RPAR', r'\)'),
    ('LE',   r'\<='),
    ('LT',   r'\<'),
    ('EQ',  r'='),
    ('GE', r'\>='),
    ('GT', r'\>'),
    ('WORD', r'[\_\-A-Za-z][\_\-0-9A-Za-z]*'),
    ('STAR', r'\*'),
    ('EOT', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('INVALID', r'.')
    ]
_tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in _token_specification)


class Scanner:

    def __init__(self, code):
        self.code = str.strip(code)
        self.tokenlist: List[Token] = []
        self._tokenize()
        self.token = iter(self.tokenlist)

    def next_token(self) -> Token:
        return next(self.token)
        # if len(self.tokenlist) == 0:
        #     return None
        # return self.tokenlist.pop(0)

    def _tokenize(self):
        line_num = 1
        line_start = 0
        column = 0
        for mo in re.finditer(_tok_regex, self.code):
            kind = TokenType[mo.lastgroup]
            value = mo.group()
            column = mo.start() - line_start
            if kind == TokenType.REAL:
                value = float(value)
            elif kind == TokenType.INT:
                value = int(value)
            elif kind == TokenType.WORD:
                if value in _keywords.keys():
                    kind = TokenType[_keywords[value]]
            elif kind == TokenType.EOT:
                line_start = mo.end()
                line_num += 1
            elif kind == TokenType.SKIP:
                continue
            elif kind == TokenType.INVALID:
                raise RuntimeError(f'{value!r} unexpected on line {line_num} column {column+1}')
            self.tokenlist.append(Token(mo.group(), kind, value, line_num, column+1))

        self.tokenlist.append(Token('', TokenType.EOT, '', line_num, column+1))
