import pm4py
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.statistics.traces.generic.log import case_statistics
from pm4py.objects.log.obj import EventLog, Trace


######################################################################
# Disclaimer: 
# This code is based on the following GitHub repository:
#  - https://github.com/MaxVidgof/cherry-picker
#  and has been adapted to the needs of this work.
#
# The corresponding scientific paper can be accessed at the following 
# link: https://doi.org/10.1007/978-3-030-49418-6_9
######################################################################

class Cherry_Picker:
    def __init__(self, event_log, path_range, activity_range):
        self.event_log = event_log
        self.path_range = self.merge_overlapping_ranges(path_range)
        self.activity_range = self.merge_overlapping_ranges(activity_range)
        self.new_log = self.cherry_picking()

        

    def merge_overlapping_ranges(self, ranges):
        # Sortiere die Bereiche nach dem Startwert
        sorted_ranges = sorted(ranges, key=lambda x: x[0])
        merged = []

        for current in sorted_ranges:
            if not merged:
                merged.append(current)
            else:
                last = merged[-1]
                if current[0] <= last[1]:
                    # überlappende Bereiche zusammenfassen
                    merged[-1] = (last[0], max(last[1], current[1]))
                else:
                    merged.append(current)
        return merged
    
    def cherry_picking(self):
        # get all variants and sort them by their frequency
        variants = variants_filter.get_variants(self.event_log)
        variants_count = case_statistics.get_variant_statistics(self.event_log)
        variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=False)
        
        # checks if the ranges are valid
        # path_range = sorted(self.path_range, reverse=False)
        # for i in range(0,len(path_range)-1):
        #     if(path_range[i][1] > path_range[i+1][0]):
        #         print("THROW EXCEPTION: Overlapping range")

        # select the variants
        nr_variants = len(variants_count)
        idx = [(round(x*nr_variants), round(y*nr_variants)) for (x,y) in self.path_range]
        
        # Flatten the list of lists of the ranges into a single list
        variants_subset = [variants_count[x:y+1] for (x,y) in idx] 
        flatten = lambda l: [item for sublist in l for item in sublist]
        variants_subset = flatten(variants_subset)
        
        # select the variants and filter the log
        filtered_variants = {k:v for k,v in variants.items() if k in [x["variant"] for x in variants_subset]}
        filtered_log = variants_filter.apply(self.event_log, filtered_variants)
        

        # overwrite the variants variable with the variants of the filtered log
        variants = variants_filter.get_variants(filtered_log)

        # count variants and sort them by their frequency
        variants_count = case_statistics.get_variant_statistics(filtered_log)
        variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=False)
        
        # count the activities per variant
        activities = dict()
        for variant in variants_count:
            for activity in variant["variant"]:
                if (activity not in activities.keys()):
                    activities[activity] = variant["count"]
                else:
                    activities[activity] += variant["count"]

        # sort the activities by their frequency
        sorted_activities = {k: v for k, v in sorted(activities.items(), key=lambda item: item[1])}
        activities_sorted_list = list(sorted_activities)
        

        # select the activities
        nr_activities = len(activities_sorted_list)
        idx = [(round(x*nr_activities), round(y*nr_activities)) for (x,y) in self.activity_range]
        activities_to_keep = [activities_sorted_list[x:y+1] for (x,y) in idx]
        activities_to_keep = flatten(activities_to_keep)
        
        # select the variants that contain the selected activities
        variants_idx = []
        for i in range(len(variants_count)):
            for activity in activities_to_keep:
                if (activity in variants_count[i]["variant"] and (i not in variants_idx)):
                    variants_idx.append(i)
                    
        # select the variants and filter the log
        variants_subset = [variants_count[i] for i in variants_idx]
        filtered_variants = {k:v for k,v in variants.items() if k in [x["variant"] for x in variants_subset]}
        filtered_log = variants_filter.apply(filtered_log, filtered_variants)
        

        # create a new event log with the selected activities
        new_log = EventLog()
        for trace in filtered_log:
            new_trace = Trace()
            for event in trace:
                if event['concept:name'] in activities_to_keep:
                    new_trace.append(event)
            if len(new_trace) > 0:
                new_log.append(new_trace)
        

        used_paths = 0
        for lower, higher in self.path_range:
            used_paths += round((higher-lower)*100)
            
        print(f"Using {used_paths}% of paths. {100-used_paths}% of paths are discarded.")

        used_activities = 0
        for lower, higher in self.activity_range:
            used_activities += round((higher-lower)*100)
            
        print(f"Using {used_activities}% of activities in remaining paths. {100-used_activities}% of activities are discarded.")

        return new_log

