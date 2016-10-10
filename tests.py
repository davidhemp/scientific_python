import unittest

class SavingTests(unittest.TestCase):
    def setUp(self):
        import numpy
        import saving

    def test_IO(self):
        x = numpy.array(range(1000), dtype=float)
        y = x**2
        saving.save_data([x,y], filename="testcase_data.txt")
        data = saving.load_data("testcase_data.txt")
        for i in range(1000):
            self.assertEqual(data.x[i], x[i])
            self.assertEqual(data.y[i], y[i])


def run():
    unittest.main()z

if __name__ == '__main__':
    run()
