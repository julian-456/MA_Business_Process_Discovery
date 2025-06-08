import os
import pandas as pd
import pm4py
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from collections import Counter



# Pfad zum Ordner mit Logs
log_folder = "data/ActiTraC/Standard_Parameter_Durchlauf"
# log_folder = "data/ProtoType Selection"

# Ergebnisse sammeln
results = []

# Alle Dateien im Ordner durchgehen
for filename in os.listdir(log_folder):
    if filename.endswith(".xes"):
        filepath = os.path.join(log_folder, filename)
        try:
            # Betrachtung Sub Log - Modell
            event_log = pm4py.read_xes(filepath)
            net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(event_log)

            # Betrachtung Gesamt Log - Modell
            # sub_log = pm4py.read_xes(filepath)
            # event_log = pd.read_csv("data/20250424104319_CELONIS_EXPORT.csv")
            # event_log = pm4py.format_dataframe(event_log, case_id='_CASE_KEY', activity_key='ACTIVITY_EN', timestamp_key='EVENTTIME')
            # net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(sub_log)

            # Unabhängig vom oberen Code-Block

            # Fitness mit Token-Replay
            fitness_result = token_replay.apply(event_log, net, initial_marking, final_marking)
            fitness = sum([trace["trace_fitness"] for trace in fitness_result]) / len(fitness_result)

            # Generalization
            generalization = generalization_evaluator.apply(event_log, net, initial_marking, final_marking)

            # Precision
            precision = precision_evaluator.apply(event_log, net, initial_marking, final_marking, variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)
            # for testing purposes
            # precision = 0

            # Simplicity
            simplicity = simplicity_evaluator.apply(net)

            # Strukturmetriken
            num_places = len(net.places)
            num_transitions = len(net.transitions)
            num_invisible_transitions = len([t for t in net.transitions if t.label is None])
            num_arcs = len(net.arcs)
            num_nodes = num_places + num_transitions

            # Model Density
            model_density = num_arcs / (num_nodes * (num_nodes - 1)) if num_nodes > 1 else 0

            # Average Connector Degree (ACD)
            all_nodes = list(net.places) + list(net.transitions)
            total_degree = 0
            for node in all_nodes:
                indegree = len([arc for arc in net.arcs if arc.target == node])
                outdegree = len([arc for arc in net.arcs if arc.source == node])
                total_degree += indegree + outdegree
            average_connector_degree = total_degree / len(all_nodes) if all_nodes else 0
        

            results.append({
                "filename": filename,
                "fitness": fitness,
                "generalization": generalization,
                "precision": precision,
                "simplicity": simplicity,
                "num_places": num_places,
                "num_transitions": num_transitions,
                "num_invisible_transitions": num_invisible_transitions,
                "num_nodes": num_nodes,
                "num_arcs": num_arcs,
                "model_density": model_density,
                "average_connector_degree": average_connector_degree
            })

            # gviz = pn_visualizer.apply(net, initial_marking, final_marking)
            # pn_visualizer.save(gviz, "data/ActiTraC/Standard_Parameter_Durchlauf/ActiTraC_Standard" + filename[:-4] + '.png')

        except Exception as e:
            print(f"Fehler beim Verarbeiten von {filename}: {e}")

# Als CSV speichern
df_results = pd.DataFrame(results)
df_results.to_csv("results/ActiTraC_standard_stat.csv", index=False)

