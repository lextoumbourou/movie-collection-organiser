import unittest
import cleanup
import glob
import os

class testCleanup(unittest.TestCase):
    def setUp(self):
        # Setup the folder to add dummy content
        self.path = "/tmp/cleanup_tests/"
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        # Add dummy content
        open(self.path+"Taxi.Driver.avi", "w").close()
        open(self.path+"Taxi.Driver-fanart.jpg", "w").close()
        open(self.path+"Jacob's Ladder.avi", "w").close()
        open(self.path+"Jacob's.Ladder.png", "w").close()
        open(self.path+"Long.Weekend.1978.DVDRip.XviD.avi", "w").close()
        open(self.path+"Jacob's.Ladder.srt", "w").close()

        cleanup.update_all_files(self.path)

    def testYearReturnsCorrectly(self):
        movie_name = cleanup.clean_movie_name("Taxi.Driver")
        title, year = cleanup.get_year(movie_name)
        self.assertEquals(year, 1976)

    def testUpdateAll(self):
        self.assertTrue(cleanup.has_year_in_brackets("Taxi Driver (2008).avi"))

    def ensureDirectoryExists(self):
        self.assertTrue(os.path.exists(self.path+"Taxi Driver (1976)"))

    #def tearDown(self):
    #    # Delete test folder
    #    for file in glob.glob(self.path+"*"):
    #        try:
    #            os.remove(file)
    #        except:
    #            os.rmdir(file)
    #    os.rmdir(self.path)

if __name__ == "__main__":
    unittest.main()
