import flet as ft

from model.model import Model
from UI.view import View
from UI.controller import Controller


def main(page: ft.Page):
    my_model = Model()
    my_view = View(page)
    my_controller = Controller(my_view, my_model)
    my_view.set_controller(my_controller)
    my_view.load_interface()


ft.run(main)


# LAB09 - PACCHETTI ESCURSIONISTICI

# OBIETTIVO: trovare la combinazione di escursioni con
# il voto totale più alto, rispettando giorni, budget
# e assenza di punti di interesse duplicati.
#
# DAO: recuperano i dati dal database.
# DTO: rappresentano i dati come oggetti Python.
# ORM: collega Escursioni e PuntiInteresse (relazione N:N).
# RICORSIONE: esplora le combinazioni possibili.
# BACKTRACKING: torna indietro per provare altre soluzioni.