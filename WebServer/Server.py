import pandas as pd
from os import urandom, path
import hashlib
import OPRF
import Constants


oprf = OPRF.OPRF()

class Server:
    def __init__(self):
        self.users = {}
        self.filename = Constants.SERVER_FILENAME
        self.servername = Constants.SERVER_NAME
        self.importCSV()

    def addUser(self, username, password):
        # Registers the user in the system.

        if self.existName(username):
            return False

        salt = urandom(32).hex()
        self.users[username] = {'Salt': salt, 'F_Output': ""}
        return True

    def getHash(self, input):
        # Returns H(pw || salt).

        return hashlib.sha256(input).hexdigest()

    def computeOutput(self, username, password):
        # Computes and returns H(pw || salt)^r.

        salt = bytes.fromhex(self.users[username]['Salt'])
        hashed = self.getHash(password.encode("utf-8") + salt)
        return oprf.raiseToR(hashed)

    def addF(self, name, f):
        # Stores the F_Output for the new user, where f equals H(pw || salt)^{rk} and F_Output equals H(pw || salt)^k.

        self.users[name]['F_Output'] = oprf.reverseR(f)
        dfList = [(name, self.users[name]['Salt'], self.users[name]['F_Output'])]
        df = pd.DataFrame(dfList)
        file_exists = path.exists(self.filename)
        df.to_csv(self.filename, mode='a', header=not file_exists, index=False)

    def userLogin(self, username, f):
        return self.users[username]['F_Output'] == oprf.reverseR(f)

    def dummyReverseF(self, f):
        return oprf.reverseR(f)

    def exportCSV(self):
        dfList = [(name, attributes['Salt'], attributes['F_Output']) for name, attributes in self.users.items()]
        df = pd.DataFrame(dfList, columns=['Username', 'Salt', 'F_Output'])
        df.to_csv(self.filename, index=False)

    def importCSV(self):
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

    def updateR(self):
        # Updates r.

        if oprf.updateKey():
            return True
        return False

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
