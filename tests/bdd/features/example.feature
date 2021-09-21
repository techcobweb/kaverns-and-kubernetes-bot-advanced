Feature: Roguelike Client
    Scenario: Demo roguelike client
        Given an empty inventory
        And the dungeon contains a sword
        And the dungeon contains a rock

        When I enter the dungeon
        And I pick up the sword

        Then I should have 1 items in my inventory
