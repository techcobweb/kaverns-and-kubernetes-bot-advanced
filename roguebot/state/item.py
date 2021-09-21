
"""
Items are useful, some more than others.

Take them, put them into your inventory, wield them, eat them, wear them or drop them.
"""
from ..navigation.point import Point


class Item:
    """An item. Some can be eaten, word or wielded.
    """

    def __init__(self, position=Point(1, 1, 0), name="unknown", edible=False, wieldable=False, wearable=False, damage=0, armour_class=10):
        self._position = position
        self._name = name
        self._edible = edible
        self._wieldable = wieldable
        self._wearable = wearable
        self._damage = damage
        self._armour_class = armour_class

    @classmethod
    def from_wire_format(cls, raw_data):
        """Parse an item from raw data.

        An example:

        {'char': 'o', 'foreground': 'green', 'background': 'black',
        'alive': False, 'walkable': True,
        'pos': {'x': 22, 'y': 16, 'z': 0 },
        'name': 'apple', 'details': 'it looks edible',
        'edible': True, 'wieldable': False, 'wearable': False,
        'damage': 3, 'ac:-2'
        }

        """
        position = Point.from_dictionary(raw_data['pos'])
        name = raw_data['name']
        edible = raw_data['edible']
        wieldable = raw_data['wieldable']
        wearable = raw_data['wearable']
        damage = int(raw_data.get('damage', "0"))
        armour_class = int(raw_data.get('ac', "10"))
        item = Item(position=position,
                    name=name,
                    edible=edible,
                    wieldable=wieldable,
                    wearable=wearable,
                    damage=damage,
                    armour_class=armour_class)
        # print(item)
        return item

    def __str__(self):
        return "Item (name={}, position={}, edible={}, wieldable={}, wearable={}, damage={} ac={})".format(
            self._name, str(self._position), self._edible, self._wieldable, self._wearable, self.damage, self.armour_class)

    def __repr__(self):
        return str(self)

    @ property
    def name(self) -> str:
        return self._name

    @ property
    def edible(self) -> bool:
        """Can it be eaten ?
        """
        return self._edible

    @ property
    def damage(self) -> int:
        """How much damage could it do if wielded as a weapon ?
        """
        return self._damage

    @property
    def armour_class(self) -> int:
        """
        How much protection does the clothing worn provide ?
        """
        return self._armour_class

    @ property
    def wieldable(self) -> bool:
        """Can it be used to hit someone ?
        """
        return self._wieldable

    @ property
    def wearable(self) -> bool:
        return self._wearable

    @ property
    def position(self) -> Point:
        """Where is it ?
        """
        return self._position

    @position.setter
    def position(self, new_point) -> None:
        self._position = new_point


class Items:
    """
    All the items we know about are stored here.

    The main query we get is `are there items at point x,y,z`
    So we order items into a dictionary.
    The key is the point the item(s) are at.
    The value is a list of items which are at that point.

    Sometimes we are told to update_items, which means removing all the items
    we know about on that dungeon level, and adding-in the new item list.
    """

    def __init__(self):
        """
        Create an empty collection of items.
        """
        self._items_by_position = {}

    def __str__(self):
        return str(self._items_by_position)

    def update_items(self, raw_items_data: dict, my_position: Point):
        """
        Every time we go up/down stairs, or when the status of items change,
        we get an update of all the items on this floor.

        Parameters:
            my_position (Point): tells us which floor we are on.
            raw_items_data (dict): A batch of items might look like this:

                <PRE>
                {'(22,16,0)': [
                    {'char': 'o', 'foreground': 'green', 'background': 'black',
                    'alive': False, 'walkable': True,
                    'pos': {'x': 22, 'y': 16, 'z': 0 },
                    'name': 'apple', 'details': 'it looks edible', 'edible': True,
                    'wieldable': False, 'wearable': False
                    }
                ],
                '(28, 6,0)': [
                    {'char': '*', 'foreground': 'grey', 'background': 'black',
                    'alive': False, 'walkable': True,
                    'pos': {'x': 28, 'y': 6, 'z': 0}, 'name': 'rock',
                    'details': 'igneous', 'edible': False, 'wieldable': True,
                    'wearable': False, 'damage': 2
                    }
                ]
                }
                </PRE>

                ie: It's a dict where the key is a string and the value is a list of dictionaries.
                Each value dict has a 'pos' attribute amongst other things...etc.

        Note: Multiple items can exist at the same point.
        """
        # So before we do anything else, delete all the items on this floor.
        self._delete_all_items_on_floor(my_position.z)

        # Now we can extract entity definitions from the wire form.
        items_to_add = []
        for key in raw_items_data.keys():
            items_at_this_location_raw_data = raw_items_data[key]
            for raw_item_data in items_at_this_location_raw_data:
                # print("raw_item_data:{}".format(raw_item_data))
                item = Item.from_wire_format(raw_item_data)
                items_to_add.append(item)

        for item in items_to_add:
            point = item.position
            self.add_item_to_position(item, point)

    def _delete_all_items_on_floor(self, level: int):
        """
        Remove all the items on the specific floor by just leaving them
        in the old dictionary whcih gets discarded.

        Parameters:
            level (int): The level of the dungeon we need to delete all the 
                items on, so they can be replaced.
        """
        surviving_items = {}
        for point in self._items_by_position.keys():
            if point.z != level:
                surviving_items[point] = self._items_by_position[point]
        self._items_by_position = surviving_items

    def add(self, item: Item):
        """
        Adds an item to the list of items.

        Parameters:
            item (Item): The item to add. We use the item's position to order
                where the item is of course.
        """
        self.add_item_to_position(item, item.position)

    def delete(self, item: Item):
        items_at_point = self._items_by_position.get(item.position, [])
        items_at_point.remove(item)

    def add_item_to_position(self, item: Item, point: Point):
        """
        Records that an item is associated with a position.

        Note: The item's position is also updated by this operation.
        """
        items_at_point = self._items_by_position.get(point, [])
        items_at_point.append(item)

        # print("Adding item to position {} gives us list at this point {}".format(
        #   point, items_at_point))
        self._items_by_position[point] = items_at_point

        # Let the item know it has been moved.
        item.position = point

    def get_items_at_position(self, point: Point) -> [Item]:
        """
        Gets the list of items at a specific point.

        Returns: 
            items ([Item]): the list of items at a position, or 
                an empty list if there's nothing there.
        """
        return self._items_by_position.get(point, [])

    def get_as_list(self) -> [Item]:
        """
        Get all the items we know about as a simple list.

        Returns:
            item_list ([item]): The list of items. No real sort order.
        """
        total = []
        for key in self._items_by_position.keys():
            #print("key {}".format(key))
            items_at_a_point = self._items_by_position[key]
            #print("items: {}".format(items_at_a_point))
            for item in items_at_a_point:
                total.append(item)
        return total

    def __len__(self) -> int:
        """
        How many items do we know about ?

        Returns:
            length (int): The number of items we know about.
        """
        all_items = self.get_as_list()
        return len(all_items)
