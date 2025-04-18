from random import randint
import pandas as pd
import gmpy2
import Constants

class OPRF:
    def __init__(self):
        self.__key = ""
        self.__inverseKey = ""
        self.__prime = Constants.PRIME
        self.__intPrime = int(self.__prime, 16)
        self.filename = Constants.OPRF_FILENAME
        self.importCSV() # try to load existing key from CSV

        if self.__key == "": # if no key, make a new one
            self.updateKey()

    def raiseToR(self, input):
        # Returns input^r where the input equals H(pw || salt).

        return hex(int(gmpy2.powmod(int(input, 16), int(self.__key, 16), self.__intPrime)))[2:]

    def reverseR(self, f):
        # Returns f^(1/r) where f equals H(pw || salt)^{rk}, i.e. returns H(pw || salt)^k.

        return hex(int(gmpy2.powmod(int(f, 16), int(self.__inverseKey, 16), self.__intPrime)))[2:]

    def updateOutput(self, f):
        # Returns input^(newR) where the input equals H(pw || salt) and f equals H(pw || salt)^k.

        newHash = gmpy2.powmod(int(f, 16), int(self.__inverseKey, 16), self.__intPrime)
        return hex(int(gmpy2.powmod(int(newHash), int(self.__key, 16), self.__intPrime)))[2:]

    def updateKey(self):
        while True:
            try:
                newKey = randint(1, self.__intPrime)
                newInverse = gmpy2.invert(newKey, self.__intPrime - 1)
                newKey = hex(newKey)[2:]
                if self.__key != newKey:
                    self.__inverseKey = hex(newInverse)[2:]
                    self.__key = newKey
                    df = pd.DataFrame([{'Key': self.__key, 'Inverse': self.__inverseKey}])
                    df.to_csv(self.filename, index=False)
                    return True
            except:
                continue

        return False

    def exportCSV(self):
        data = {'Key': self.__key, 'Inverse': self.__inverseKey}
        df = pd.DataFrame(data)
        df.to_csv(self.filename, index=False)

    def importCSV(self):
        df = pd.read_csv(self.filename)
        if df.empty or 'Key' not in df.columns or 0 not in df.index or pd.isna(df.loc[0, 'Key']):
            self.__key = ""
        else:
            self.__key = df.loc[0, 'Key']

        if df.empty or 'Inverse' not in df.columns or 0 not in df.index or pd.isna(df.loc[0, 'Inverse']):
            self.__inverseKey = ""
        else:
            self.__inverseKey = df.loc[0, 'Inverse']
