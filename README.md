# Disclaimer

Dieses Repository wird für die Masterarbeit zum Thema "Ansätze der business Process Discover für Geschäftsprozesse mit vielen Varianten: Eine Literaturanalyse und praktische Evaluation" verwendet.  

Das Repository umfasst die Implementierungen der beiden Process Discovery Ansätze: Cherry Picker & Edge Filtering.
Beide wurden nicht vollständig selbst implementiert, sondern basieren auf den folgendenen Repositories:
-   Edge Filtering: https://github.com/david-chapela/dfg-edge-filtering
-   Cherry Picker:  https://github.com/MaxVidgof/cherry-picker

Darüber hinaus können anhand des Codes Statistiken zum Event Log und den resultierenden Modellen erzeugt werden.

Zusätzlich wurde eine Python-Datei geschrieben, die auf einen Ordner zugreift, für alle Event Logs im XES Format innerhalb dieses Ordners mit dem Induktive Miner Modelle erstellt, diese visualisiert und bewertet. Dies ist besonders für Clustering ALgorithmen hilfreich. Da in der Arbeit der ActiTraC-Ansatz untersucht wurde, heißt diese Datei: ActiTraC_statistic.py. 

# Abhängigkeiten
Die Implementierung wurde in der Python Version 3.13.3.  
Die nötigen Bibliotheken können über die requirements.txt installiert werden.

Für die Ausführung der JAR-Datei des Edge Filters wurde JRE-8 genutzt.  
Für die Visualisierung muss zusätzlich Graphviz installiert sein.


# Testen des Edge Filtering und Cherry Picking Ansatzes
Die beiden Ansätze können über die Main.py getestet werden.
Hierfür müssen zunächst die Pfade angepasst werden und die Datei im CSV oder XES Format in den Data Ordner gelegt werden. Im Fall einer CSV Datei kann es nötig sein, die relevanten Spalten in der entsprechenden Funktion anzupassen.  
Je nachdem ob eine CSV Datei oder XES Datei analysiert werden soll, muss der jeweils andere Code auskommentiert werden.

Anschließend können die verschiedenen voreingestellten Tests durchgeführt werden.


# Testen der ActiTraC_statistic.py
Wie zuvor beschrieben, dient dieses Programm der Analyse mehrere XES-Dateien. 
Um jedes Modell gegen das eigene Event Log zu testen, muss zu Beginn nur der Dateipfad angepasst werden. Für eine korrekte Benennung sollte ebenfalls die letzte Zeile angepasst werden.  
Für eine Ausgabe der Modelle als PNGs können die Zeilen 87 & 88 auskommentiert werden.



Für einen Evaluation des Modells gegen ein anderes Log - beispielsweise das Gesamtlog - können die Zeilen 30-33 verwendet werden. Auch hier muss ein korrekter Dateipfad angegeben werden.







