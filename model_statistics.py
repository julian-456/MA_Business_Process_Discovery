from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
from collections import Counter


class Model_Statistics:
    def __init__(self, event_log, net, initial_marking, final_marking, model_name, results_path):
        self.event_log = event_log
        self.net = net
        self.initial_marking = initial_marking
        self.final_marking = final_marking
        self.model_name = model_name
        self.results_path = results_path

    def calculate_statistics(self):
        # Fitness mit Token-Replay
        fitness_result = token_replay.apply(self.event_log, self.net, self.initial_marking, self.final_marking)
        fitness = sum([trace["trace_fitness"] for trace in fitness_result]) / len(fitness_result)

        # Generalization
        generalization = generalization_evaluator.apply(self.event_log, self.net, self.initial_marking, self.final_marking)

        # Precision
        precision = precision_evaluator.apply(self.event_log, self.net, self.initial_marking, self.final_marking, variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)
        # for testing purposes
        # precision = 0

        # Simplicity
        simplicity = simplicity_evaluator.apply(self.net)

        # Strukturmetriken
        num_places = len(self.net.places)
        num_transitions = len(self.net.transitions)
        num_invisible_transitions = len([t for t in self.net.transitions if t.label is None])
        num_arcs = len(self.net.arcs)
        num_nodes = num_places + num_transitions

        # Model Density
        model_density = num_arcs / (num_nodes * (num_nodes - 1)) if num_nodes > 1 else 0

        # Average Connector Degree (ACD)
        all_nodes = list(self.net.places) + list(self.net.transitions)
        total_degree = 0
        for node in all_nodes:
            indegree = len([arc for arc in self.net.arcs if arc.target == node])
            outdegree = len([arc for arc in self.net.arcs if arc.source == node])
            total_degree += indegree + outdegree
        average_connector_degree = total_degree / len(all_nodes) if all_nodes else 0



        print("Fitness:", fitness)
        print("Generalization:", generalization)
        print("Precision:", precision)
        print("Simplicity:", simplicity)
        print("Anzahl Places:", num_places)
        print("Anzahl Transitions:", num_transitions)
        print("Anzahl unsichtbarer Transitionen:", num_invisible_transitions)
        print("Anzahl Knoten:", num_nodes)
        print("Anzahl Kanten:", num_arcs)
        print("Average Connector Degree (ACD):", average_connector_degree)
        print("Model Density:", model_density)

        self.write_metrics_to_file(fitness, generalization, precision,
                                 simplicity, num_nodes, num_arcs, average_connector_degree, model_density)
        

    def write_metrics_to_file(self, fitness, generalization, precision, simplicity,
                         num_nodes, num_arcs, average_connector_degree, model_density):
        
        transition_labels = [t.label if t.label else "invisible" for t in self.net.transitions]
        label_counts = Counter(transition_labels)

        filepath = self.results_path + 'model_statistics/' + self.model_name + '_statistics.txt'
        with open(filepath, 'w') as file:
            file.write(f"Fitness: {fitness}\n")
            file.write(f"Generalization: {generalization}\n")
            file.write(f"Precision: {precision}\n")
            file.write(f"Simplicity: {simplicity}\n")
            file.write(f"Anzahl Places: {len(self.net.places)}\n")
            file.write(f"Anzahl Transitions: {len(self.net.transitions)}\n")
            file.write(f"Anzahl unsichtbarer Transitionen: {len([t for t in self.net.transitions if t.label is None])}\n")
            file.write(f"Anzahl Knoten: {num_nodes}\n")
            file.write(f"Anzahl Kanten: {num_arcs}\n")
            file.write(f"Average Connector Degree (ACD): {average_connector_degree}\n")
            file.write(f"Model Density: {model_density}\n")

            file.write("\n")
            file.write("\nTransitionstypen:\n")
            for label, count in label_counts.items():
                file.write(f"{label}: {count}\n")