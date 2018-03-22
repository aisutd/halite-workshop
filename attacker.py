
import hlt
import logging

#game start
game = hlt.Game("Attacker")

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []

    planets = game_map.all_planets()
    ships = game_map.get_me().all_ships()


    for ship in game_map.get_me().all_ships():
        # If the ship is docked skip the ship
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue

        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        nearest_planet = None
        planet_list = {}

        #planet list
        for key,value in entities_by_distance.items():
            if isinstance(value[0], hlt.entity.Planet):
                planet_list[key] = value[0]

        #sorted planet list by distanec
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

        enemy_ship = None
        enemyPlanets = []
        #if all are full attack the docked ship of nearest enemy planet
        if nearest_planet == None:
            for planet in sorted(planet_list):
                if(planet_list[planet].owner.id!=game_map.my_id):
                    enemyPlanets.append(planet_list[planet])
            nearest_planet = enemyPlanets[ships.index(ship)%len(enemyPlanets)]

            for enemyShip in nearest_planet.all_docked_ships():
                if(enemyShip.owner.id!=game_map.my_id):
                    enemy_ship = enemyShip
                    break

        if nearest_planet == None:
            nearest_planet = planets[ships.index(ship)%len(planets)]
        obs = game_map.obstacles_between(ship,nearest_planet) if enemy_ship == None else game_map.obstacles_between(ship,enemy_ship)

        if ship.can_dock(nearest_planet):
            command_queue.append(ship.dock(nearest_planet))
        else:
            # If we can't dock, we move towards the closest empty point near this planet (by using closest_point_to)

            #adjust speed based on obstacles
            maxSpeed =  hlt.constants.MAX_SPEED/1.25 if len(obs)>0 else hlt.constants.MAX_SPEED
            #adjust avoid_obstacles flag based on obstacles
            avoid_obstacles = True if len(obs) > 0 else False
            target = ship.closest_point_to(nearest_planet) if enemy_ship==None else enemy_ship
            navigate_command = ship.navigate(target,
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
