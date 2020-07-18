import unittest
from model import *

class ModelTestMethods(unittest.TestCase):

    def test_AddTilesToSet(self):
        set = Set()
        t = Tile(1, GameConstants.BLACK, 1, set)
        self.assertEqual(set.addTile(t), 1)
        self.assertEqual(len(set.tiles), 1)
        #attempt to add same tile to the set again, it should fail (addTile returns 0)
        self.assertEqual(set.addTile(t), 0)

    def test_AddWrongTileToSet(self):
        set = Set()
        # add black 1,2,3 to the set
        for v in range(1,4):
            t = Tile(v, GameConstants.BLACK, v, set)
            t.print()
            self.assertEqual(set.addTile(t), v)
        # attempt to add black 5 to the set, it should fail (addTile returns 0)
        self.assertEqual(set.addTile(Tile(5, GameConstants.BLACK, 5, set)), 0)

    def test_AddTileToFullSet(self):
        set = Set()
        i = 1
        for c in GameConstants.TILECOLORS:
            t = Tile(i, c, 1, set)
            self.assertEqual(set.addTile(t), i)
            i+=1
        # attempt to add another black 1 to the set, it should fail (addTile returns 0)
        self.assertEqual(set.addTile(Tile(5, GameConstants.BLACK, 1, set)), 0)

    def test_AddJoker(self):
        set = Set()
        i = 1
        for c in GameConstants.TILECOLORS:
            t = Tile(i, c, 1, set)
            self.assertEqual(set.addTile(t), i)
            i+=1
        # attempt to add a joker to the set, it should not fail (addTile returns a position >0)
        self.assertNotEqual(set.addTile(Joker(5, GameConstants.BLACK, set)), 0)

    def test_MoveTileFromPileToBoard(self):
        game = Game(2)
        pileSizeBefore = len(game.pile.tiles)
        tile = game.pile.findTile(1, GameConstants.BLACK)
        self.assertIsNotNone(tile)
        tile.move(game.board)
        self.assertEqual(len(game.board.sets), 1)
        pileSizeAfter = len(game.pile.tiles)
        self.assertEqual(pileSizeBefore-pileSizeAfter, 1)

    def test_AddPlayer(self):
        game = Game(2)
        game.addPlayer("Joe")
        joe = game.getPlayer("Joe")
        self.assertIsNotNone(joe)

    def test_PickTile(self):
        game = Game(2)
        game.addPlayer("Joe")
        joe = game.getPlayer("Joe")

        plateSizeBefore = len(joe.plate.tiles)
        joe.pickTile()
        plateSizeAfter = len(joe.plate.tiles)
        self.assertEqual(plateSizeAfter-plateSizeBefore, 1)

    def test_BoardCleanUp(self):
        game = Game(2)
        game.addPlayer("Joe")
        joe = game.getPlayer("Joe")

        for tId in joe.plate.tiles:
            t = joe.plate.tiles[tId]
            t.move(game.board)
            self.assertEqual(len(game.board.sets), 1)
            game.board.cleanUp()
            self.assertEqual(len(game.board.sets), 0)

            #break after first iteration, we only needed to test this for a single tile on Joe's plate
            break



if __name__ == '__main__':
    unittest.main()

