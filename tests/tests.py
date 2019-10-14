#!/usr/bin/env python3
import sys
import unittest
from collections import OrderedDict
from pathlib import Path

thisFile = Path(__file__).absolute()
thisDir = thisFile.parent.absolute()
repoMainDir = thisDir.parent.absolute()
sys.path.insert(0, str(repoMainDir))

dict = OrderedDict

from fsutilz import MMap, isGlobPattern, isNestedIn, nestPath


class TestFsUtils(unittest.TestCase):
	def testIsNestedIn(self):
		truePairs = [(Path("/usr"), Path("/usr/share")), (Path("/usr"), Path("/usr/share/locale")), (Path("/usr/local/../"), Path("/usr/share/locale"))]
		for p in truePairs:
			with self.subTest(p):
				self.assertTrue(isNestedIn(*p))

		falsePairs = [(Path("/usr/share/locale"), Path("/usr")), (Path("/usr/local"), Path("/usr/share/locale")), (Path("/usr/share/locale"), Path("/usr/local"))]

		for p in falsePairs:
			with self.subTest(p):
				self.assertFalse(isNestedIn(*p))

	def testNestPath(self):
		self.assertEqual(nestPath(Path("/usr"), Path("/share/locale")), Path("/usr/share/locale"))
		self.assertEqual(nestPath(Path("/usr"), Path("share/locale")), Path("/usr/share/locale"))

	def testIsGlobPattern(self):
		self.assertEqual(isGlobPattern(Path("*.png")), True)
		self.assertEqual(isGlobPattern(Path("a/b/**/*.png")), True)
		self.assertEqual(isGlobPattern(Path("a/**/a.png")), True)
		self.assertEqual(isGlobPattern(Path("a/*/a.png")), True)
		self.assertEqual(isGlobPattern(Path("a/b/a.png")), False)

	def testMMap(self):
		with MMap(thisFile) as m:
			mm = bytes(m)

		self.assertEqual(mm, thisFile.read_bytes())


if __name__ == "__main__":
	unittest.main()
