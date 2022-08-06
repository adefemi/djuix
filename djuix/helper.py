from random import SystemRandom
import string
import re


class Helper:

    @staticmethod
    def normalizer_request(data):
        try:
            data._mutable = True
            result = data.dict()
        except:
            result = data

        return result

    @staticmethod
    def generate_random_string(length):
        return ''.join(SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length))

    @staticmethod
    def camelToSnake(word):
        return re.sub('(?!^)([A-Z]+)', r'_\1', word).lower()
    
    staticmethod
    def camelToSnakeDash(word):
        return re.sub('(?!^)([A-Z]+)', r'-\1', word).lower()
    
    @staticmethod
    def handleException(excep):
        print(excep)
        raise Exception(excep) 
