# This is where you build your AI for the Catastrophe game.

from joueur.base_ai import BaseAI
from .ai_controller import AIController, MISSIONARY_JOB_TITLE, SOLDIER_JOB_TITLE, BUILDER_JOB_TITLE

# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
# you can add additional import(s) here
# <<-- /Creer-Merge: imports -->>

SOLDIER_ACTION_COST = 25
NUM_SOLDIERS_FOR_MISS2 = 2
MAX_NUM_MISS = 2
DIST_TO_CAT_OFFSET = 2

class AI(BaseAI):
    """ The basic AI functions that are the same between games. """

    def get_name(self):
        """ This is the name you send to the server so your AI will control the player named this string.

        Returns
            str: The name of your Player.
        """
        # <<-- Creer-Merge: get-name -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        return "DumbSophomores" # REPLACE THIS WITH YOUR TEAM NAME
        # <<-- /Creer-Merge: get-name -->>

    def start(self):
        """ This is called once the game starts and your AI knows its playerID and game. You can initialize your AI here.
        """
        # <<-- Creer-Merge: start -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your start logic
        # <<-- /Creer-Merge: start -->>
        
        self . ATTACK_SOLDIERS = 12
        self._controller = AIController(self.game, self.player)
        self . attack = False


    @property
    def controller(self):
        return self._controller

    def game_updated(self):
        """ This is called every time the game's state updates, so if you are tracking anything you can update it here.
        """
        # <<-- Creer-Merge: game-updated -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your game updated logic
        # <<-- /Creer-Merge: game-updated -->>

        self.controller.update_structures()

    def end(self, won, reason):
        """ This is called when the game ends, you can clean up your data and dump files here if need be.

        Args:
            won (bool): True means you won, False means you lost.
            reason (str): The human readable string explaining why you won or lost.
        """
        # <<-- Creer-Merge: end -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your end logic
        # <<-- /Creer-Merge: end -->>
    # <<-- Creer-Merge: end -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your end logic
        # <<-- /Creer-Merge: end -->>
    def GetAllMyUnits ( self ) :
        return self . player . units
        
    def GetMySoldiers ( self ) :
        Soldiers = []
        Units = self . GetAllMyUnits ( )
        for TempUnit in Units :
            if TempUnit . job == self . controller . get_job ( 'soldier' ) :
                Soldiers . append ( TempUnit )
        return Soldiers
    
    def GetAllPlayerUnits ( self , player ) :
        return player . units
        
    def GetPlayerSoldiers ( self , player ) :
        Soldiers = []
        Units = self . GetAllPlayerUnits ( player )
        for TempUnit in Units :
            if TempUnit . job == self . controller . get_job ( 'soldier' ) :
                Soldiers . append ( TempUnit )
        return Soldiers
        
    def MoveSoldiers ( self ) :
        Soldiers = self . GetMySoldiers ( )
        for TempSoldier in Soldiers :
            if TempSoldier . energy > SOLDIER_ACTION_COST:
                OppoKingTile = self . player . opponent . cat . tile
                TileOn = TempSoldier . tile
                PathTiles = self . find_path ( TileOn , OppoKingTile )
                while TempSoldier . moves > 0 and len ( PathTiles ) > 1 :
                    TempSoldier . move ( PathTiles [ 0 ] )
                    TileOn = TempSoldier . tile
                    PathTiles = self . find_path ( TileOn , OppoKingTile )
            else :
                self . MoveTowardNearestShelterAndRest( TempSoldier )
    
    def HasCat ( self , tile ) :
        Output = False
        PossibleUnit = tile . unit
        if PossibleUnit :
            if PossibleUnit . job . title == 'cat overlord' :
                Output = True
        return Output
    
    def HasStructure ( self , tile ) :
        Output = False
        PossibleStructure = tile . structure
        if PossibleStructure :
            Title = PossibleStructure . type
            if Title == 'shelter' :
                Output = True
        return Output
    
    def FindNearestShelter ( self , Unit ) :
        MinDist = 9999999
        ClosestStructure = self . player . structures [ 0 ]
        for TempStructure in self . player . structures :
            if TempStructure . type == 'shelter' :
                PathTiles = self . find_path ( Unit . tile , TempStructure . tile )
                TempDist = len ( PathTiles )
                if self . HasCat ( TempStructure . tile ) == True :
                    TempDist = 500
                if TempDist < MinDist :
                    MinDist = TempDist
                    ClosestStructure = TempStructure
        return ClosestStructure
    
    def MoveSoldiersToAShelter ( self ) :
        Soldiers = self . GetMySoldiers ( )
        for TempSoldier in Soldiers :
            TargetShelter = self . FindNearestShelter ( TempSoldier )
            PathTiles = self . find_path ( TempSoldier . tile , TargetShelter . tile )
            if len ( PathTiles ) > 0 :
                TempSoldier . move ( PathTiles [ 0 ] )
    
    def GetDistToClosestSoldierFromCat ( self ) :
        MinDist = 99999
        Soldiers = self . GetMySoldiers ( )
        CatTile = self . player . cat . tile
        for TempSoldier in Soldiers :
            PathTiles = self . find_path ( CatTile , TempSoldier . tile )
            TempDist = len ( PathTiles )
            if TempDist < MinDist :
                MinDist = TempDist
        return MinDist
    
    def IsCatInDanger ( self ) :
        Output = False
        NearestEnemySoldierDist , Tile = self . controller . get_distance_to_closest_enemy_unit ( )
        MinSoldierDist = self . GetDistToClosestSoldierFromCat ( )
        if NearestEnemySoldierDist < MinSoldierDist + DIST_TO_CAT_OFFSET :
            Output = True
        return Output
    
    def MoveSoldiersDefense ( self ) :
        Soldiers = self . GetMySoldiers ( )
        for TempSoldier in Soldiers :
            if TempSoldier . energy > SOLDIER_ACTION_COST:
                Distance , OpponentTile = self . controller . get_distance_to_closest_enemy_unit ( )
                if OpponentTile != None :
                    TileOn = TempSoldier . tile
                    PathTiles = self . find_path ( TileOn , OpponentTile )
                    while TempSoldier . moves > 0 and len ( PathTiles ) > 1 :
                        TempSoldier . move ( PathTiles [ 0 ] )
                        TileOn = TempSoldier . tile
                        PathTiles = self . find_path ( TileOn , OpponentTile )
            else :
                self . MoveTowardNearestShelterAndRest( TempSoldier )
    
    def MoveUnits ( self ) :
        if self . IsCatInDanger ( ) == True :
            self . MoveSoldiersDefense ( )
        else :
            if self . attack == True :
                self . MoveSoldiers ( )
            else :
                self . MoveSoldiersToAShelter ( )
            print ( 'aha' )

    def canRest ( self , unit ) :
        if unit . tile . structure and unit . tile . structure . type == 'shelter' and unit . tile . structure . owner == self . player :
            return True
        for tile in unit . tile . get_neighbors ( ) :
            if tile . structure and tile . structure . type == 'shelter' and tile . structure . owner == self . player :
                return True
            for tile2 in tile . get_neighbors ( ) :
                if tile . structure and tile . structure . type == 'shelter' and tile . structure . owner == self . player :
                    return True
        return False

    def MoveTowardNearestShelterAndRest ( self , unit ) :
        stuck = False
        while not stuck and unit . moves > 0 :
            path_to_nearest_shelter = [ ]
            for structure in self . player . structures :
                if structure . type == 'shelter' :
                    path = self . find_path ( unit . tile , structure . tile )
                    valid = True
                    if len ( path ) > 0 :
                        for tile in path :
                            if not ( not tile . unit and ( not tile . structure or tile . structure . type in [ 'road' , 'shelter' ] ) ) :
                                valid = False
                        if valid :
                            if len ( path ) < len ( path_to_nearest_shelter ) or len ( path_to_nearest_shelter ) == 0:
                                path_to_nearest_shelter = path
            if len ( path_to_nearest_shelter ) > 0 :
                unit . move ( path_to_nearest_shelter [ 0 ] )
            else :
                print ( "MoveTowardNearestShelterAndRest is stuck" )
                stuck = True
        if self . canRest ( unit ) :
           unit . rest ( )

    def SoldiersAttack ( self ) :
        Soldiers = self . GetMySoldiers ( )
        for TempSoldier in Soldiers :
            if TempSoldier . energy > SOLDIER_ACTION_COST:
                NeighborTiles = TempSoldier . tile . get_neighbors ( )
                for TempTile in NeighborTiles :
                    PossibleUnit = TempTile . unit
                    if PossibleUnit != None :
                        if PossibleUnit . owner != self . player :
                            TempTitle = PossibleUnit . job . title
                            if TempTitle == 'cat overlord' :
                                TempSoldier . attack ( TempTile )
                            elif TempTitle == 'soldier' :
                                TempSoldier . attack ( TempTile )
                            elif TempTitle == 'missionary' and PossibleUnit . energy <= TempSoldier . energy :
                                TempSoldier . attack ( TempTile )
            else:
                self . MoveTowardNearestShelterAndRest ( TempSoldier )
                
    def SoldierHeal ( self ) :
        Soldiers = self . GetMySoldiers ( )
        for TempSoldier in Soldiers :
            neighbors = TempSoldier . tile . get_neighbors ( )
            for neighbor in neighbors :
                if self . HasStructure ( neighbor ) == True :
                    TempSoldier . rest ( )
    
    def CheckToAttack ( self ) :
        Soldiers = self . GetMySoldiers ( )
        BadSoldiers = self . GetPlayerSoldiers ( self . player . opponent )
        if len ( Soldiers ) > len ( BadSoldiers ) + 3 or len ( Soldiers ) >= self . ATTACK_SOLDIERS :
            self . attack = True
    
    def run_turn(self):
        """ This is called every time it is this AI.player's turn.

        Returns:
            bool: Represents if you want to end your turn. True means end your turn, False means to keep your turn going and re-call this function.
        """
        
        try :
            first_turn = self.controller.first_turn

            if first_turn:
                self.controller.change_jobs_at_start()
            
            self.controller.update_units()
            self.controller.update_build_targets()
            num_missionaries = self.controller.get_number_of_units(MISSIONARY_JOB_TITLE)
            num_soldiers = self.controller.get_number_of_units(SOLDIER_JOB_TITLE)
            num_builders = self.controller.get_number_of_units(BUILDER_JOB_TITLE)


            self.controller.have_missionaries_convert_fresh_humans(self.find_path)
            self.controller.convert_units_near_missionaries()
            self.controller.move_fresh_humans_towards_cat_overlord(self.find_path)
            convert_to = SOLDIER_JOB_TITLE

            if (num_missionaries < MAX_NUM_MISS and num_soldiers >= NUM_SOLDIERS_FOR_MISS2) or num_missionaries == 0: 
                convert_to = MISSIONARY_JOB_TITLE
            elif num_builders == 0 or num_builders < 2 and num_soldiers >= NUM_SOLDIERS_FOR_MISS2:
                convert_to = BUILDER_JOB_TITLE
            
            self.controller.convert_fresh_humans_to(convert_to)
            self.controller.have_builders_harvest_resources(self.find_path)
            self.controller.send_builders_with_materials_to_build_shelter_near_missionary(self.find_path)
            
            self . SoldiersAttack ( )
            
            self . MoveUnits ( )
            
            self . SoldiersAttack ( )
            
            self . SoldierHeal ( )
            
            self . CheckToAttack ( )
            
        except Exception as e:
            print(e)
            return True
        
        # <<-- Creer-Merge: runTurn -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # Put your game logic here for runTurn
        return True
        # <<-- /Creer-Merge: runTurn -->>

    def find_path(self, start, goal):
        """A very basic path finding algorithm (Breadth First Search) that when given a starting Tile, will return a valid path to the goal Tile.
        Args:
            start (Tile): the starting Tile
            goal (Tile): the goal Tile
        Returns:
            list[Tile]: A list of Tiles representing the path, the the first element being a valid adjacent Tile to the start, and the last element being the goal.
        """

        if start == goal:
            # no need to make a path to here...
            return []

        # queue of the tiles that will have their neighbors searched for 'goal'
        fringe = []

        # How we got to each tile that went into the fringe.
        came_from = {}

        # Enqueue start as the first tile to have its neighbors searched.
        fringe.append(start)

        # keep exploring neighbors of neighbors... until there are no more.
        while len(fringe) > 0:
            # the tile we are currently exploring.
            inspect = fringe.pop(0)

            # cycle through the tile's neighbors.
            for neighbor in inspect.get_neighbors():
                # if we found the goal, we have the path!
                if neighbor == goal:
                    # Follow the path backward to the start from the goal and return it.
                    path = [goal]

                    # Starting at the tile we are currently at, insert them retracing our steps till we get to the starting tile
                    while inspect != start:
                        path.insert(0, inspect)
                        inspect = came_from[inspect.id]
                    
                    return path
                # else we did not find the goal, so enqueue this tile's neighbors to be inspected

                # if the tile exists, has not been explored or added to the fringe yet, and it is pathable
                if neighbor and neighbor.id not in came_from and neighbor.is_pathable():
                    # add it to the tiles to be explored and add where it came from for path reconstruction.
                    fringe.append(neighbor)
                    came_from[neighbor.id] = inspect

        # if you're here, that means that there was not a path to get to where you want to go.
        #   in that case, we'll just return an empty path.
        return []

    # <<-- Creer-Merge: functions -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
    # if you need additional functions for your AI you can add them here
    # <<-- /Creer-Merge: functions -->>