from __future__ import annotations
from copy import deepcopy

from grammar import Grammar


START_SYMBOL = '$'


class Situation:
    rule: Grammar.Rule
    index: int
    left: int

    def __init__(self, rule: Grammar.Rule, index: int, left: int) -> None:
        self.rule = rule
        self.index = index
        self.left = left

    def is_able_to_complete(self) -> bool:
        return len(self.rule.generation) == self.index

    def get_next_symbol(self) -> str:
        if self.is_able_to_complete():
            return ''
        return self.rule.generation[self.index]
    
    def is_next_nonterminal(self) -> bool:
        next_symbol = self.get_next_symbol()
        return next_symbol != '' and Grammar.is_nonterminal(next_symbol)

    def is_next_terminal(self) -> bool:
        next_symbol = self.get_next_symbol()
        return next_symbol != '' and Grammar.is_terminal(next_symbol)

    def get_next_situation(self) -> Situation:
        if self.is_able_to_complete():
            raise Exception("Situation is already at the end! (cannot get next situation)")
        return Situation(self.rule, self.index + 1, self.left)

    def __hash__(self) -> int:
        return hash((self.rule, self.index, self.left))

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Situation) and hash(self) == hash(__value)

    def __str__(self) -> str:
        generation_with_point = self.rule.generation[:self.index] + '⋅' + self.rule.generation[self.index:]
        return f"[{self.rule.nonterminal} -> {generation_with_point}, {self.left}]"

    def __repr__(self) -> str:
        return f"Situation({str(self)})"


class Earley:
    grammar: Grammar
    previous_start_symbol: str

    def __init__(self, grammar: Grammar, previous_start_symbol: str) -> None:
        self.grammar = grammar
        self.previous_start_symbol = previous_start_symbol

    def _scan(self, layers: list[set[Situation]], layer_index: int, word: str) -> set[Situation]:
        # O(n) in the worst case
        if layer_index == 0:
            return set()
        result: set[Situation] = set()
        for situation in layers[layer_index - 1]:
            if situation.is_next_terminal() and situation.get_next_symbol() == word[layer_index - 1]:
                result.add(situation.get_next_situation())
        return result

    def _predict(self, layers: list[set[Situation]], layer_index: int) -> set[Situation]:
        result: set[Situation] = set()
        # O(n) in the worst case
        for situation in layers[layer_index]:
            if not situation.is_next_nonterminal():
                continue
            nonterminal: str = situation.get_next_symbol()
            # O(1), because grammar is constant
            for rule in self.grammar.rules:
                if nonterminal == rule.nonterminal:
                    # layers[layer_index].add(new_situation)
                    result.add(Situation(rule, 0, layer_index))
        return result - layers[layer_index]

    def _complete_by_situation(self, layers: list[set[Situation]], layer_index: int, complete_situation: Situation) -> set[Situation]:
        if not complete_situation.is_able_to_complete():
            return set()
        result: set[Situation] = set()
        # O(n) in the worst case
        for situation in layers[complete_situation.left]:
            if situation.get_next_symbol() == complete_situation.rule.nonterminal:
                result.add(situation.get_next_situation())
        return result - layers[layer_index]

    def _complete(self, layers: list[set[Situation]], layer_index: int, new_situations: set[Situation]) -> set[Situation]:
        result: set[Situation] = set()
        # O(n^2) in the worst case
        for situation in new_situations:
            result |= self._complete_by_situation(layers, layer_index, situation)
        return result - layers[layer_index]

    def predict(self, word: str) -> bool:
        word = word.strip()
        length: int = len(word)
        # creation of the layers
        layers: list[set[Situation]] = [set() for _ in range(length + 1)]
        # adding start situation to the zero layer
        start_situation = Situation(Grammar.Rule('$', self.previous_start_symbol), 0, 0)
        layers[0].add(start_situation)
        #
        new_situations: set[Situation] = set()
        for j in range(length + 1):
            # scan
            layers[j] |= self._scan(layers, j, word)
            # other
            previously_added_situations: set[Situation] = layers[j].copy()
            new_situations: set[Situation] = set()
            while True:
                # complete only new situations to reduce O(n^2) to O(n) amortized
                new_situations = self._complete(layers, j, previously_added_situations)
                # complete all situations with predefined type (left == j)
                for rule in self.grammar.rules:
                    situation = Situation(rule, len(rule.generation), j)
                    if situation in layers[j]:
                        new_situations |= self._complete_by_situation(layers, j, situation)
                layers[j] |= new_situations
                # predict
                new_situations |= self._predict(layers, j)
                # changing
                previously_added_situations = new_situations.copy()
                layers[j] |= new_situations
                # checking
                if len(new_situations) == 0:
                    break

        # checking if end situation is in the last layer
        end_situation = Situation(Grammar.Rule('$', self.previous_start_symbol), 1, 0)
        return end_situation in layers[length]

    @classmethod
    def fit(cls, grammar: Grammar) -> Earley:
        grammar = deepcopy(grammar)
        previous_start_symbol: str = grammar.start_symbol
        grammar.rules.append(Grammar.Rule('$', previous_start_symbol))
        grammar.start_symbol = '$'
        return cls(grammar, previous_start_symbol)
