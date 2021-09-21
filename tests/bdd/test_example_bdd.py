from pytest_bdd import scenario, given, when, then, parsers
from pytest import fixture
from assertpy import assert_that

@scenario('features/example.feature', 'Demo roguelike client')
def test_arguments_for_given_when_thens():
    """Demo roguelike client"""

@fixture
def dungeon():
    return set()


@given('an empty inventory', target_fixture="inventory")
def an_empty_inventory():
    return []

@given(parsers.parse('the dungeon contains a {item}'))
def the_dungeon_contains(dungeon, item):
    dungeon.add(item)


@when('I enter the dungeon', target_fixture="client")
def i_enter_the_dungeon(dungeon):
    # would return some connection object in reality
    conn = dict(connected=True, initial_items=len(dungeon))
    return conn


@when(parsers.parse('I pick up the {item}'))
def i_pick_up_the_sword(client, dungeon, inventory, item):
    if client['connected'] and item in dungeon:
            inventory.append(item)
            dungeon.remove(item)


@then(parsers.parse('I should have {num:d} items in my inventory'))
def i_should_have_1_items_in_my_inventory(dungeon, client, inventory, num):
    assert_that(len(inventory)).is_equal_to(num)
    assert_that(client['initial_items'] - len(inventory)).is_equal_to(len(dungeon))