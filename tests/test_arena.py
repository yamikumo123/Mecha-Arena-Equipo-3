import unittest
from src.services.arena_service import Arena, FLOOR

IDLE = [{}, {}]

class ArenaTests(unittest.TestCase):
    def near(self):
        arena = Arena()
        arena.fighters[0].x = 500
        arena.fighters[1].x = 584
        return arena

    def advance(self, arena, seconds, controls=None):
        for _ in range(round(seconds / .01)):
            arena.step(.01, controls or IDLE)

    def test_light_attack_only_hits_once(self):
        arena = self.near()
        self.assertTrue(arena.strike(0, 'light'))
        self.advance(arena, .3)
        self.assertEqual(arena.fighters[1].robot.vida, 92)
        self.advance(arena, .4)
        self.assertEqual(arena.fighters[1].robot.vida, 92)

    def test_guard_reduces_damage(self):
        arena = self.near()
        arena.strike(0, 'light')
        self.advance(arena, .3, [{}, {'guard': True}])
        self.assertEqual(arena.fighters[1].robot.vida, 98)

    def test_combo_and_expiration(self):
        arena = Arena()
        for kind in ('light', 'light'):
            self.assertTrue(arena.strike(0, kind))
            self.advance(arena, .33)
        arena.strike(0, 'heavy')
        self.assertEqual(arena.fighters[0].attack.kind, 'finisher')
        self.advance(arena, 1.5)
        arena.strike(0, 'heavy')
        self.assertEqual(arena.fighters[0].attack.kind, 'heavy')

    def test_special_cost_and_projectile(self):
        arena = Arena()
        self.assertFalse(arena.strike(0, 'special'))
        arena.fighters[0].energy = 60
        self.assertTrue(arena.strike(0, 'special'))
        self.assertEqual(arena.fighters[0].energy, 0)
        self.advance(arena, 1.2)
        self.assertEqual(arena.fighters[1].robot.vida, 74)

    def test_jump_lands_and_cannot_double_jump(self):
        arena = Arena()
        arena.jump(0)
        self.advance(arena, .1)
        f = arena.fighters[0]
        self.assertLess(f.y, FLOOR)
        previous = f.vy
        arena.jump(0)
        self.assertEqual(f.vy, previous)
        self.advance(arena, 1)
        self.assertEqual(f.y, FLOOR)
        self.assertEqual(f.vy, 0)

    def test_simultaneous_knockout_is_draw(self):
        arena = self.near()
        for f in arena.fighters:
            f.robot.vida = 8
        arena.strike(0, 'light')
        arena.strike(1, 'light')
        self.advance(arena, .15)
        self.assertTrue(arena.finished)
        self.assertEqual(arena.winner, -1)
        self.assertEqual(arena.scores, [0, 0])

    def test_timeout_and_reset(self):
        arena = Arena()
        arena.remaining = .01
        arena.fighters[1].robot.vida = 70
        arena.step(.02, IDLE)
        self.assertEqual(arena.winner, 0)
        arena.step(.02, IDLE)
        self.assertEqual(arena.scores, [1, 0])
        arena.reset()
        self.assertEqual(arena.scores, [1, 0])
        self.assertEqual(arena.fighters[1].robot.vida, 100)
        self.assertFalse(arena.finished)

    def test_movement_bounds_and_body_collision(self):
        arena = Arena()
        self.advance(arena, 3, [{'right': True}, {'left': True}])
        self.assertGreaterEqual(abs(arena.fighters[0].x - arena.fighters[1].x), 82)
        self.advance(arena, 5, [{'left': True}, {'right': True}])
        self.assertGreaterEqual(arena.fighters[0].x, 65)
        self.assertLessEqual(arena.fighters[1].x, 1135)

if __name__ == '__main__':
    unittest.main()
