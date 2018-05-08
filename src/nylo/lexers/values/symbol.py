# This file is a part of nylo
#
# Copyright (c) 2018 The nylo Authors (see AUTHORS)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from nylo.lexers.lexer import Lexer
from nylo.objects.values.symbol import Symbol as SymObj
from nylo.objects.values.value import Value as ValObj
from nylo.objects.struct.struct import Struct
from nylo.objects.struct.call import Call


class Symbol(Lexer):
    """Symbol class is used to
    define all keywords (e.g. ``+``, ``-``, etc..) and to
    evaluate all their uses (ex. `'1 + 1``)."""

    unary_symbols = '+', '-', 'not '
    symbols = ('=', 'and ', '>', 'or ', '<', '!=', 'xor ', '>=',
               '<=', '..', 'in ', '*', '+-', '/', '^', '|', '%',
               '&', '.') + unary_symbols
    to_avoid = ('->',)
    symbols_priority = (
        ('|',),
        ('and', 'or'),
        ('=', '!=', '>=', '<=', 'in'),
        ('..', '%'),
        ('+', '-', '&'),
        ('*', '/'),
        ('^', '+-'),
        ('.',)
    )

    def lexe(self, reader):
        """It generates all characters
        associated to the token.

        Args:
            reader (Reader): The reader you're going to use.

        Returns:
            generator: All characters associated to the token.
        """
        from nylo.lexers.values.value import Value
        if not reader.any_starts_with(self.unary_symbols):
            yield Value(reader).value
        if (not reader.any_starts_with(self.symbols)
                or reader.any_starts_with(self.to_avoid)):
            return
        self.symbol = reader.any_starts_with(self.symbols)
        reader.move(len(self.symbol))
        yield Symbol(reader).value
        yield self.symbol

    def parse(self, reader):
        """It returns all lexer characters using
        an object.

        Args:
            reader (Reader): The reader you're going to use

        Returns:
            ValueObj: The lexer characters object
        """
        *values, symbol = list(self.lexe(reader))
        if len(values) == 0:
            return symbol
        newobj = SymObj(symbol, values)
        if isinstance(values[1], SymObj):
            if self.priority(symbol) > self.priority(values[1].value):
                otherobj = newobj.args[1]
                otherobj.args[0], newobj.args[1] = newobj, otherobj.args[0]
                newobj = otherobj
        return newobj

    def priority(self, symbol):
        for index, value in enumerate(self.symbols_priority):
            if symbol in value:
                return index
