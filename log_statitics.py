import pm4py

class Log_Statistics:
    def __init__(self, event_log):
        self.event_log = event_log
        self.statistics = {}
        self.start_activities = {}
        self.end_activities = {}

        self.get_statistics()
        self.get_start_activities()
        self.get_end_activities()

    
    def get_statistics(self):
        # Anzahl der Events
        self.statistics['event_count'] = len(self.event_log)
        # Anzahl der Fälle
        self.statistics['case_count'] = self.event_log['case:concept:name'].nunique()
        # Anzahl der Aktivitäten
        self.statistics['activity_count'] = self.event_log['concept:name'].nunique()
        # Anzahl der Events pro Fall
        self.statistics['event_count_per_case'] = self.event_log.groupby('case:concept:name').size().describe()
        # Anzahl der Aktivitäten pro Fall
        self.statistics['activity_count_per_case'] = self.event_log.groupby('case:concept:name')['concept:name'].nunique().describe()
        print("Calculting log statistics was successful.")

    def get_start_activities(self):
        self.start_activities = pm4py.get_start_activities(self.event_log)
        print("Calculting start activities was successful.")

    def get_end_activities(self):
        self.end_activities = pm4py.get_end_activities(self.event_log)
        print("Calculting end activities was successful.")

    def export_statistics_to_txt(self, filename):
        with open(filename, 'w') as file:
            file.write("Log Statistics:\n")
            for key, value in self.statistics.items():
                file.write(f"{key}:\n{value}\n\n")

            file.write("Start Activities:\n")
            for activity, count in self.start_activities.items():
                file.write(f"{activity}: {count}\n")

            file.write("\nEnd Activities:\n")
            for activity, count in self.end_activities.items():
                file.write(f"{activity}: {count}\n")
        print(f"Statistics exported to {filename}")
