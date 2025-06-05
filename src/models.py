class Graphique:
    def __init__(self):
        self.nom = ""
        self.type_score = ""
        self.variables = []
        self.donnees = Donnees("")
        self.modele_ia = ModeleIA("")
        
    def ajouter_variable(self, var:str):
        self.variables.append(var)
        
    def supprimer_variable(self, var:str):
        self.variables.remove(var)
        
    def modifier_typer_score(self, type:str):
        self.type_score = type

    def modifier_donnees(fichier):
        pass
    
    def generer():
        pass
    
class Donnees:
    def __init__(self, fichier):
        pass
    
class ModeleIA:
    def __init__(self, type_score:str):
        pass
    
    def analyser(texte:str):
        pass