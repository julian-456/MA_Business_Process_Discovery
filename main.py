import pandas as pd
import pm4py
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.log.importer.xes import importer as xes_importer
from log_statitics import Log_Statistics
from cherry_picker import Cherry_Picker
from edge_Filter import Edge_Filter
from model_statistics import Model_Statistics
from pm4py.objects.conversion.dfg import converter as dfg_converter

def import_csv(file_path):
    event_log = pd.read_csv(file_path)
    event_log = pm4py.format_dataframe(event_log, case_id='_CASE_KEY', activity_key='ACTIVITY_EN', timestamp_key='EVENTTIME')
    return event_log

def activity_sequences_to_csv(event_log):
    activity_sequences = event_log.groupby('case:concept:name')['concept:name'].apply(list).reset_index(name='activity_sequence')
    activity_sequences.to_csv('./results/csvs/activity_sequences.csv', index=False)
    return activity_sequences


def export_xes(event_log, output_name):
    # Export to XES
    pm4py.write_xes(event_log, './results/xes/' + output_name + '.xes')
    return event_log


def null_checker(event_log):
    # Null Checker
    null_values = event_log.isnull().sum()
    null_columns = null_values[null_values > 0].index.tolist()
    if null_columns:
        print(f"Null values found in columns: {null_columns}")
    else:
        print("No null values found in the event log.")
    return null_columns

def create_csv_without_null(csv_path, output_name):
    df = pd.read_csv(csv_path)
    # Remove rows with null values
    df_no_null = df.dropna(axis=1, how='any')
    # Save the cleaned DataFrame to a new CSV file
    df_no_null.to_csv(f'./results/csvs/{output_name}_no_null.csv', index=False)
    return df_no_null
    


