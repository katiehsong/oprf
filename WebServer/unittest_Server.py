import Server
import unittest

class TestRs(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.server = Server.Server()
        cls.usernames = ["Hello", "Hippo", "Husky"]
        cls.passwords = ["Kitty", "HippoHippo", "Northeastern"]
            
        for i in range(len(cls.usernames)):
            cls.server.addUser(cls.usernames[i], cls.passwords[i])
            
    def test_addUser(self):
        count = len(self.usernames)
        self.assertEqual(count, len(self.server.users))
        self.server.addUser("Lion", "rawrrr")
        self.assertEqual(count + 1, len(self.server.users))
    
    def test_RPower(self):
        for i in range(len(self.usernames)):
            rPower = self.server.computeRPower(self.usernames[i], self.passwords[i])        
            self.assertEqual(self.server.getHash(self.usernames[i], self.passwords[i]),
                             self.server.reverseRPower(self.usernames[i], rPower))


if __name__ == "__main__":
    unittest.main()
