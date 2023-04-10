# Класс - надстройка над классом dict, упрощающий работу с множеством переменных, например класса
# простой переход от json к dict и обратно
# простое добавление и обновление значений переменных, удаление переменных
# made by korol4ik
import json

class Message:
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self(*args)

    def __call__(self,*args, **kwargs):
        if kwargs:
            self.__dict__.update(kwargs)
        if args:
            for jstr in args:
                self.json(jstr)
        return self.__dict__

    def __str__(self):
        return self.json()

    def __repr__(self):
        return self.json()

    def __getattr__(self,name):
        return None

    def json(self,_json=None):
        if not _json:
            return json.dumps(self.__dict__)
        else:
            try:
                _add = json.loads(_json)
                self(**_add)
                return json.dumps(self.__dict__)
            except Exception as e:
                print(f'can not update message from json {_json}, {e}')
    def rm(self, *args):  # list of keys
        for key in args:
            if key in self.__dict__:
                self.__dict__.pop(key)