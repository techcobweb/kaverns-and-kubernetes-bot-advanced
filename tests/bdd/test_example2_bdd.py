from pytest_bdd import scenario, given, when, then
from assertpy import assert_that

@scenario(
    "features/example2.feature",
    "Outlined given, when, thens",
    example_converters=dict(start=int, eat=float, left=str)
)
def test_outlined():
    pass


@given("there are <start> cucumbers", target_fixture="start_cucumbers")
def start_cucumbers(start):
    assert_that(isinstance(start, int)).is_true()
    return dict(start=start)


@when("I eat <eat> cucumbers")
def eat_cucumbers(start_cucumbers, eat):
    assert_that(isinstance(eat, float)).is_true()
    start_cucumbers["eat"] = eat


@then("I should have <left> cucumbers")
def should_have_left_cucumbers(start_cucumbers, start, eat, left):
    assert_that(isinstance(left, str)).is_true()
    assert_that(start - eat).is_equal_to(int(left))
    assert_that(start_cucumbers["start"]).is_equal_to(start)
    assert_that(start_cucumbers["eat"]).is_equal_to(eat)