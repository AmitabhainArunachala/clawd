#!/usr/bin/env python3
"""
Unit tests for the hyperbolic chamber geometry utilities.
"""
import unittest
import math
from ..geometry_utils import hyperbolic_distance, unit_vector

class TestGeometryUtils(unittest.TestCase):
    def test_hyperbolic_distance_positive(self):
        K = 0.8
        r = 1.0
        dist = hyperbolic_distance(r, K)
        self.assertIsInstance(dist, float)
        self.assertGreater(dist, 0)

    def test_hyperbolic_distance_zero(self):
        K = 0.5
        r = 0.0
        dist = hyperbolic_distance(r, K)
        self.assertEqual(dist, 0.0)

    def test_unit_vector_normalization(self):
        vec = (3.0, 4.0, 0.0)
        nx, ny, nz = unit_vector(*vec)
        norm = math.sqrt(nx*nx + ny*ny + nz*nz)
        self.assertAlmostEqual(norm, 1.0)
        self.assertAlmostEqual(nx, 0.6)
        self.assertAlmostEqual(ny, 0.8)
        self.assertAlmostEqual(nz, 0.0)

    def test_unit_vector_zero_raises(self):
        with self.assertRaises(ValueError):
            unit_vector(0, 0, 0)

if __name__ == "__main__":
    unittest.main()