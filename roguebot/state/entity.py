import logging
from ..navigation.point import Point
from .item import Item


class Entities:
    """ A collection of entity objects.
    """

    def __init__(self):
        """Create a blank set of entities.
        """
        self._entities_by_id = {}
        self._entities_by_position = {}
        self._logger = logging.getLogger(__name__)

    @classmethod
    def from_wire_format(cls, raw_entity_list_input):
        """Create entities given the json from the network.
        """
        entities = Entities()
        for raw_entity_input in raw_entity_list_input:
            entity = Entity.from_wire_format(raw_entity_input)
            entities.add(entity)
        return entities

    def add(self, entity):
        if entity is not None:
            self._entities_by_id[entity.entity_id] = entity
            self._add_entity_to_position(entity, entity.position)

    def delete(self, entity):
        self._logger.debug("Entity to delete: %s", entity)
        if entity is not None:
            identifier = entity.entity_id
            position = entity.position
            entities_at_same_position = self._entities_by_position.get(
                position, [])

            for entity_to_delete in entities_at_same_position:
                if entity_to_delete.entity_id == identifier:
                    self._entities_by_position.pop(position)

            self._entities_by_id.pop(identifier)

    def update(self, entity):
        """An entity needs to be replaced with a different version of
        that same entity.
        """
        if entity is not None:
            identifier = entity.entity_id
            self._logger.debug("Entity to update:%s", identifier)
            old_entity = self.get_by_id(identifier)
            self.delete(old_entity)
            self.add(entity)

    def delete_at_position(self, position: Point):
        """Delete whatever entity is currently at a specific position.
        """
        entities_at_same_position = self._entities_by_position.get(
            position, [])
        for entity_to_delete in entities_at_same_position:
            self._entities_by_position.pop(position)
            self._entities_by_id.pop(entity_to_delete.entity_id)

    def delete_by_id(self, identifier: str) -> None:
        """Delete the entity with the specified identifier."
        """
        old_entity = self.get_by_id(identifier)
        self.delete(old_entity)

    def _add_entity_to_position(self, entity, position: Point):
        """Add the entity to the list of entities at the same position.
        """
        entities_at_same_position = self._entities_by_position.get(
            position, [])
        entities_at_same_position.append(entity)
        self._entities_by_position[position] = entities_at_same_position

    def _remove_entity_from_position(self, entity, position):
        entities_at_same_position = self._entities_by_position.get(
            position, [])
        entities_at_same_position.remove(entity)
        self._entities_by_position[position] = entities_at_same_position

    def __str__(self):
        result = "Entities("
        for key in self._entities_by_id.keys():
            result = result + " " + \
                str(key) + ":" + str(self._entities_by_id[key])
        result += " )"
        return result

    def get_all(self):
        return self._entities_by_id.values()

    def get_by_id(self, identifier):
        return self._entities_by_id.get(identifier, None)

    def get_by_position(self, point):
        """Returns a list of entities found at the specific point.
        """
        return self._entities_by_position.get(point, [])

    def __len__(self):
        return len(self._entities_by_id)

    def update_position(self, identifier, new_position):
        entity_to_update = self.get_by_id(identifier)
        self._remove_entity_from_position(
            entity_to_update, entity_to_update.position)
        entity_to_update.position = new_position
        self._add_entity_to_position(entity_to_update, new_position)


