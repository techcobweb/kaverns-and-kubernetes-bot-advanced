

import pytest
from sys import version_info
from assertpy import assert_that
from roguebot.env_vars import EnvVarExtractor


@pytest.fixture
def env_a() -> dict:
    env = {
        'K_AND_K_BOT_NAME': 'fred',
        'K_AND_K_BOT_ROLE': 'hero',
        'K_AND_K_SERVER_URL': 'http://localhost:3000',
        'K_AND_K_BOT_DEBUG': 'True'
    }
    return env


class VersionInfo():
    def __init__(self, major, minor, micro):
        self.major = major
        self.minor = minor
        self.micro = micro


@pytest.fixture
def ok_python_version() -> dict:
    return VersionInfo(3, 8, 0)


@pytest.fixture
def old_python_version_major_small() -> dict:
    return VersionInfo(2, 8, 0)


@pytest.fixture
def old_python_version_minor_small() -> dict:
    return VersionInfo(3, 4, 0)


def test_env_var_extractor_gets_all_ok(env_a, ok_python_version) -> None:

    env = EnvVarExtractor(env_a, ok_python_version)

    assert_that(env.character_name).contains('-')

    assert_that(env.character_name.startswith('fred')).is_true()
    assert_that(env.character_role).is_equal_to('hero')
    assert_that(env.url).is_equal_to('http://localhost:3000')
    assert_that(env.is_debug).is_true()
    assert_that(env.is_ok).is_true()


def test_env_var_spots_down_level_python_version_major_small(env_a, old_python_version_major_small) -> None:
    env = EnvVarExtractor(env_a, old_python_version_major_small)
    assert_that(env.is_ok).is_false()


def test_env_var_spots_down_level_python_version_minor_small(env_a, old_python_version_minor_small) -> None:
    env = EnvVarExtractor(env_a, old_python_version_minor_small)
    assert_that(env.is_ok).is_false()


def test_env_var_not_ok_when_character_name_missing(env_a, ok_python_version) -> None:

    env_a.pop('K_AND_K_BOT_NAME')

    env = EnvVarExtractor(env_a, ok_python_version)

    assert_that(env.is_ok).is_false()


def test_env_var_startup_delay_defaults_to_five(env_a, ok_python_version) -> None:

    env = EnvVarExtractor(env_a, ok_python_version)

    assert_that(env.startup_delay_seconds).is_equal_to(5)


def test_env_var_startup_delay_can_be_set(env_a, ok_python_version) -> None:
    env_a['K_AND_K_BOT_STARTUP_DELAY_SECONDS'] = "2"
    env = EnvVarExtractor(env_a, ok_python_version)
    assert_that(env.startup_delay_seconds).is_equal_to(2)


def test_env_var_startup_delay_cannot_be_negative(env_a, ok_python_version) -> None:
    env_a['K_AND_K_BOT_STARTUP_DELAY_SECONDS'] = "-2"
    env = EnvVarExtractor(env_a, ok_python_version)
    assert_that(env.startup_delay_seconds).is_equal_to(0)


def test_env_var_bot_http_port_can_be_set_and_got(env_a, ok_python_version) -> None:
    env_a['K_AND_K_BOT_HTTP_SERVER_PORT'] = "4001"
    env = EnvVarExtractor(env_a, ok_python_version)
    assert_that(env.bot_http_server_port).is_equal_to(4001)


def test_env_var_limits_actions_per_turn_to_1_minimum(env_a, ok_python_version) -> None:

    # Under 1
    env_a['K_AND_K_BOT_ACTIONS_PER_TURN'] = 0

    env = EnvVarExtractor(env_a, ok_python_version)

    assert_that(env.actions_per_turn).is_equal_to(1)


def test_env_var_limits_speed_1_minimum(env_a, ok_python_version) -> None:

    # Under 1
    env_a['K_AND_K_BOT_SPEED'] = 0

    env = EnvVarExtractor(env_a, ok_python_version)

    assert_that(env.speed).is_equal_to(1)


def test_env_var_limits_speed_10_maximum(env_a, ok_python_version) -> None:

    # Over 11
    env_a['K_AND_K_BOT_SPEED'] = 11

    env = EnvVarExtractor(env_a, ok_python_version)

    assert_that(env.speed).is_equal_to(10)


def test_env_var_not_ok_when_role_missing(env_a, ok_python_version) -> None:
    env_a.pop('K_AND_K_BOT_ROLE')

    env = EnvVarExtractor(env_a, ok_python_version)

    assert_that(env.is_ok).is_false()


def test_env_var_not_ok_when_url_missing(env_a, ok_python_version) -> None:
    env_a.pop('K_AND_K_SERVER_URL')

    env = EnvVarExtractor(env_a, ok_python_version)

    assert_that(env.is_ok).is_false()


def test_env_var_not_ok_when_url_doesnt_start_with_http(env_a, ok_python_version) -> None:
    env_a['K_AND_K_SERVER_URL'] = 'invalidOnPurpose'

    env = EnvVarExtractor(env_a, ok_python_version)

    assert_that(env.is_ok).is_false()


def test_missing_debug_ok_defaults_to_false(env_a, ok_python_version) -> None:
    env_a.pop('K_AND_K_BOT_DEBUG')

    env = EnvVarExtractor(env_a, ok_python_version)

    assert_that(env.is_ok).is_true()
    assert_that(env.is_debug).is_false()
