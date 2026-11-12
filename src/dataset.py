import os
import json
class Dataset:
    def __init__(self):
        p = os.getcwd()
        if 'src' in p:
            p.removesuffix('project')
        d = os.path.join(p,'dataset')
        p = os.path.join(p,'users.json')
        self.DATASET = d
        if not os.path.isdir(d):
            os.makedirs(d)
        self.URL = p
        self.data = {}
        self.load()

    def load(self):
        with open(self.URL,'rb') as f:
            self.data = json.load(f)

    def save(self):
        json_data = json.dumps(self.data)
        with open(self.URL,'wb') as f:
            f.write(json_data.encode('utf-8'))

    def add_user(self,name:str):
        new = self.data['next']
        self.data['users'][f'{new}']=name
        self.data['next']=new+1
        d = os.path.join(self.DATASET,str(new))
        if not os.path.isdir(d):
            os.makedirs(d)
        self.save()
        return(d)

    def __str__(self):
        resp = ""
        for u in self.data['users']:
            resp += f'{f'ID:{u}':<8}| Usuário: {self.data['users'][u]}\n'
        return resp
        

        