class Entity:
    """Something which thinks, possible is alive, maybe moves...etc.

    eg: A player, a bot, a monster.
    """

    def __init__(self, char, name, position, identifier,
                 alive=True,
                 inventory=None,
                 current_weapon=None,
                 armour_class=10,
                 hit_points=10,
                 current_armour=None,
                 hunger=0
                 ):
        """Create an entity with the attributes we care about .
        """
        self._char = char
        self._name = name
        self._position = position
        self._identifier = identifier
        self._alive = alive
        if inventory is None:
            self._inventory = []
        else:
            self._inventory = inventory
        self._current_weapon = current_weapon
        self._armour_class = armour_class
        self._hit_points = hit_points
        self._current_armour = current_armour
        self._hunger = hunger

    @property
    def identifier(self) -> str:
        return self._identifier

    @classmethod
    def from_wire_format(cls, raw_entity_input):
        """
        Create an entity from the raw network format.
        """
        char = raw_entity_input['char']
        name = raw_entity_input['name']
        position = Point.from_dictionary(raw_entity_input['pos'])
        identifier = raw_entity_input['id']
        alive = raw_entity_input['alive']
        hunger = raw_entity_input['hunger']

        # Inventory is a list of items.
        inventory = cls.parse_inventory(raw_entity_input)

        # Current weapon is an item
        # (which is a duplicate of something in the inventory)
        current_weapon = cls.parse_current_weapon(raw_entity_input)

        armour_class = int(raw_entity_input.get('ac', 10))
        hit_points = int(raw_entity_input.get('hp', 10))

        # Current armour is an item.
        # (which is a duplicate of something in the inventory)
        current_armour = cls.parse_current_armour(raw_entity_input)

        return Entity(char, name, position, identifier, alive,
                      inventory=inventory,
                      current_weapon=current_weapon,
                      armour_class=armour_class,
                      hit_points=hit_points,
                      current_armour=current_armour,
                      hunger=hunger
                      )

    @classmethod
    def parse_current_armour(cls, raw_entity_input: dict) -> Item:
        raw_current_armour = raw_entity_input.get('currentArmour', None)
        current_armour = None
        if raw_current_armour is not None:
            current_armour = Item.from_wire_format(raw_current_armour)
        return current_armour

    @classmethod
    def parse_current_weapon(cls, raw_entity_input: dict) -> Item:
        raw_current_weapon = raw_entity_input.get('currentWeapon', None)
        current_weapon = None
        if raw_current_weapon is not None:
            current_weapon = Item.from_wire_format(raw_current_weapon)
        return current_weapon

    @classmethod
    def parse_inventory(cls, raw_entity_input: dict) -> [Item]:
        raw_inventory = raw_entity_input.get('inventory', [])
        inventory = []
        for raw_item in raw_inventory:
            item = Item.from_wire_format(raw_item)
            inventory.append(item)
        return inventory

    def __str__(self):
        result = "Entity("
        result += "identifier="+self._identifier
        result += " name=" + self._name
        result += " char="+self._char
        result += " position="+str(self._position)
        result += " hit points="+str(self.hit_points)
        result += " weapon="+str(self._current_weapon)
        result += " inventory="+str(self._inventory)
        result += " armour="+str(self._current_armour)
        result += " hunger="+str(self._hunger)
        result += ")"
        return result

    def __repr__(self):
        return str(self)

    @ property
    def armour_class(self):
        """ The armor class. 10 = normal clothes. Full plate-mail might
        be closer to 0, or negative. Lower is good.
        """
        return self._armour_class

    @ property
    def current_armour(self):
        """ A piece of armour if we are wearing it, or None.
        Armour can make your armour-class (ac) better/lower,
        which makes it harder for enemies to hit you.
        """
        return self._current_armour

    @ current_armour.setter
    def current_armour(self, new_armour):
        """ sets the current armour being worn
        """
        self._current_armour = new_armour

    @ property
    def hit_points(self):
        """ The amount of damage this entity can take before it dies
        The higher the number the better.
        """
        return self._hit_points

    @ property
    def char(self):
        """ How does this entity look on the map to others in a UI ? """
        return self._char

    @ property
    def current_weapon(self):
        """ This will be None if the entity isn't wielding anything,
        otherwise it will be a weapon which is also appearing in their
        inventory.
        """
        return self._current_weapon

    @ current_weapon.setter
    def current_weapon(self, weapon):
        """ Start wielding a weapon
        """
        self._current_weapon = weapon

    @ property
    def hunger(self):
        """ What is the hunger value for this entity?
        """
        return self._hunger

    @ hunger.setter
    def hunger(self, hunger):
        """ Set the hunger value for this entity
        """
        self._hunger = hunger

    @ property
    def name(self):
        """ Names don't have to be unique.
        """
        return self._name

    @ property
    def position(self) -> Point:
        """ Where are we in the dungeon ?
        """
        return self._position

    @ position.setter
    def position(self, position: Point):
        """ set where we are in the dungeon
        """
        self._position = position

    @ property
    def entity_id(self) -> str:
        """ The unique identifier for the entity.
        """
        return self._identifier

    @ property
    def alive(self) -> bool:
        """ Is this entity alive ?
        """
        return self._alive

    @ property
    def inventory(self) -> [Item]:
        """ A list of things being carried. """
        return self._inventory
