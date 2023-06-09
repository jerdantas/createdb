from typing import List

from lex.token import Token
from lex.token_type import TokenType
from lex.scanner import Scanner

_comparator = {TokenType.LT, TokenType.LE, TokenType.EQ, TokenType.GE, TokenType.GT}


def _show_error(text: str, pos: int):
    print(text)
    white = ''
    for i in range(pos-1):
        white += ' '

    white += '^'
    print(white)


class AnalyseRule:
    def __init__(self, line: str, lineno: int, cat_list: dict[str, int]):
        self.name = ''
        self.category_name = ''
        self.rule_def = ''
        self.scan = Scanner(line)
        self.lineno = lineno
        self.token = Token('', TokenType.INVALID, '')
        self.cat_list = cat_list

    def analyse(self) -> bool:
        """
        exp -> trm OR trm | trm
        trm -> fat AND fat | fat
        fat -> NOT cmp | ( exp ) | cmp
        cmp -> WORD opc INT
        opc -> < | <= | = | >= | >
        """
        self.token = self.scan.next_token()
        if self.token.token_type != TokenType.WORD:
            _show_error(self.scan.code, self.token.col)
            print(f'Expected rule name. Line {self.lineno}, column {self.token.col}')
            return False
        self.name = self.token.text

        self.token = self.scan.next_token()
        if self.token.token_type != TokenType.WORD and self.token.token_type != TokenType.STAR:
            _show_error(self.scan.code, self.token.col)
            print(f'Second element must be category name or *. Line {self.lineno}, column {self.token.col}')
            return False
        self.category_name = self.token.text if self.token.token_type != TokenType.STAR else None
        if self.token.token_type == TokenType.WORD:
            if self.category_name not in self.cat_list.keys():
                print(f'Undefined category {self.category_name}. Line {self.lineno}, column {self.token.col}')
                return False
            self.token.value = str(self.cat_list[self.category_name])
        self.token = self.scan.next_token()

        if self._expression():
            if self.token.token_type != TokenType.EOT:
                _show_error(self.scan.code, self.token.col)
                print(f'Invalid syntax. Line {self.lineno}, column {self.token.col}')
                return False
            return True
        return False

    def _expression(self) -> bool:
        if not self._term():
            return False

        if self.token.token_type == TokenType.EOT:
            return True

        while self.token.token_type == TokenType.OR:
            self.rule_def += ' ' + self.token.text + ' '

            self.token = self.scan.next_token()
            if not self._term():
                return False

        return True

    def _term(self) -> bool:
        if not self._factor():
            return False

        if self.token.token_type == TokenType.EOT:
            return True

        while self.token.token_type == TokenType.AND:
            self.rule_def += ' ' + self.token.text + ' '
            self.token = self.scan.next_token()

            if not self._factor():
                return False

        return True

    def _factor(self) -> bool:
        if self.token.token_type == TokenType.LPAR:
            self.rule_def += self.token.text
            self.token = self.scan.next_token()
            if not self._expression():
                return False

            if self.token.token_type != TokenType.RPAR:
                _show_error(self.scan.code, self.token.col)
                print(f'Expected right parenthesis. Line {self.lineno}, column {self.token.col}')
                return False
            self.rule_def += self.token.text
            self.token = self.scan.next_token()

            return True

        while self.token.token_type == TokenType.NOT:
            self.rule_def += ' ' + self.token.text + ' '
            self.token = self.scan.next_token()

        return self._comparison()

    def _comparison(self) -> bool:
        if self.token.token_type != TokenType.WORD:
            _show_error(self.scan.code, self.token.col)
            print(f'Expected category name. Line {self.lineno}, column {self.token.col}')
            return False
        if self.token.text not in self.cat_list.keys():
            print(f'Undefined category {self.token.text}. Line {self.lineno}, column {self.token.col}')
            return False
        self.token.value = str(self.cat_list[self.token.text])
        self.rule_def += self.token.text

        self.token = self.scan.next_token()
        if self.token.token_type not in _comparator:
            _show_error(self.scan.code, self.token.col)
            print(f'Expected comparator. Line {self.lineno}, column {self.token.col}')
            return False
        self.rule_def += self.token.text

        self.token = self.scan.next_token()
        if self.token.token_type != TokenType.INT:
            _show_error(self.scan.code, self.token.col)
            print(f'Expected integer value. Line {self.lineno}, column {self.token.col}')
            return False
        self.rule_def += self.token.text

        self.token = self.scan.next_token()

        return True
