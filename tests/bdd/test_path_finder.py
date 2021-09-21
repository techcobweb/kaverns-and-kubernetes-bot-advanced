import pytest
from assertpy import assert_that
from pytest_bdd import scenario, given, when, then, parsers
from roguebot.state.entity import Entities, Entity
from roguebot.navigation.path import PathFinder
from roguebot.navigation.path_printer import PathPrinter
from roguebot.state.state import State
from tests.state.dungeon_draw import *


def path_from_picture(picture) -> [Point]:
    path = []


@scenario('features/path_finder.feature', 'finds path between rooms on same level')
def test_finds_path_between_rooms_on_same_level():
    pass


@scenario('features/path_finder.feature', 'finds path between rooms on same level in a maze')
def test_path_between_two_rooms_in_a_maze():
    pass


@scenario('features/path_finder.feature', 'finds path between through funnel')
def test_path_through_funnel():
    pass


@given(parsers.parse("a dungeon map of:{picture}"), target_fixture="dungeon_map")
def dungeon_map(picture: str):
    dungeon = get_dungeon_from_picture(picture)
    return dungeon


@given(parsers.parse("the start-point is {x:d},{y:d},{z:d}"), target_fixture="start_point")
def start_point(x: int, y: int, z: int) -> Point:
    return Point(x, y, z)


@given(parsers.parse("the end-point is {x:d},{y:d},{z:d}"), target_fixture="end_point")
def end_point(x: int, y: int, z: int) -> Point:
    return Point(x, y, z)


@pytest.fixture
def path_finder() -> PathFinder:
    return PathFinder()


@given("there are no entities", target_fixture="entities")
def no_entities() -> Entities:
    return Entities()


@pytest.fixture
def state(entities, dungeon_map) -> State:
    state = State()
    state.entities = entities
    state.dungeon_map = dungeon_map
    return state


@when("we plot a path", target_fixture="path")
def plot_a_path(state, start_point, end_point, path_finder: PathFinder):
    path = path_finder.find_path(start_point, end_point, state)
    return path


@pytest.fixture
def path_printer() -> PathPrinter:
    return PathPrinter()


@then(parsers.parse("the route is:{picture}"))
def route_check(picture, path, path_printer, start_point, state):
    expected_points = get_path_points_from_picture(picture)

    printed_actual = path_printer.render_path(state,
                                              path,
                                              only_show_floor=False,
                                              me_point=start_point)

    print("actual:")
    print(printed_actual)
    print(path)
    print()
    print("expected:")
    print(picture)
    print(expected_points)

    expected_points_not_in_actual = []
    for point in expected_points:
        if point in path:
            path.remove(point)
        else:
            expected_points_not_in_actual.append(point)

    assert_that(path,
                "points in actual but not expected").is_empty()
    assert_that(expected_points_not_in_actual,
                "points expected but not in returned path").is_empty()
