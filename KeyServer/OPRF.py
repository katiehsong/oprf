from random import randint
import pandas as pd
import gmpy2, os
import Constants

class OPRF:
    def __init__(self):
        self.__key = ""
        self.__inverseKey = ""
        self.__prime = Constants.PRIME
        self.__intPrime = int(self.__prime, 16)
        self.filename = Constants.OPRF_FILENAME
        self.importCSV()
        if self.__key == "" and self.updateKey():
            dfList = [(self.__key, self.__inverseKey)]
            df = pd.DataFrame(dfList)
            file_exists = os.path.exists(self.filename)
            df.to_csv(self.filename, mode='a', header=not file_exists, index=False)

    def raiseToK(self, input):
        # Returns input^k where the input equals H(pw || salt)^r.

        return hex(int(gmpy2.powmod(int(input, 16), int(self.__key, 16), self.__intPrime)))[2:]

    def updateKey(self):
        while True:
            try:
                newKey = randint(1, self.__intPrime)
                newInverse = gmpy2.invert(newKey, self.__intPrime - 1)
                newKey = hex(newKey)[2:]
                if self.__key != newKey:
                    if self.__key == "":
                        self.__inverseKey = hex(newInverse)[2:]
                    else:
                        oldInverse = gmpy2.invert(int(self.__key, 16), self.__intPrime - 1)
                        self.__inverseKey = hex(oldInverse)[2:]
                    self.__key = newKey
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
        if df.empty or 'Key' not in df.columns or 0 not in df.index or pd.notna(df.loc[0, 'Key']):
            self.__key = ""
        else:
            self.__key = df.loc[0, 'Key']

        if df.empty or 'Inverse' not in df.columns or 0 not in df.index or pd.notna(df.loc[0, 'Inverse']):
            self.__inverseKey = ""
        else:
            self.__inverseKey = df.loc[0, 'Inverse']
