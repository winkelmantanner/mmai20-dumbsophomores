import numpy as np

CAT_OVERLORD_TITLE = 'cat overlord'
STARTING_UNIT_JOBS = ['missionary', 'soldier', 'builder']
STRUCTURE_TYPE_ROAD = 'road'
STRUCTURE_TYPE_NEUTRAL = 'neutral'
MISSIONARY_JOB_TITLE = 'missionary'
SOLDIER_JOB_TITLE = 'soldier'
BUILDER_JOB_TITLE = 'builder'
SHELTER_TYPE = 'shelter'
FRESH_HUMAN_JOB_TITLE = 'fresh human'
ENERGY_NEEDED_TO_CONVERT = 75
ENERGY_NEEDED_TO_DECONSTRUCT = 75
ENERGY_NEEDED_TO_CONSTRUCT = 75
MATERIALS_NEEDED_TO_CONSTRUCT = 50

class AIController():
    def __init__(self, game, player):
        self._jobs = {}

        for job in game.jobs:
            self._jobs[job.title] = job

        self._player = player
        self._units = self.player.units
        self._first_turn = True
        self._game = game

        self.update_structures()

        self._my_units = {}
        self._missionary_targets = {}
        self._builders_targets = {}
        self.update_units()
        self.update_build_targets()

    def update_structures(self):
        self._road = {}
        self._road_coordinates = []
        self._neutral_structures = []
        self._neutral_structure_coordinates = []
        self._our_structures = []
        self._our_structures_coordinates = []
        self._their_strucutures = []
        self._their_structures_coordinates =[]

        for structure in self.game.structures:
            if structure.tile:
                if self.is_road(structure):
                    self._road_coordinates.append((structure.tile.x, structure.tile.y))
                    y = structure.tile.y

                    if y not in self._road:
                        self._road[y] = []
                    
                    self._road[y].append(structure)
                elif self.is_neutral_structure(structure):
                    self._neutral_structure_coordinates.append((structure.tile.x, structure.tile.y))
                    self._neutral_structures.append(structure)
                elif self.is_our_structure(structure):
                    self._our_structures_coordinates.append((structure.tile.x, structure.tile.y))
                    self._our_structures.append(structure)
                elif self.is_their_structure(structure):
                    self._their_structures_coordinates.append((structure.tile.x, structure.tile.y))
                    self._their_structures_coordinates.append(structure)
        
        self._road_coordinates = np.asarray(self._road_coordinates)
        self._neutral_structure_coordinates = np.asarray(self._neutral_structure_coordinates)
        self._our_structures_coordinates = np.asarray(self._our_structures_coordinates)
        self._their_structures_coordinates = np.asarray(self._their_structures_coordinates)
        self._top_road = self._road[min(self._road.keys())]
        self._bottom_road = self._road[max(self._road.keys())]
        self._leftmost_top_road = sorted(self._top_road, key=lambda structure: structure.tile.x)[1].tile
        self._rightmost_bottom_road = sorted(self._bottom_road, key=lambda structure: structure.tile.x)[-2].tile

    def update_units(self):
        for job_title in self._jobs.keys():
            self._my_units[job_title] = []
        for unit in self.game.units:
            if unit.owner and unit.owner == self.player and unit.job:
                self._my_units[unit.job.title].append(unit)

    def update_build_targets(self):
        self._build_targets = []
        cat_overlord = self.find_unit_with_job_type(CAT_OVERLORD_TITLE)

        for y in range(cat_overlord.tile.y - 2, cat_overlord.tile.y + 2):
            for x in range(cat_overlord.tile.x - 2, cat_overlord.tile.x + 2):
                target = self.game.get_tile_at(x, y)

                if target and target.is_pathable() and not target.structure:
                    self._build_targets.append(target)
            
    @property
    def player(self):
        return self._player

    @property
    def first_turn(self):
        value = self._first_turn
        self._first_turn = False
        return value

    @property
    def road_coordinates(self):
        return self._road_coordinates

    @property
    def neutral_structures(self):
        return self._neutral_structures

    @property
    def neutral_structure_coordinates(self):
        return self._neutral_structure_coordinates

    @property
    def units(self):
        return self._units

    @property
    def top_road(self):
        return self._top_road

    @property
    def bottom_road(self):
        return self._bottom_road

    @property
    def game(self):
        return self._game

    def get_number_of_units(self, title):
        return len(self._my_units[title])

    def change_jobs_at_start(self, jobs=STARTING_UNIT_JOBS):
        assert len(jobs) == len(self.units)-1, 'Not enough jobs for the number of units!'
        idx = 0

        for unit in self.units:
            if not self.is_cat_overlord(unit):
                unit.change_job(jobs[idx])
                self._my_units[jobs[idx]].append(unit)
                
                idx += 1
            else:
                self._my_units[CAT_OVERLORD_TITLE].append(unit)

    def get_distance_to_closest_enemy_unit(self):
        cat_overlord = self.find_unit_with_job_type(CAT_OVERLORD_TITLE)
        unit_pos = np.asarray(self.get_unit_pos(cat_overlord))
        enemy_unit_coordinates = []
        distance = np.inf
        tile = None

        for unit in self.game.units:
            if unit and unit.owner is not None and unit.owner != self.player and unit.job and unit.job.title == SOLDIER_JOB_TITLE:
                enemy_unit_coordinates.append(self.get_unit_pos(unit))
        
        enemy_unit_coordinates = np.asarray(enemy_unit_coordinates)
        
        if len(enemy_unit_coordinates) > 0:
            distances = np.sqrt(np.sum((enemy_unit_coordinates-unit_pos)**2, axis=1))
            idx = np.argmin(distances)
            tile = self.game.get_tile_at(*enemy_unit_coordinates[idx])
            distance = distances[idx]

        return distance, tile
    
    def get_distance_to_closest_unit(self):
        cat_overlord = self.find_unit_with_job_type(CAT_OVERLORD_TITLE)
        unit_pos = np.asarray(self.get_unit_pos(cat_overlord))
        enemy_unit_coordinates = []
        distance = np.inf
        tile = None

        for unit in self.game.units:
            if unit and unit.owner is not None and unit.owner == self.player and unit.job and unit.job.title == SOLDIER_JOB_TITLE:
                enemy_unit_coordinates.append(self.get_unit_pos(unit))
        
        enemy_unit_coordinates = np.asarray(enemy_unit_coordinates)
        
        if len(enemy_unit_coordinates) > 0:
            distances = np.sqrt(np.sum((enemy_unit_coordinates-unit_pos)**2, axis=1))
            idx = np.argmin(distances)
            tile = self.game.get_tile_at(*enemy_unit_coordinates[idx])
            distance = distances[idx]

        return distance, tile

    def get_unit_pos(self, unit):
        return (unit.tile.x, unit.tile.y)

    def get_closest_tile_to_unit(self, unit, tiles):
        if unit.tile:
            tiles = [tile for tile in tiles if tile.is_pathable()]
            tile_locations = np.asarray([(tile.x, tile.y) for tile in tiles])
            
            if not len(tile_locations):
                tile_locations = np.array([[np.inf, np.inf]])

            unit_pos = np.asarray(self.get_unit_pos(unit))
            distances = np.sum((tile_locations - unit_pos)**2, axis=1)
            
            return tiles[np.argmin(distances)] if len(tiles) > 0 else unit.tile
    
    def get_road_tile_closest_to_unit(self, unit):
        unit_pos = np.asarray(self.get_unit_pos(unit))
        distances = np.sum((self.road_coordinates - unit_pos)**2, axis=1)
        return self.game.get_tile_at(*self.road_coordinates[np.argmin(distances)])

    def get_neutral_structure_closest_to_unit(self, unit):
        unit_pos = np.asarray(self.get_unit_pos(unit))

        if not len(self.neutral_structure_coordinates):
            return None

        distances = np.sum((self.neutral_structure_coordinates - unit_pos)**2, axis=1)
        return self.game.get_tile_at(*self.neutral_structure_coordinates[np.argmin(distances)])
    
    def get_shelter_closest_to_unit(self, unit):
        unit_pos = np.asarray(self.get_unit_pos(unit))

        if not len(self._our_structures_coordinates):
            return None

        distances = np.sum((self._our_structures_coordinates - unit_pos)**2, axis=1)
        return self.game.get_tile_at(*self._our_structures_coordinates[np.argmin(distances)])

    def get_enemy_shelter_closest_to_unit(self, unit):
        unit_pos = np.asarray(self.get_unit_pos(unit))

        if not len(self._their_structures_coordinates):
            return None

        distances = np.sum((self._their_structures_coordinates - unit_pos)**2, axis=1)
        return self.game.get_tile_at(*self._their_structures_coordinates[np.argmin(distances)])

    def move_towards_target(self, unit, target, find_path):
        neighbors = [tile for tile in target.get_neighbors() if tile and tile.is_pathable()]

        for tile in (target.tile_east, target.tile_west):
            if tile:
                if tile.tile_north and tile.tile_north.is_pathable():
                    neighbors.append(tile.tile_north)
                if tile.tile_south and tile.tile_south.is_pathable():
                    neighbors.append(tile.tile_south)
        
        closest_tile = self.get_closest_tile_to_unit(unit, neighbors)

        if closest_tile is not None:
            path = find_path(unit.tile, self.get_closest_tile_to_unit(unit, neighbors))
            
            while len(path) > 0 and unit.moves > 0:
                unit.move(path[0])
                del path[0]

            return len(path)
        else:
            return 0

    def move_to(self, unit, tile, find_path):
        path = find_path(unit.tile, tile)
        
        while len(path) > 0 and unit.moves > 0:
            unit.move(path[0])
            del path[0]

        return len(path)
    
    def move_towards_unit(self, unit, target_unit, find_path):
        if target_unit:
            return self.move_towards_target(unit, target_unit.tile, find_path)
        
        return 0

    def have_missionaries_convert_fresh_humans(self, find_path):
        for missionary in self.get_units_with_job_type(MISSIONARY_JOB_TITLE):
            if missionary.energy >= ENERGY_NEEDED_TO_CONVERT:
                self._missionary_targets[missionary] = None
                possible_tiles = []

                for unit in self.game.units:
                    if self.is_unit_convertible(unit) and unit.tile:
                        possible_tiles.extend(unit.tile.get_neighbors())
                    
                if possible_tiles:
                    self._missionary_targets[missionary] = self.get_closest_tile_to_unit(missionary, possible_tiles)
                
                if self._missionary_targets[missionary]:
                    self.move_to(missionary, self._missionary_targets[missionary], find_path)
            else:
                if missionary in self._missionary_targets:
                    del self._missionary_targets[missionary]
                
                shelter = self.get_shelter_closest_to_unit(missionary)
                
                if shelter is not None:
                    path_length = self.move_towards_target(missionary, shelter, find_path)
                    
                    if not path_length:
                        missionary.rest()

    def get_all_neighbors(self, tile):
        neighbors = tile.get_neighbors()

        for tile in (tile.tile_east, tile.tile_west):
            if tile:
                if tile.tile_north:
                    neighbors.append(tile.tile_north)
                if tile.tile_south:
                    neighbors.append(tile.tile_south)
        
        return neighbors

            
    def is_unit_near_unit_type(self, unit, title):
        neighbors = self.get_all_neighbors(unit.tile)

        for tile in neighbors:
            if tile.unit and tile.unit.owner == self.player and tile.unit.job.title == title:
                return True
    
    def have_builders_harvest_resources(self, find_path):
        builders = self.get_units_with_job_type(BUILDER_JOB_TITLE)
        cat_overlord = self.find_unit_with_job_type(CAT_OVERLORD_TITLE)
        
        for builder in builders:
            if builder.materials == 0:
                if builder.energy >= ENERGY_NEEDED_TO_DECONSTRUCT:
                    if builder not in self._builders_targets:
                        self._builders_targets[builder] = self.get_neutral_structure_closest_to_unit(builder)
                    
                    if self._builders_targets[builder]:
                        path_length = self.move_towards_target(builder, self._builders_targets[builder], find_path)

                        if not path_length:
                            builder.deconstruct(self._builders_targets[builder])

                else:
                    if builder in self._builders_targets:
                        del self._builders_targets[builder]

                    closest_shelter = self.get_shelter_closest_to_unit(builder)
                    
                    if closest_shelter:
                        path_length = self.move_towards_target(builder, closest_shelter, find_path)

                        if not path_length:
                            builder.rest()
    
    def send_builders_with_materials_to_build_shelter_near_missionary(self, find_path):
        builders = self.get_units_with_job_type(BUILDER_JOB_TITLE)
        missionary = self.find_unit_with_job_type(MISSIONARY_JOB_TITLE)
        cat_overlord = self.find_unit_with_job_type(CAT_OVERLORD_TITLE)

        for builder in builders:
            if builder.materials >= MATERIALS_NEEDED_TO_CONSTRUCT:
                if builder.energy >= ENERGY_NEEDED_TO_CONSTRUCT:
                    path_length = self.move_to(builder, self.get_closest_tile_to_unit(builder, self._build_targets), find_path)
                    
                    if not path_length:
                        for tile in builder.tile.get_neighbors():
                            if tile and not tile.structure and tile.is_pathable():
                                builder.drop(tile, 'material', -1)
                                builder.construct(tile, SHELTER_TYPE)
                                break
                else:
                    target = self.get_shelter_closest_to_unit(builder)

                    if not target:
                        target = self.get_enemy_shelter_closest_to_unit(builder)
                    
                    if target:
                        path_length = self.move_towards_target(builder, target, find_path)

                        if not path_length:
                            builder.rest()
    
    def move_cat_overlord_away_from_starting_point(self, find_path):
        cat_overlord = self.find_unit_with_job_type(CAT_OVERLORD_TITLE)
        neutral_shelter = self.get_neutral_structure_closest_to_unit(cat_overlord)
        self.move_towards_target(cat_overlord, neutral_shelter, find_path)

    def move_fresh_humans_towards_cat_overlord(self, find_path):
        cat_overlord = self.find_unit_with_job_type(CAT_OVERLORD_TITLE)
        fresh_humans = self.get_units_with_job_type(FRESH_HUMAN_JOB_TITLE)

        for fresh_human in fresh_humans:
            path_length = self.move_towards_unit(fresh_human, cat_overlord, find_path)
            if fresh_human.energy < 100 and (not path_length or self.is_unit_near_unit_type(CAT_OVERLORD_TITLE)):
                fresh_human.rest()
            
    def find_convertable_unit_near_missionary(self, missionary):
        tile = missionary.tile

        if tile:
            tiles_to_check = tile.get_neighbors()
            unit_found = None
            tile_found = None

            for tile in tiles_to_check:
                if tile and tile.unit and self.is_unit_convertible(tile.unit):
                    unit_found = tile.unit
                    tile_found = tile
                    break

            return unit_found, tile_found

    def convert_units_near_missionaries(self):
        converted_unit = False

        for missionary in self.get_units_with_job_type(MISSIONARY_JOB_TITLE):
            convertible_unit, tile = self.find_convertable_unit_near_missionary(missionary)
            if missionary.energy >= ENERGY_NEEDED_TO_CONVERT and convertible_unit:
                if missionary.convert(tile):
                    converted_unit = True
                    self._my_units[convertible_unit.job.title].append(convertible_unit)

        return converted_unit

    def convert_fresh_humans_to(self, convert_to=SOLDIER_JOB_TITLE):
        cat_overlord = self.find_unit_with_job_type(CAT_OVERLORD_TITLE)
        fresh_humans = self.get_units_with_job_type(FRESH_HUMAN_JOB_TITLE)

        for neighbor in self.get_all_neighbors(cat_overlord.tile):
            if neighbor.unit and neighbor.unit in fresh_humans:
                conversion_successful = neighbor.unit.change_job(convert_to)
                
                if conversion_successful:
                    fresh_humans.remove(neighbor.unit)
    
    def get_unit_tile(self, unit):
        return unit.job.title

    def get_structure_type(self, structure):
        return structure.type

    def is_cat_overlord(self, unit):
        return self.get_unit_tile(unit) == CAT_OVERLORD_TITLE
    
    def is_road(self, structure):
        return self.get_structure_type(structure) == STRUCTURE_TYPE_ROAD
    
    def is_neutral_structure(self, structure):
        return self.get_structure_type(structure) == STRUCTURE_TYPE_NEUTRAL

    def is_our_structure(self, structure):
        return self.get_structure_type(structure) == SHELTER_TYPE and structure.owner == self.player

    def is_their_structure(self, structure):
        return self.get_structure_type(structure) == SHELTER_TYPE and structure.owner and structure.owner != self.player

    def is_unit_near_bottom_road(self, unit):
        return unit.tile.y >= self.bottom_road[0].tile.y

    def get_job(self, name):
        return self._jobs[name]

    def is_unit_convertible(self, unit):
        return unit.owner is None

    def get_units_with_job_type(self, title):
        return self._my_units[title]

    def find_unit_with_job_type(self, title, idx=0):
        num_units_with_target_job = len(self._my_units[title])
        return self._my_units[title][idx] if 0 < num_units_with_target_job and idx < num_units_with_target_job else None
