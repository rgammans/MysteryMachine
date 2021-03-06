##From voidspace.org.uk  - RichCompare's test harness


from unittest import main, TestCase

from MysteryMachine.utils.RichCompare import RichComparisonMixin



class RichComparer(RichComparisonMixin):

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if not hasattr(other, 'value'):
            return self.value == other
        return self.value == other.value

    def __hash__(self, other):
        return hash(self.value)


    def __lt__(self, other):
        if not hasattr(other, 'value'):
            return self.value < other
        return self.value < other.value


class RichComparisonMixinTest(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.comp = RichComparer(6)

    def testDefaultComparison(self):
        self.assertRaises(NotImplementedError,
                          lambda: RichComparisonMixin() == 3)
        self.assertRaises(NotImplementedError,
                          lambda: RichComparisonMixin() != 3)
        self.assertRaises(NotImplementedError,
                          lambda: RichComparisonMixin() < 3)
        self.assertRaises(NotImplementedError,
                          lambda: RichComparisonMixin() > 3)
        self.assertRaises(NotImplementedError,
                          lambda: RichComparisonMixin() <= 3)
        self.assertRaises(NotImplementedError,
                          lambda: RichComparisonMixin() >= 3)


    def testEquality(self):
        self.assertTrue(self.comp == 6)
        self.assertTrue(self.comp == RichComparer(6))

        self.assertFalse(self.comp == 7)
        self.assertFalse(self.comp == RichComparer(7))

    def testInEquality(self):
        self.assertFalse(self.comp != 6)
        self.assertFalse(self.comp != RichComparer(6))

        self.assertTrue(self.comp != 7)
        self.assertTrue(self.comp != RichComparer(7))

    def testLessThan(self):
        self.assertTrue(self.comp < 7)
        self.assertTrue(self.comp < RichComparer(7))

        self.assertFalse(self.comp < 5)
        self.assertFalse(self.comp < RichComparer(5))

        self.assertFalse(self.comp < 6)
        self.assertFalse(self.comp < RichComparer(6))

    def testGreaterThan(self):
        self.assertTrue(self.comp > 5)
        self.assertTrue(self.comp > RichComparer(5))

        self.assertFalse(self.comp > 7)
        self.assertFalse(self.comp > RichComparer(7))

        self.assertFalse(self.comp > 6)
        self.assertFalse(self.comp > RichComparer(6))

    def testLessThanEqual(self):
        self.assertTrue(self.comp <= 7)
        self.assertTrue(self.comp <= RichComparer(7))
        self.assertTrue(self.comp <= 6)
        self.assertTrue(self.comp <= RichComparer(6))

        self.assertFalse(self.comp <= 5)
        self.assertFalse(self.comp <= RichComparer(5))

    def testGreaterThanEqual(self):
        self.assertTrue(self.comp >= 5)
        self.assertTrue(self.comp >= RichComparer(5))
        self.assertTrue(self.comp >= 6)
        self.assertTrue(self.comp >= RichComparer(6))

        self.assertFalse(self.comp >= 7)
        self.assertFalse(self.comp >= RichComparer(7))
        

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
