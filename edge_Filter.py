from pm4py.statistics.start_activities.log import get as start_activities_get
from pm4py.statistics.end_activities.log import get as end_activities_get
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.discovery.dfg.algorithm import Variants
from pm4py.visualization.dfg import visualizer as dfg_visualization
from pm4py.objects.conversion.dfg import converter as dfg_converter
from pm4py.visualization.petri_net import visualizer as pn_visualizer
import subprocess

class Edge_Filter:

    def __init__(self, event_log, results_path, log_name):
        self.event_log = event_log
        self.results_path = results_path
        self.log_name = log_name
        self.pre_tgf_path = self.results_path + 'tgfs/' + log_name + '_pre.tgf'
        self.post_tgf_path = self.results_path + 'tgfs/' + log_name + '_post.tgf'
        self.dfg = None
        
        

    def write_tgf_from_log(self):
        
        start_acts = start_activities_get.get_start_activities(self.event_log)
        end_acts = end_activities_get.get_end_activities(self.event_log)

        # DFG erstellen (häufigkeitsbasiert)
        dfg = dfg_discovery.apply(self.event_log, variant=Variants.FREQUENCY)

        # Aktivitätenmenge extrahieren
        activities = set()
        for (a, b) in dfg:
            activities.add(a)
            activities.add(b)
        activities.update(start_acts.keys())
        activities.update(end_acts.keys())

        # IDs zuweisen (Start = 0, End = max+1)
        activity_to_id = {"Start": 0}
        for idx, act in enumerate(sorted(activities), start=1):
            activity_to_id[act] = idx
        activity_to_id["End"] = len(activity_to_id)

        # Rückwärts-Mapping für Klarheit (optional)
        # id_to_activity = {v: k for k, v in activity_to_id.items()}

        # TGF-Datei schreiben
        with open(self.pre_tgf_path, "w", encoding="utf-8") as f:
            # Knoten
            for act, idx in activity_to_id.items():
                f.write(f"{idx} {act}\n")
            f.write("#\n")
            # DFG-Kanten mit Gewicht
            for (a, b), freq in dfg.items():
                f.write(f"{activity_to_id[a]} {activity_to_id[b]} {freq}\n")
            # Kanten von zentralem Start
            for act, freq in start_acts.items():
                f.write(f"{activity_to_id['Start']} {activity_to_id[act]} {freq}\n")
            # Kanten zum zentralen End
            for act, freq in end_acts.items():
                f.write(f"{activity_to_id[act]} {activity_to_id['End']} {freq}\n")

    def use_edge_filter(self, variant="--twe"):
        
        jar_path = "MA_PD/edge_filter/dfg-edge-filtering-1.0.jar"
        java_args = ["-jar", jar_path, variant, "-r", self.pre_tgf_path, self.post_tgf_path]

        # Java ausführen
        try:
            result = subprocess.run(["java"] + java_args, capture_output=True, text=True, check=True)
            print("Ausgabe der .jar-Datei:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("Fehler beim Ausführen der .jar-Datei:")
            print(e.stderr)


    def tgf_to_dfg(self):
        dfg = {}
        id_to_label = {}
        

        with open(self.post_tgf_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()

        sep_index = lines.index('#')
        node_lines = lines[:sep_index]
        edge_lines = lines[sep_index+1:]

        # Knoten lesen
        for line in node_lines:
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                node_id, label = parts
                id_to_label[node_id] = label

        # Kanten lesen und als DFG speichern
        for line in edge_lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                src_id, tgt_id = parts[:2]
                weight = float(parts[2]) if len(parts) == 3 else 1 
                src = id_to_label.get(src_id)
                tgt = id_to_label.get(tgt_id)
                if src is not None and tgt is not None:
                    dfg[(src, tgt)] = weight
        return dfg


    def print_dfg_to_png(self):
        # DFG in eine PNG-Datei speichern
        gviz = dfg_visualization.apply(self.dfg)
        # dfg_visualization.view(gviz)
        dfg_visualization.save(gviz, self.results_path + 'models/' + 'dfg_after_edge_filter_'+ self.log_name+ 'BPI_Challenge_2012.png')

    
    
    
