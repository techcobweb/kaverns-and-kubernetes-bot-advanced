import unittest
import pytest

from roguebot.state.dungeon_map import DungeonMap
from roguebot.brains.ibrain import IBrain
from roguebot.brains.item_handling_brain import ItemHandlingBrain
from roguebot.navigation.point import Point
from roguebot.navigation.direction import Direction
from roguebot.state.entity import Entities, Entity
from assertpy import assert_that
from roguebot.state.item import Item, Items
from roguebot.action import *
from tests.state.dungeon_draw import *
from roguebot.state.state import State
from roguebot.action import Action, TakeAction


@pytest.fixture
def fred() -> Entity:
    return Entity(char="@", name="fred", position=Point(1, 1, 0), identifier="fredID", alive=True, inventory=list())


@pytest.fixture
def small_prison_cell(fred) -> State:
    dungeon_picture = """
            ----------- level z=0 :
            ###
            # #
            ###
            -----------
            """

    entrance_point = Point(99, 99, 99)

    state = State()

    state.dungeon_map = get_dungeon_from_picture(
        dungeon_picture, entrance=entrance_point)

    state.my_entity_id = fred.entity_id

    entities = Entities()
    entities.add(fred)
    state.entities = entities

    state.items = Items()

    return state


@pytest.fixture
def brain():
    return ItemHandlingBrain()


@pytest.fixture
def mud():
    """A pretty useless item. We should not bother 
    picking it up.
    """
    return Item(Point(1, 1, 0), "mud", edible=False,
                wieldable=False, wearable=False)


@pytest.fixture
def pear():
    return Item(Point(1, 1, 0), "pear",
                edible=True, wieldable=False, wearable=False)


@pytest.fixture
def hat() -> Item:
    return Item(Point(1, 1, 0), "hat",
                edible=False, wieldable=False, wearable=True, armour_class=9)


@pytest.fixture
def chainmail() -> Item:
    return Item(Point(1, 1, 0), "chainmail",
                edible=False, wieldable=False, wearable=True, armour_class=5)


@pytest.fixture
def cloak() -> Item:
    return Item(Point(1, 1, 0), "cloak",
                edible=False, wieldable=False, wearable=True, armour_class=8)


@pytest.fixture
def sword() -> Item:
    return Item(position=Point(0, 0, 0), name="sword",
                edible=False, wieldable=True, wearable=False, damage=6)


@pytest.fixture
def coin() -> Item:
    return Item(Point(1, 1, 0), "coin",
                edible=False, wieldable=False, wearable=False)


@pytest.fixture
def dagger() -> Item:
    return Item(position=Point(0, 0, 0), name="dagger",
                edible=False, wieldable=True, wearable=False, damage=2)


def test_eat_food_in_inventory_when_hungry(small_prison_cell, brain, pear):
    state = small_prison_cell

    me = state.find_my_entity()
    me.hunger = 5

    me.inventory.append(pear)

    actions = brain.decide_actions(state)

    assert_that(actions).is_length(1)
    assert_that(actions[0].action_code).is_equal_to(ActionCode.EAT)
    assert_that(actions[0].item_name).is_equal_to("pear")


def test_dont_eat_food_in_inventory_when_not_hungry(small_prison_cell, brain, pear):
    state = small_prison_cell
    me = state.find_my_entity()
    me.inventory.append(pear)

    actions = brain.decide_actions(state)

    assert_that(actions).is_length(0)


def test_takes_item_if_stood_on_it(small_prison_cell, brain, sword):

    item_to_pick_up = sword
    state = small_prison_cell
    state.items.add_item_to_position(item_to_pick_up, Point(1, 1, 0))

    actions = brain.decide_actions(state)

    assert_that(actions).is_length(1)
    assert_that(actions[0].action_code).is_equal_to(ActionCode.TAKE)
    assert_that(actions[0].item_name).is_equal_to("sword")


def test_wears_item_if_wearable_in_inventory(small_prison_cell, brain, hat):
    state = small_prison_cell

    me = state.find_my_entity()
    me.inventory.append(hat)

    actions = brain.decide_actions(state)

    assert_that(actions).is_length(1)
    assert_that(actions[0].action_code).is_equal_to(ActionCode.WEAR)
    assert_that(actions[0].item_name).is_equal_to("hat")


def test_doesnt_wear_item_if_wearable_one_already(small_prison_cell, brain, hat):
    state = small_prison_cell
    me = state.find_my_entity()
    me.inventory.append(hat)
    me.current_armour = hat

    actions = brain.decide_actions(state)

    # We expect them not to do anyting.
    assert_that(actions).is_length(0)


def test_swaps_armour_if_has_better_available(small_prison_cell, brain, hat, chainmail, cloak):
    state = small_prison_cell
    me = state.find_my_entity()

    me.inventory.append(hat)
    me.inventory.append(chainmail)
    me.inventory.append(cloak)
    me.current_armour = hat

    actions = brain.decide_actions(state)

    # We expect them not to do anyting.
    assert_that(actions).is_length(1)
    assert_that(actions[0].action_code).is_equal_to(ActionCode.WEAR)
    assert_that(actions[0].item_name).is_equal_to("chainmail")


def test_wields_item_if_wieldable_in_inventory(small_prison_cell, brain, sword):
    state = small_prison_cell
    me = state.find_my_entity()
    me.inventory.append(sword)

    actions = brain.decide_actions(state)

    assert_that(actions).is_length(1)
    assert_that(actions[0].action_code).is_equal_to(ActionCode.WIELD)
    assert_that(actions[0].item_name).is_equal_to("sword")


def test_swaps_weapons_if_inventory_has_better_one(small_prison_cell, brain, sword, dagger):
    state = small_prison_cell
    me = state.find_my_entity()

    me.inventory.append(dagger)
    me.inventory.append(sword)
    me.inventory.append(dagger)

    # Arm ourselves with the worst weapon of the two.
    me.current_weapon = dagger

    actions = brain.decide_actions(state)

    assert_that(actions).is_length(2)
    # We expect Wield None to free up our hands.
    assert_that(actions[0].action_code).is_equal_to(ActionCode.WIELD)
    assert_that(actions[0].item_name).is_none()
    # We next expect a wield sword action.
    assert_that(actions[1].action_code).is_equal_to(ActionCode.WIELD)
    assert_that(actions[1].item_name).is_equal_to("sword")


def test_does_not_wield_item_if_wielding_one_already(small_prison_cell, brain, sword, dagger):
    state = small_prison_cell
    me = state.find_my_entity()
    me.inventory.append(sword)
    me.current_weapon = sword

    actions = brain.decide_actions(state)

    assert_that(actions).is_length(0)


def test_does_not_take_item_if_it_is_worthless(small_prison_cell, brain, mud):
    state = small_prison_cell
    state.items.add_item_to_position(mud, Point(1, 1, 0))

    actions = brain.decide_actions(state)

    # Should not bother picking up the mud.
    assert_that(actions).is_length(0)
