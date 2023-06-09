from lex.token_type import TokenType


class Token:
    """
    Represents a token recognized by Lexical Analyzer
    """
    def __init__(
            self,
            text: str,
            token_type: TokenType,
            value: str = '',
            line: int = 0,
            col: int = 0
    ):
        self.text = text
        self.token_type = token_type
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f'Token: Text: {self.text}, type: {self.token_type}, value: {self.value}'