if __name__ == "__main__":
    # Setting up paths 
    results_path = './results/'
    models_path = results_path + 'models/'
    xes_path = results_path + 'xes/'
    csvs_path = results_path + 'csvs/'
    data_path = './data/'
    tgf_path = results_path + 'tgfs/'

    event_log_name_csv = 'example.csv'
    event_log_name_xes = 'BPI_Challenge_2012.xes'
    
    # # Importing xes and converting to event_log
    event_log = pm4py.read_xes(data_path + event_log_name_xes)


    # Importing CSVs and converting to event_log
    # event_log = import_csv(data_path + event_log_name_csv)
    
    # # Creating Log Statistics
    log_statistics = Log_Statistics(event_log)
    log_statistics.export_statistics_to_txt(results_path + event_log_name_xes[:-4] +'.txt')
    
   

    # # Cherry_Picker 
    # Cherry Picker (0.8-1.0) - variant
    cherry_picker_log = Cherry_Picker(event_log, activity_range=[(0.8, 1.0)], path_range=[(0.8, 1.0)]).new_log
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(cherry_picker_log)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.save(gviz, models_path + 'cherry_picker_' + '08_1' + '.png')
    m_stat = Model_Statistics(event_log, net, initial_marking, final_marking, 'cherry_picker_' + '08_1', results_path)
    m_stat.calculate_statistics()

    # Cherry Picker (0.6-1.0) - variant
    cherry_picker_log = Cherry_Picker(event_log, activity_range=[(0.6, 1.0)], path_range=[(0.6, 1.0)]).new_log
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(cherry_picker_log)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.save(gviz, models_path + 'cherry_picker_' + '06_1' + '.png')
    m_stat = Model_Statistics(event_log, net, initial_marking, final_marking, 'cherry_picker_' + '06_1', results_path)
    m_stat.calculate_statistics()

    # Cherry Picker (0.2-1.0) - variant
    cherry_picker_log = Cherry_Picker(event_log, activity_range=[(0.2, 1.0)], path_range=[(0.2, 1.0)]).new_log
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(cherry_picker_log)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.save(gviz, models_path + 'cherry_picker_' + '02_1' + '.png')
    m_stat = Model_Statistics(event_log, net, initial_marking, final_marking, 'cherry_picker_' + '02_1', results_path)
    m_stat.calculate_statistics()

    # Cherry Picker (0.2-0.4; 0.8-1.0) - variant
    cherry_picker_log = Cherry_Picker(event_log, activity_range=[(0.2,0.4),(0.8, 1.0)], path_range=[(0.2,0.4),(0.8, 1.0)]).new_log
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(cherry_picker_log)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.save(gviz, models_path + 'cherry_picker_' + '02_04' + ', 08_1'+ '.png')
    m_stat = Model_Statistics(event_log, net, initial_marking, final_marking, 'cherry_picker_' + '02_04' + ', 08_1', results_path)
    m_stat.calculate_statistics()

    # Edge Filter
    # Edge_Filter - TWE variant
    edge_filter = Edge_Filter(event_log, results_path, "Celonis")
    edge_filter.write_tgf_from_log()
    edge_filter.use_edge_filter("--twe")  # Using the TWE variant for edge filtering
    edge_filter.dfg = edge_filter.tgf_to_dfg()
    edge_filter.print_dfg_to_png()

    # DFG to Petri Net
    #  Removing Start and End activities from DFG für Precision calculation
    edge_filter_dfg_no_start_end = {k: v for k, v in edge_filter.dfg.items() if "Start" not in k and "End" not in k}
    net, initial_marking, final_marking = dfg_converter.apply(edge_filter_dfg_no_start_end)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.save(gviz, models_path + 'edge_filter_twe' + '.png')
    m_stat = Model_Statistics(event_log, net, initial_marking, final_marking, "edge_filter_twe", results_path)
    m_stat.calculate_statistics()
    


    # Edge_Filter - Greedy variant
    edge_filter = Edge_Filter(event_log, results_path, "Celonis")
    edge_filter.write_tgf_from_log()
    edge_filter.use_edge_filter("--g")  # Using the TWE variant for edge filtering
    edge_filter.dfg = edge_filter.tgf_to_dfg()
    edge_filter.print_dfg_to_png()

    # DFG to Petri Net
    #  Removing Start and End activities from DFG für Precision calculation
    edge_filter_dfg_no_start_end = {k: v for k, v in edge_filter.dfg.items() if "Start" not in k and "End" not in k}
    net, initial_marking, final_marking = dfg_converter.apply(edge_filter_dfg_no_start_end)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.save(gviz, models_path + 'edge_filter_g' + '.png')
    m_stat = Model_Statistics(event_log, net, initial_marking, final_marking, "edge_filter_g", results_path)
    m_stat.calculate_statistics()



    # Edge_Filter - tweg variant
    edge_filter = Edge_Filter(event_log, results_path, "Celonis")
    edge_filter.write_tgf_from_log()
    edge_filter.use_edge_filter("--tweg")  # Using the TWE variant for edge filtering
    edge_filter.dfg = edge_filter.tgf_to_dfg()
    edge_filter.print_dfg_to_png()

    # DFG to Petri Net
    #  Removing Start and End activities from DFG für Precision calculation
    edge_filter_dfg_no_start_end = {k: v for k, v in edge_filter.dfg.items() if "Start" not in k and "End" not in k}
    net, initial_marking, final_marking = dfg_converter.apply(edge_filter_dfg_no_start_end)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.save(gviz, models_path + 'edge_filter_tweg' + '.png')
    m_stat = Model_Statistics(event_log, net, initial_marking, final_marking, "edge_filter_tweg", results_path)
    m_stat.calculate_statistics()



    # Inductive Miner
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(event_log)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.save(gviz, models_path + 'inductive_miner_' + 'Celonis' + '.png')
    m_stat = Model_Statistics(event_log, net, initial_marking, final_marking, "Celonis_inductive", results_path)
    m_stat.calculate_statistics()


    

    
    
