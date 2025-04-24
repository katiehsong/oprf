import pandas as pd
from os import urandom, path
from random import randint
import hashlib, gmpy2
import Constants


class Server:
    def __init__(self):
        self.users = {}
        self.filename = Constants.SERVER_FILENAME
        self.servername = Constants.SERVER_NAME
        self.importCSV()
        self.__temp_users = {}

    def addUser(self, username, password):
        # Registers the user in the system, by saving the username and salt.

        if self.existName(username):
            return False

        salt = self.getSalt()
        self.users[username] = {'Salt': salt, 'F_Output': ""}
        return True

    def getSalt(self):
        return urandom(32).hex()

    def getHash(self, username, password):
        # Returns H(pw || salt).

        salt = bytes.fromhex(self.users[username]['Salt'])
        return hashlib.sha256(password.encode("utf-8") + salt).hexdigest().zfill(64)

    def __setRs(self, username):
        '''
        Sets a temporary random r and its inverse mod PRIME for a user for sign-up/login process.
        Called in computeRPower function and deleted in either reverseRPower or addF via __popRs.
        '''
        while True:
            try:
                newKey = randint(1, Constants.INT_PRIME)
                self.__temp_users[username] = {
                    'inverseR': hex(int(gmpy2.invert(newKey, Constants.INT_PRIME - 1)))[2:],
                    'R': hex(newKey)[2:]
                    }
                return True
            except:
                continue
        return False

    def __popRs(self, username):
        '''
        Deletes the temporary random r and its inverse set in __setRs.
        Called in either reverseRPower.
        '''
        rInfo = self.__temp_users.pop(username)
        return rInfo['inverseR']

    def computeRPower(self, username, password):
        # Computes and returns H(pw || salt)^r, after setting r first.

        hashed = self.getHash(username, password)
        self.__setRs(username)
        rHex = self.__temp_users[username]['R']
        r = int(rHex, 16)
        return rHex, hex(int(gmpy2.powmod(int(hashed, 16), r, Constants.INT_PRIME)))[2:].zfill(64)

    def reverseRPower(self, username, f):
        # Returns f^(1/r) where f equals H(pw || salt)^{rk}, i.e. returns H(pw || salt)^k.
        rInverseHex = self.__popRs(username)
        inverseR = int(rInverseHex, 16)
        return rInverseHex, hex(int(gmpy2.powmod(int(f, 16), inverseR, Constants.INT_PRIME)))[2:].zfill(64)

    def addF(self, username, f):
        # Stores the F_Output for the new user, where f equals H(pw || salt)^{rk} and F_Output equals H(pw || salt)^k.
        self.users[username]['F_Output'] = self.reverseRPower(username, f)
        self.appendCSV(username)

    def appendCSV(self, username):
        if not self.filename or self.filename == "":
            return

        dfList = [(username, self.users[username]['Salt'], self.users[username]['F_Output'])]
        df = pd.DataFrame(dfList)
        file_exists = path.exists(self.filename)
        df.to_csv(self.filename, mode='a', header=not file_exists, index=False)

    def userLogin(self, username, f):
        return self.users[username]['F_Output'] == self.reverseRPower(username, f)

    def exportCSV(self):
        dfList = [(name, attributes['Salt'], attributes['F_Output']) for name, attributes in self.users.items()]
        df = pd.DataFrame(dfList, columns=['Username', 'Salt', 'F_Output'])
        df.to_csv(self.filename, index=False)

    def importCSV(self):
        if not self.filename or self.filename == "":
            return
        df = pd.read_csv(self.filename)
        self.users = df.set_index('Username').to_dict('index')

    def validData(self, name, password):
        if not name or not name.isalnum() or len(name) < 3 or len(password) < 4:
            return False
        return True

    def existName(self, name):
        if name not in self.users:
            return False
        return True

    '''
    def updateF(self):
        # Updates all H(pw || salt)^k after k changes.

            for name in self.users.keys():
                f = self.users[name]['F_Output']
                self.users[name]['F_Output'] = oprf.updateOutput(f)
            self.exportCSV()
            return True
        return False
    '''
