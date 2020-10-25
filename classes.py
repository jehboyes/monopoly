import random


class Board(object):
    """
    Monopoly board object

    Contains description of board, and handles consequences of dice rolls 
    via the move method. Plan is to add more detail on the actual squares, and better 
    logging & capacity for tweaking, hence it being overcomplicated for the initial use. 
    """

    def __init__(self):
        self.space_log = {i+1: 0 for i in range(40)}
        # setup board landing consequences
        self.landing = {i+1: self._property for i in range(40)}
        special = {3: self._land_community_chest,
                   8: self._land_chance,
                   18: self._land_community_chest,
                   23: self._land_chance,
                   31: self._to_jail,
                   34: self._land_community_chest,
                   37: self._land_community_chest}
        self.landing.update(special)
        self._community_chest = []

    def reset_board(self, players):
        """
        Reset the game board

        Setup the community chest and chance decks as alphanumeric keys; 
        letters indicate special actions, whilst numbers are changes to the player's balance
        """
        community_chest = ['A', 200, -50, 50, 'F', 'G', 50,
                           100, 20, 10, 100, -100, -150, 25, 0, 10, 100]
        chance = ['A', 'M26', 'M12', 'U', 'R', 50, 'F',
                  'B', 'G', 0, -15, 'M6', 'M40', 'C', 150, 100]
        self._community_chest = Deck(community_chest)
        self._chance = Deck(chance)
        self._players = players

    def move(self, character, distance):
        destination = (character.position + distance) % 40
        destination = 40 if destination == 0 else destination
        # Check for passing go
        if destination < character.position:
            character.cash += 200
        # Move
        self._reposition(character, destination)
        self.landing[destination](character, destination)

    def _reposition(self, character, position):
        self.space_log[position] += 1
        character.position = position

    def three_double_jail(self, character):
        self._to_jail(character)

    def _to_jail(self, character, position=None):
        self._reposition(character, 11)
        character.gaoled = True

    def _land_community_chest(self, character, position):
        self._resolve_deck(character, position, self._community_chest)

    def _land_chance(self, character, position):
        self._resolve_deck(character, position, self._chance)

    def _resolve_deck(self, character, position, deck):
        card = deck.draw()
        repl = True
        if isinstance(card, int):  # simple cash change
            character.cash = + card
        elif card == 'A':  # Advance to go
            advance = 41-character.position
            self.move(character, advance)
        elif card == 'B':
            self.move(character, -3)
        elif card == 'C':
            loss = (len(self._players)-1) * 50
            character.cash -= loss
        elif card == 'F':
            character.goj += 1
            repl = False
        elif card == 'G':
            self._to_jail(character)
        elif card == 'R':
            self._advance_to(character, [6, 16, 26, 36])
        elif card == 'U':
            self._advance_to(character, [13, 29])
        elif card[0] == 'M':
            self._advance_to(character, [int(card[1:])])
        else:
            raise ValueError(f"Unrecognised card {card}")
        if repl:
            deck.replace(card)

    def _advance_to(self, character, positions):
        """
        Finds number of spaces needed to advance character to position
        """
        i = 0
        if 40 in positions:
            positions.remove(40)
            positions.append(0)
        while (i + character.position) % 40 not in positions:
            i += 1
            if i > 40:
                raise ValueError(
                    "Increment too high - impossible destination passed?")
        self.move(character, i)

    def _property(self, character, position):
        pass

    def _nothing(self, character, position):
        pass


class Card(object):
    """
    Generic base class for card
    """

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.owner = None

    def set_ownership(self, player):
        self.owner = player


class PropertyCard(Card):
    """
    Extension of card class for properties

    Not yet used
    """

    def __init__(self, name, price, colour):
        super().__init__(name, category="property")
        self.price = price
        self.colour = colour


class Player(object):

    def __init__(self):
        self.cash = 1_500
        self.position = 1
        self.cards = []
        self.goj = 0
        self.gaoled = False
        self.walk_history = []

    def check_out_of_jail(self):
        if self.goj > 1:
            self.goj -= 1
            return True
        else:
            return False

    def moved_to(self, position):
        self.walk_history.append(position)


class Deck(object):
    """
    Deck of cards

    Used for chance and community chest 
    """

    def __init__(self, effects):
        self.deck = effects
        random.shuffle(self.deck)

    def draw(self, replacement=True):
        card = self.deck[0]
        self.deck.remove(card)
        return card

    def replace(self, card):
        self.deck.append(card)
