import unittest
from model import *
from pubsub import MessageQueue

from log import Log
log = Log()
log.setVerbosity(Log.VERBOSITY_VERBOSE)

class ModelTestMethods(unittest.TestCase):

    def setUp(self):
        Tile.init()
        MessageQueue.getInstance(True)
        self.root = ModelObject()
    
    def tearDown(self):
        MessageQueue.reset(True)
        

    def test_AddTilesToSet(self):
        set = Set(self.root)
        t = Tile(1, GameConstants.BLACK, 1, set)
        self.assertEqual(set.addTile(t), 1)
        self.assertEqual(len(set.getTiles()), 1)
        #attempt to add same tile to the set again, it should fail (addTile returns 0)
        self.assertEqual(set.addTile(t), 0)

    def test_AddDoubleTileToGroup(self):
        set = Set(self.root)
        #create a set with 3 tiles with value 1, and different colors
        self.assertEqual(set.addTile(Tile(1, GameConstants.BLACK, 1, set)), 1)
        self.assertEqual(set.addTile(Tile(2, GameConstants.BLUE, 1, set)), 2)
        self.assertEqual(set.addTile(Tile(3, GameConstants.RED, 1, set)), 3)

        # attempt to add another black 1 to the set, it should fail (addTile returns 0)
        self.assertEqual(set.addTile(Tile(4, GameConstants.BLACK, 1, set)), 0)

    def test_ValidGroup(self):
        set = Set(self.root)
        i = 1
        #create a set with four tiles with value 1, and different colors
        for c in GameConstants.TILECOLORS:
            t = Tile(i, c, 1, set)
            self.assertEqual(set.addTile(t), i)
            i+=1
        self.assertTrue(set.isValid())

    def test_ValidRun(self):
        set = Set(self.root)
        # create a sequence of tiles of the same color (black 1,2,3)
        for v in range(1,4):
            t = Tile(v, GameConstants.BLACK, v, set)
            self.assertEqual(set.addTile(t), v)
        self.assertTrue(set.isValid())

    def test_AddTileToFullGroup(self):
        set = Set(self.root)
        i = 1
        #create a set with four tiles with value 1, and different colors
        for c in GameConstants.TILECOLORS:
            t = Tile(i, c, 1, set)
            self.assertEqual(set.addTile(t), i)
            i+=1
        # attempt to add another black 1 to the set, it should fail (addTile returns 0)
        self.assertEqual(set.addTile(Tile(5, GameConstants.BLACK, 1, set)), 0)

    def test_AddTileFitPosition(self):
        set = Set(self.root)
        self.assertEqual(set.addTile(Tile(5, GameConstants.BLACK, 4, set)), 1)
        #attempt to add a 3. it should be added to the front, restulting in fitpos==1
        self.assertEqual(set.addTile(Tile(6, GameConstants.BLACK, 3, set)), 1)

    def test_AddWrongTileToRun(self):
        #test that you cannot add a wrong colored tile to a sequence
        set = Set(self.root)
        # create a sequence of tiles of the same color (black 4,5,6)
        for v in range(1,4):
            t = Tile(v, GameConstants.BLACK, v+3, set)
            self.assertEqual(set.addTile(t), v)
        # attempt to add another black 5 to the set, it should fail (addTile returns 0)
        self.assertEqual(set.addTile(Tile(5, GameConstants.BLACK, 4, set)), 0)
        # attempt to add a red 7 to the set, it should fail (addTile returns 0)
        self.assertEqual(set.addTile(Tile(6, GameConstants.RED, 7, set)), 0)
        # attempt to add a blue 1 to the set, it should fail (addTile returns 0)
        self.assertEqual(set.addTile(Tile(7, GameConstants.BLUE, 1, set)), 0)

    def test_AddJokerToFullGroup(self):
        set = Set(self.root)
        i = 1
        #create a set with four tiles with value 1, and different colors
        for c in GameConstants.TILECOLORS:
            t = Tile(i, c, 1, set)
            self.assertEqual(set.addTile(t), i)
            i+=1
        # attempt to add a joker to the set, it should fail (addTile returns a position >0)
        self.assertEqual(set.addTile(Joker(5, GameConstants.BLACK, set)), 0)

    def test_AddJokerToRun(self):
        set = Set(self.root)
        # create a sequence of tiles of the same color (black 1,2,3)
        for v in range(1,4):
            t = Tile(v, GameConstants.BLACK, v, set)
            t.print()
            self.assertEqual(set.addTile(t), v)
        # attempt to add a joker to the set, it should not fail (addTile returns a position >0)
        self.assertNotEqual(set.addTile(Joker(5, GameConstants.BLACK, set)), 0)

    def test_AddJokerToFullRun(self):
        set = Set(self.root)
        # create a sequence of tiles of the same color (black 1,2,3)
        for v in range(1,14):
            t = Tile(v, GameConstants.BLACK, v, set)
            t.print()
            self.assertEqual(set.addTile(t), v)
        # attempt to add a joker to the set, it should fail (addTile returns a position == 0)
        self.assertEqual(set.addTile(Joker(15, GameConstants.BLACK, set)), 0)

    def test_AddRunToSetWithJoker(self):
        #create an empty set
        set = Set(self.root)
        #add a joker
        set.addTile(Joker(1, GameConstants.BLACK, set))
        # attempt to add a blue 7 to the set, it should NOT fail (addTile returns a pos>0)
        self.assertNotEqual(set.addTile(Tile(2, GameConstants.BLUE, 7, set)), 0)
        # attempt to add a blue 8 to the set, it should NOT fail (addTile returns a pos>0)
        self.assertNotEqual(set.addTile(Tile(3, GameConstants.BLUE, 8, set)), 0)
        # attempt to add a blue 5 to the set, it should NOT fail and addTile should return 1)
        self.assertEqual(set.addTile(Tile(4, GameConstants.BLUE, 5, set)), 1)

    def test_AddGroupToSetWithJoker(self):
        #create an empty set
        set = Set(self.root)
        #add a joker
        set.addTile(Joker(1, GameConstants.BLACK, set))
        # attempt to add a blue 1 to the set, it should NOT fail (addTile returns a pos>0)
        self.assertNotEqual(set.addTile(Tile(2, GameConstants.BLUE, 1, set)), 0)
        # attempt to add a red 1 to the set, it should NOT fail (addTile returns a pos>0)
        self.assertNotEqual(set.addTile(Tile(3, GameConstants.RED, 1, set)), 0)

