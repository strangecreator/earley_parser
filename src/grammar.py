from __future__ import annotations

from exception import InputError


class Grammar:
    @staticmethod
    def is_nonterminal(symbol: str):
        return ord('A') <= ord(symbol) <= ord('Z')
    
    @staticmethod
    def is_terminal(symbol: str):
        return not Grammar.is_nonterminal(symbol) and symbol != ' '

    class Rule:
        nonterminal: str
        generation: str

        def __init__(self, nonterminal: str, generation: str = '') -> None:
            self.nonterminal = nonterminal.strip()
            self.generation = generation.strip()

        def _validate(self, nonterminal_symbols: set[str], terminal_symbols: set[str]) -> None:
            if len(self.nonterminal) != 1 or self.nonterminal not in nonterminal_symbols:
                raise InputError(f"Left side of the rule must be one nonterminal symbol (got: '{self.nonterminal}')!")
            for symbol in self.generation:
                if symbol not in terminal_symbols and symbol not in nonterminal_symbols:
                    raise InputError(f"'{symbol}' symbol is not listed as either terminal or nonterminal!")
            
        def __str__(self) -> str:
            return self.nonterminal + " -> " + (self.generation if self.generation else 'ε')
        
        def __repr__(self) -> str:
            return f"Rule('{self.__str__()}')"

        def __hash__(self) -> int:
            return hash((self.nonterminal, self.generation))

        @classmethod
        def read(cls, content: str) -> Grammar.Rule:
            content_splitted = list(map(lambda x: x.strip(), content.strip().replace(' ', '').split("->")))
            if not 1 <= len(content_splitted) <= 2:
                raise InputError("Incorrect length of the rule!")
            return cls(*content_splitted)

    nonterminal_symbols = set()
    terminal_symbols = set()

    rules: list[Rule] = []
    start_symbol: str = 'S'

    def __init__(self, nonterminal_symbols: set[str], terminal_symbols: set[str],\
                 rules: list[Rule], start_symbol: str) -> None:
        self.nonterminal_symbols = nonterminal_symbols
        self.terminal_symbols = terminal_symbols
        self.rules = rules
        self.start_symbol = start_symbol.strip()
        # validation
        self._validate()

    def _validate(self) -> None:
        # checking nonterminal symbols
        for symbol in self.nonterminal_symbols:
            if not Grammar.is_nonterminal(symbol):
                raise InputError(f"'{symbol}' symbol is not nonterminal!")
        # checking terminal symbols
        for symbol in self.terminal_symbols:
            if not Grammar.is_terminal(symbol):
                raise InputError(f"'{symbol}' symbol is not terminal!")
        # checking rules
        for rule in self.rules:
            rule._validate(self.nonterminal_symbols, self.terminal_symbols)
        # checking start symbol
        if len(self.start_symbol) != 1 or self.start_symbol not in self.nonterminal_symbols:
            raise InputError("Start symbol must be one nonterminal symbol!")
        
    def __str__(self) -> str:
        rules = '\n'.join(map(str, self.rules))
        result = (
            "------- Grammar -------\n"
            "\033[34mRules:\033[0m\n"
            f"{rules}\n"
            f"\033[34mStart symbol:\033[0m {self.start_symbol}\n"
            "-----------------------\n"
        )
        return result

    def check_word(self, word: str) -> bool:
        for symbol in word:
            if symbol not in self.terminal_symbols:
                return False
        return True

    @classmethod
    def read(cls, content: str) -> tuple[Grammar, str]:
        lines = list(filter(lambda x: x, map(lambda x: x.strip(), content.strip().split('\n'))))
        number_of_nonterminal, number_of_terminal, number_of_rules = map(int, lines[0].split())
        if len(lines) < number_of_rules + 4:
            raise InputError(f"Not enough lines are there!")
        if len(lines[1]) != number_of_nonterminal:
            raise InputError(f"Suggested number of nonterminal symbols differ with actual number!")
        if len(lines[2]) != number_of_terminal:
            raise InputError(f"Suggested number of terminal symbols differ with actual number!")
        nonterminal_symbols = set(lines[1])
        terminal_symbols = set(lines[2])
        rules = []
        for i in range(number_of_rules):
            rules.append(Grammar.Rule.read(lines[i + 3]))
        start_symbol = lines[number_of_rules + 3].strip()
        return (
            Grammar(
                nonterminal_symbols,
                terminal_symbols,
                rules,
                start_symbol
            ),
            '\n'.join(lines[number_of_rules + 4:])
        )
