from database.parco_DAO import ParcoDAO
from database.escursione_DAO import EscursioneDAO
from database.punto_interesse_DAO import PuntoInteresseDAO
from model import punto_interesse
from model.escursione import Escursione


class Model:
    def __init__(self):
        # Dizionari: chiave = ID, valore = oggetto Python.
        # .values() permette di scorrere direttamente gli oggetti.

        # _pacchetto_ottimo: lista della combinazione migliore.
        # _valore_ottimo: voto massimo trovato (-1 inizialmente).
        # _costo: costo della migliore combinazione.

        # Gli attributi self. appartengono all'oggetto Model
        # e sono accessibili dagli altri metodi della stessa istanza.

        # Prima carico Escursioni e PuntiInteresse dal database.
        # Poi load_relazioni() collega gli oggetti tra loro.

        self.escursioni_map = {} # Mappa ID escursione -> oggetti Escursione
        self.punti_interesse_map = {} # Mappa ID punto di interesse -> oggetti PuntoInteresse

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_escursioni()
        self.load_punti_interesse()
        self.load_relazioni()

    @staticmethod
    def load_parchi():
        """ Restituisce tutti i parchi disponibili """
        return ParcoDAO.get_parchi()

    def load_escursioni(self):
        """ Carica tutte le escursioni in un dizionario [id, Escursione]"""
        self.escursioni_map = EscursioneDAO.get_escursioni()

    def load_punti_interesse(self):
        """ Carica tutti i punti di interesse in un dizionario [id, PuntoInteresse]"""
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra escursioni e punti di interesse e salvarle nelle strutture dati
            Collega escursione <-> punti di interesse.
            --> Ogni Escursione ha un set di PuntoInteresse.
            --> Ogni PuntoInteresse ha un set di Escursioni.
        """
        # TODO
        # ORM - RELAZIONE MOLTI A MOLTI (N:N)
        # Il DAO restituisce una lista di dizionari contenenti
        # gli ID delle escursioni e dei punti di interesse.

        # Scorro ogni relazione con un for e utilizzo gli ID
        # come chiavi per recuperare gli oggetti dai dizionari.

        # Collego gli oggetti in entrambe le direzioni:
        # Escursione -> set di PuntoInteresse
        # PuntoInteresse -> set di Escursione

        # Uso .add() perché gli attributi sono set.
        # Non serve return: modifico direttamente gli oggetti
        # già contenuti nei dizionari del Model

        relazioni= EscursioneDAO.get_escursioni_punti_interesse()

        for relazione in relazioni:
            escursione_ogg = self.escursioni_map[relazione["id_escursione"]]
            punto_interesse_ogg = self.punti_interesse_map[relazione["id_punto_interesse"]]
            escursione_ogg.punti_interesse.add(punto_interesse_ogg)
            punto_interesse_ogg.escursioni.add(escursione_ogg)

    def genera_pacchetto(self, id_parco: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto di escursioni ottimale per un parco rispettando i vincoli di durata, budget e punti di interesse unici.
        :param id_parco: id del parco
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Escursione)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il voto complessivo dei visitatori per il pacchetto)
        """
        # PREPARAZIONE DELLA RICORSIONE
        # Azzero i risultati precedenti per iniziare una nuova ricerca.
        # Salvo budget e giorni come attributi self. per utilizzarli
        # anche dentro _ricorsione().

        # Creo self._escursioni_parco, lista delle escursioni candidate.
        # Uso .values() per scorrere gli oggetti del dizionario.

        # Seleziono solo le escursioni del parco scelto che
        # rispettano singolarmente i limiti di giorni e budget.

        # None significa nessun limite.
        # Uso OR: accetto se il limite non esiste OPPURE è rispettato.

        # Non conosco ancora il pacchetto ottimo: sarà la ricorsione
        # a determinarlo confrontando le combinazioni.

        # Avvio _ricorsione(0, [], 0, 0, 0, set()):
        # indice 0, pacchetto vuoto, giorni/costo/voto a zero
        # e nessun punto di interesse utilizzato.

        # Al termine restituisco pacchetto, costo e voto migliore.

        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        self._escursioni_parco = []

        self._max_giorni = max_giorni
        self._max_budget = max_budget


        for escursione in self.escursioni_map.values():
            if escursione.id_parco == id_parco:
                if max_budget is None or escursione.costo <= max_budget:
                    if max_giorni is None or escursione.durata_giorni <= max_giorni:
                        self._escursioni_parco.append(escursione)

        self._ricorsione(0, [], 0, 0, 0, set())

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, punti_usati: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il voto complessivo dei visitatori"""

        # RICORSIONE CON BACKTRACKING

        # PARAMETRI:
        # start_index: indice da cui cercare le prossime escursioni.
        # pacchetto_parziale: lista delle escursioni già selezionate.
        # durata_corrente: giorni totali utilizzati.
        # costo_corrente: costo totale del pacchetto parziale.
        # valore_corrente: somma dei voti ottenuta finora.
        # punti_usati: set dei punti di interesse già visitati.

        # CONTROLLO SOLUZIONE
        # Se valore_corrente supera _valore_ottimo, salvo
        # il nuovo voto, il costo e una COPIA del pacchetto.
        # .copy() evita che i successivi pop() modifichino
        # anche la soluzione migliore già salvata.

        # CONTROLLO VINCOLI
        # Scarto con continue le escursioni che superano
        # giorni o budget oppure ripetono punti di interesse.
        # Uso AND: scarto se il limite ESISTE E viene superato.

        # intersection() verifica se due set hanno punti comuni.
        # Se l'intersezione non è vuota, scarto l'escursione.

        # AGGIUNTA ESCURSIONE
        # Con append() aggiungo l'escursione al pacchetto.
        # Calcolo il voto sommando voto_visitatori dei suoi punti.
        # Con union() creo un nuovo set di punti utilizzati,
        # senza modificare quello precedente.

        # CHIAMATA RICORSIVA
        # Richiamo _ricorsione() con indice i+1, pacchetto
        # aggiornato, nuovi giorni, costo, voto e punti usati.

        # BACKTRACKING
        # Quando la ricorsione termina, uso pop() per rimuovere
        # l'ultima escursione e provare altre combinazioni.
        # Non devo ripristinare gli altri valori perché passo
        # nuove somme e union() crea un nuovo set.

        # TERMINAZIONE:
        # Quando non ci sono altri indici da esplorare,
        # il for termina e la funzione ritorna automaticamente.

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
        if valore_corrente >  self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()
            self._costo = costo_corrente

        for i in range(start_index,  len(self._escursioni_parco)):
            escursione = self._escursioni_parco[i]
            #controlli su giorni bughet e durata
            if self._max_giorni is not None and escursione.durata_giorni + durata_corrente > self._max_giorni:
                continue

            if punti_usati.intersection(escursione.punti_interesse):
                continue

            if self._max_budget is not None and escursione.costo + costo_corrente > self._max_budget:
                continue

            pacchetto_parziale.append(escursione)

            #aggiorniamo dati
            nuovi_punti = punti_usati.union(escursione.punti_interesse)

            voto_escursione = 0

            for punto in escursione.punti_interesse:
                voto_escursione += punto.voto_visitatori

            self._ricorsione(i+1, pacchetto_parziale, durata_corrente + escursione.durata_giorni, costo_corrente + escursione.costo, valore_corrente + voto_escursione, nuovi_punti)

            '''
            aggiorniamo i dati
            durata_corrente += escursione.durata_giorni
            costo_corrente += escursione.costo
            nuovi_punti = punti_usati.union(escursione.punti_interesse)
            
            voto_escursione= 0
            
            for punto in escursione.punti_interesse:
                voto_escursione += punto.voto_visitatori
            '''

            #backtracking
            pacchetto_parziale.pop()