
import hlt
import logging

#game start
game = hlt.Game("Harvester")

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []

    planets = game_map.all_planets()
    ships = game_map.get_me().all_ships()


    for ship in game_map.get_me().all_ships():
        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue
        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        nearest_planet = None
        planet_list = {}

        #planet list
        for key,value in entities_by_distance.items():
            if isinstance(value[0], hlt.entity.Planet):
                planet_list[key] = value[0]

        #move towards unowned planets
        for planet in sorted(planet_list):
            if(planet_list[planet].is_owned()==False):
                nearest_planet = planet_list[planet]
                break;

        #if all planets are owned, goto planets which are not completely docked
        if nearest_planet == None:
            for planet in sorted(planet_list):
                if(planet_list[planet].is_full()==False):
                    nearest_planet = planet_list[planet]
                    break;

        #if all are full randomly move towards a planet
        if nearest_planet == None:
            nearest_planet = planets[ships.index(ship)%len(planets)]

        obs = game_map.obstacles_between(ship,nearest_planet)
        # If we can dock, let's (try to) dock. If two ships try to dock at once, neither will be able to.
        if ship.can_dock(nearest_planet):
            # We add the command by appending it to the command_queue
            command_queue.append(ship.dock(nearest_planet))
        else:
            # If we can't dock, we move towards the closest empty point near this planet (by using closest_point_to)
            maxSpeed =  hlt.constants.MAX_SPEED/1.25 if len(obs)>0 else hlt.constants.MAX_SPEED
            avoid_obstacles = True if len(obs) > 0 else False
            navigate_command = ship.navigate(ship.closest_point_to(nearest_planet),
                game_map,
                speed=maxSpeed,
                avoid_obstacles=avoid_obstacles,
                ignore_ships=False,
                ignore_planets=False)

            if navigate_command:
                command_queue.append(navigate_command)



    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