class GameTestMethods(unittest.TestCase):

    def setUp(self):
        MessageQueue.getInstance(True)
        self.game = Game(2)
        self.game.addPlayerByName("Joe")
        self.joe = self.game.getPlayerByName("Joe")
        self.assertIsNotNone(self.joe)
        self.game.start(self.joe)
        print(self.game.toString())
        
    def tearDown(self):
        MessageQueue.reset(True)
        del self.game

    def test_MoveTileFromPileToBoard(self):
        pileSizeBefore = self.game.pile.getSize()
        tile = self.game.pile.findTile(1, GameConstants.BLACK)
        self.assertIsNotNone(tile)
        tile.move(self.game.board)
        self.assertEqual(len(self.game.board.sets), 1)
        pileSizeAfter = self.game.pile.getSize()
        self.assertEqual(pileSizeBefore-pileSizeAfter, 1)

    def test_AddSecondPlayer(self):
        self.game.addPlayerByName("Peter")
        self.assertIsNotNone(self.game.getPlayerByName("Peter"))

    def test_PickTile(self):
        plateSizeBefore = self.joe.plate.getSize()
        self.joe.pickTile()
        plateSizeAfter = self.joe.plate.getSize()
        self.assertEqual(plateSizeAfter-plateSizeBefore, 1)

    def test_BoardCleanUp(self):
        for tId in self.joe.plate.getTiles():
            t = self.joe.plate.getTile(tId)
            t.move(self.game.board)
            self.assertEqual(len(self.game.board.sets), 1)
            self.game.board.cleanUp()
            self.assertEqual(len(self.game.board.sets), 0)

            #break after first iteration, we only needed to test this for a single tile on Joe's plate
            break

    def test_CommitMoves(self):
        # add black tiles 1 through 5 to test player Joe's plate
        for i in range(1,6):
            tile = self.game.pile.findTile(i, GameConstants.BLACK)
            if tile:
                tile.move(self.joe.plate)

        #create a valid (complete) set on the board
        set = None
        for i in range(1,4):
            tile = self.joe.plate.findTile(i, GameConstants.BLACK)
            self.assertIsNotNone(tile)
            if not set:
                tile.move(self.game.board)
                set = tile.getContainer()
            else:
                tile.move(set)
        self.assertEqual(set.getSize(), 3)
        #assert that this set is valid
        self.assertTrue(set.isValid())

        #create an invalid (incomplete) set on the board
        set = None
        for i in range(4,6):
            tile = self.joe.plate.findTile(i, GameConstants.BLACK)
            self.assertIsNotNone(tile)
            if not set:
                tile.move(self.game.board)
                set = tile.getContainer()
            else:
                tile.move(set)
        self.assertEqual(set.getSize(), 2)
        #assert that this set is NOT valid
        self.assertFalse(set.isValid())

        #a recursive check on the modification state of the entire model should return True at this point
        self.assertTrue(self.game.isModified(True))

        #the board should contain 2 sets
        self.assertEqual(len(self.game.board.sets),2)

        #now Joe commits the set he just put on the board
        self.joe.commitMoves()
        print(self.game.toString())

        #just the valid set should remain on the board (board contains 1 set)
        self.assertEqual(len(self.game.board.sets),1)

        modified = self.game.getModifiedObjects()
        print ("number of modified objects = ", len(modified))
        for mo in modified:
            print (type(mo))
            
        #a recursive check on the modification state of the entire model should return False at this point
        self.assertFalse(self.game.isModified(True))


        



if __name__ == '__main__':
    unittest.main()
    
