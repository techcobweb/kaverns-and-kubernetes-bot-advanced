Feature: Path Finder

    Scenario: finds path between rooms on same level
        Given a dungeon map of:
            """
            ----------- level z=0 :
            ######
            #    #
            #    #
            #    #
            #### #
            #    #
            #    #
            #    #
            ######
            -----------
            """
        And the start-point is 1,1,0
        And the end-point is 1,7,0
        And there are no entities
        When we plot a path
        Then the route is:
            """
            ----------- level z=0 :
            ######
            #X   #
            #.   #
            #....#
            ####.#
            #....#
            #.   #
            #.   #
            ######
            -----------
            """

    Scenario: finds path between rooms on same level in a maze
        Given a dungeon map of:
            """
            ----------- level z=0 :
            ######
            #    #
            #    #
            #  # #
            #### #
            #  # #
            #  # #
            #    #
            ######
            -----------
            """
        And the start-point is 1,1,0
        And the end-point is 1,5,0
        And there are no entities
        When we plot a path
        Then the route is:
            """
            ----------- level z=0 :
            ######
            #X   #
            #....#
            #  #.#
            ####.#
            #..#.#
            # .#.#
            # ...#
            ######
            -----------
            """

    Scenario: finds path between through funnel
        Given a dungeon map of:
            """
            ----------- level z=0 :
            #################
            #               #
            #               #
            #       # #     #
            ######### #######
            #  #    # #     #
            #  #    # #     #
            #    #### ####  #
            #               #
            #################
            -----------
            """
        And the start-point is 1,1,0
        And the end-point is 1,5,0
        And there are no entities
        When we plot a path
        Then the route is:
            """
            -----------------
            #################
            #X              #
            #.........      #
            #       #.#     #
            #########.#######
            #..#    #.#     #
            # .#    #.#     #
            # ...####.####  #
            #   ......      #
            #################
            -----------------
            """
