
# Imports
from scipy.spatial.distance import cdist
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from collections import Counter
import matplotlib.pyplot as plt
import scipy.stats as st
import seaborn as sb
import pandas as pd
import numpy as np
import random
import math
import sys
import os

# Globals
device_categories = {
    'hub': [
        'd0-52-a8-00-67-5e', 
        '44-65-0d-56-cc-d3'
    ],
    'camera': [
        '70-ee-50-18-34-43',
        'f4-f2-6d-93-51-f1',
        '00-16-6c-ab-6b-88',
        '30-8c-fb-2f-e4-b2',
        '00-62-6e-51-27-2e',
        'e8-ab-fa-19-de-4f',
        '00-24-e4-11-18-a8'
    ],
    'switch': [
        'ec-1a-59-79-f4-89',
        '50-c7-bf-00-56-39',
        '74-c6-3b-29-d7-1d',
        'ec-1a-59-83-28-11'
    ],
    'air_quality': [
        '18-b4-30-25-be-e4',
        '70-ee-50-03-b8-ac'
    ],
    'healthcare': [
        '00-24-e4-1b-6f-96',
        '74-6a-89-00-2e-25',
        '00-24-e4-20-28-c6'
    ],
    'lightbulbs': [
        'd0-73-d5-01-83-08'
    ],
    'electronics': [
        '18-b7-9e-02-20-44',
        'e0-76-d0-33-bb-85',
        '70-5a-0f-e4-9b-c0'
    ],
    'non_iot': [
        '00-24-e4-10-ee-4c',
        '08-21-ef-3b-fc-e3',
        '14-cc-20-51-33-ea',
        '30-8c-fb-b6-ea-45',
        '40-f3-08-ff-1e-da',
        '74-2f-68-81-69-42',
        '8a-05-81-fa-cc-14',
        'ac-bc-32-d4-6f-2f',
        'b4-ce-f6-a7-a3-c2',
        'd0-a6-37-df-a1-e1',
        'd2-13-91-23-2a-58',
        'f4-5c-89-93-cc-85'
    ]
}

device_names = {
    # IoT
    'd0-52-a8-00-67-5e': 'Smart_Things',
    '44-65-0d-56-cc-d3': 'Amazon_Echo',
    '70-ee-50-18-34-43': 'Netatmo_Welcome',
    'f4-f2-6d-93-51-f1': 'TP-Link_Day_Night_Cloud_Camera',
    '00-16-6c-ab-6b-88': 'Samsung_SmartCam',
    '30-8c-fb-2f-e4-b2': 'Dropcam',
    '00-62-6e-51-27-2e': 'Insteon_Camera_wired',
    'e8-ab-fa-19-de-4f': 'Insteon_Camera_wireless',
    '00-24-e4-11-18-a8': 'Withings_Smart_Baby_Monitor',
    'ec-1a-59-79-f4-89': 'Belkin_Wemo_Switch',
    '50-c7-bf-00-56-39': 'TP-Link_Smart_Plug',
    '74-c6-3b-29-d7-1d': 'iHome',
    'ec-1a-59-83-28-11': 'Belkin_Wemo_motion_sensor',
    '18-b4-30-25-be-e4': 'NEST_Protect_smoke_alarm',
    '70-ee-50-03-b8-ac': 'Netatmo_weather_station',
    '00-24-e4-1b-6f-96': 'Withings_smart_scale',
    '74-6a-89-00-2e-25': 'Blipcare_blood_pressure_meter',
    '00-24-e4-20-28-c6': 'Withings_aura_sleep_sensor',
    'd0-73-d5-01-83-08': 'LiFX_Smart_bulb',
    '18-b7-9e-02-20-44': 'Triby_speaker',
    'e0-76-d0-33-bb-85': 'PIX-STAR_photo_frame',
    '70-5a-0f-e4-9b-c0': 'HP_printer',
    # non-IoT
    '00-24-e4-10-ee-4c': 'non-iot_1',
    '08-21-ef-3b-fc-e3': 'non-iot_Smartphone',
    '14-cc-20-51-33-ea': 'non-iot_Laptop',
    '30-8c-fb-b6-ea-45': 'non-iot_2',
    '40-f3-08-ff-1e-da': 'non-iot_3',
    '74-2f-68-81-69-42': 'non-iot_4',
    '8a-05-81-fa-cc-14': 'non-iot_5',
    'ac-bc-32-d4-6f-2f': 'non-iot_6',
    'b4-ce-f6-a7-a3-c2': 'non-iot_7',
    'd0-a6-37-df-a1-e1': 'non-iot_8',
    'd2-13-91-23-2a-58': 'non-iot_9',
    'f4-5c-89-93-cc-85': 'non-iot_10'
}

def assign_category(device):
    for k, v in device_categories.items():
        if device in v:
            return k
    print('Warning: no category found for device "{}"'.format(device))
    return 'no_category_found'

def is_iot(device):
    iot_cats = {x:device_categories[x] for x in device_categories if x!='non_iot'}
    return any(device in l for l in iot_cats.values())

def mac_to_name(mac):
    return device_names[mac]

########################
# Train on N-1 devices #
########################
# Classify device category
def cycle_remove_devices(data, device_categories):
    bags = []
    prob_preds = []
    for c, ds in device_categories.items():
        for d in ds:
            # Train/test split
            train = data[data['device']!=d]
            test = data[data['device']==d]
            # Train
            features = df.columns[2:-1]
            clf = DecisionTreeClassifier(criterion='entropy')
            clf.fit(train[features], train['device_category'])
            # Test
            ps = clf.predict(test[features])
            gt = assign_category(d)
            bags.insert(0, {
                'device': mac_to_name(d),
                'ground_truth': gt,
                'accuracy': len([p for p in ps if p==gt])/len(ps),
                'consensus': Counter(ps).most_common(1)[0][0]
            })
            for row in clf.predict_proba(test[features]):
                dev_dict = dict(zip(clf.classes_, row))
                dev_dict['device'] = d
                dev_dict['ground_truth'] = c
                prob_preds.insert(0, dev_dict)
    return bags, prob_preds


# Classify IoT v. non-IoT
def cycle_remove_devices_binary(data, device_categories):
    bags = []
    prob_preds = []
    for c, ds in device_categories.items():
        for d in ds:
            # Train/test split
            train = data[data['device']!=d]
            test = data[data['device']==d]
            # Train
            features = df.columns[2:-1]
            clf = DecisionTreeClassifier(criterion='entropy')
            y = train['device_category']!='non_iot'
            clf.fit(train[features], y)
            # Test
            print(d)
            ps = clf.predict(test[features])
            gt = assign_category(d)
            bags.insert(0, {
                'device': mac_to_name(d),
                'ground_truth': gt,
                'accuracy': clf.score(test[features], test['device_category']!='non_iot'),
                'consensus': Counter(ps).most_common(1)[0][0]
            })
            for row in clf.predict_proba(test[features]):
                dev_dict = dict(zip(clf.classes_, row))
                dev_dict['device'] = d
                dev_dict['ground_truth'] = c
                prob_preds.insert(0, dev_dict)
    return bags, prob_preds


###############
# 70/30 split #
###############
# Classify device categories
def holdout(data, device_names, n=10):
    runs = []
    for i in range(n):
        # Train/test split
        holdout_devices = random.sample(list(device_names.keys()), 7)
        train = data[~data['device'].isin(holdout_devices)]
        test = data[data['device'].isin(holdout_devices)]
        # Train
        features = df.columns[2:-1]
        clf = DecisionTreeClassifier(criterion='entropy')
        clf.fit(train[features], train['device_category'])
        # Test
        score = clf.score(test[features], test['device_category'])
        runs.insert(0, {
            'devices': holdout_devices,
            'accuracy': score
        })
    return runs


# Classify IoT v. non-IoT
def holdout_binary(data, device_names, n=20):
    runs = []
    for i in range(n):
        # Train/test split
        holdout_devices = random.sample(list(device_names.keys()), 7)
        train = data[~data['device'].isin(holdout_devices)]
        test = data[data['device'].isin(holdout_devices)]
        # Train
        features = df.columns[2:-1]
        clf = DecisionTreeClassifier(criterion='entropy')
        clf.fit(train[features], train['device_category']!='non_iot')
        # Test
        score = clf.score(test[features], test['device_category']!='non_iot')
        runs.insert(0, {
            'devices': holdout_devices,
            'accuracy': score
        })
    return runs


########
# Main #
########
if __name__=='__main__':
    if len(sys.argv) == 1:
        sys.exit('Please provide the input CSV file as the first argument')
    # Set up the dataframe
    # Read in the csv
    df = pd.read_csv(sys.argv[1])
    # Drop NaN values
    df.fillna(df.groupby('device').mean(), inplace=True)
    df.fillna(df.mean(), inplace=True)
    # Add device categories
    df['device_category'] = df.apply(lambda row: assign_category(row['device']), axis=1)

    #
    # N-1
    #
    # IoT v. non-IoT
    # Get the results
    bin_bags, bin_prob_preds = cycle_remove_devices_binary(df, device_categories)

    # Put the consensus results in a readable dataframe
    bin_bag_cols = ['device', 'ground_truth', 'consensus', 'accuracy']
    bin_bag_df = pd.DataFrame(bin_bags)[bin_bag_cols].sort_values(by='accuracy').reset_index(drop=True)

    # Put the probabilities of each category for each device in a readable df
    bin_prob_df = pd.DataFrame(bin_prob_preds).sort_values(by=['ground_truth', 'device']).reset_index(drop=True)
    bin_prob_cols = ['device', 'ground_truth', True, False]
    bin_prob_df = bin_prob_df[bin_prob_cols]

    print('N-1 IoT v. non-IoT consensus:')
    print(bin_bag_df.round(decimals=3))
    print('----------------------------------')

    print('N-1 IoT v. non-IoT category probabilities:')
    print(bin_prob_df.round(decimals=3))
    print('----------------------------------')

    #
    # 70/30
    #
    # IoT v. non-IoT
    # Get the results
    bin_holdout_df = pd.DataFrame(holdout_binary(df, device_names))
    # Replace mac addresses of the holdout devices with device names
    bin_holdout_df['devices'] = bin_holdout_df['devices'].apply(lambda d: [mac_to_name(x) for x in d])
    # Report the holdout devices in their own columns
    bin_holdout_df[['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7']] = pd.DataFrame([x for x in bin_holdout_df.devices])
    # Get rid of the holdout devices column
    bin_holdout_df = bin_holdout_df.drop('devices', axis=1)

    print('70/30 IoT v. non-IoT results of each run:')
    print(bin_holdout_df)
    print('----------------------------------')

    clf = DecisionTreeClassifier(criterion='entropy')
    clf.fit(df[df.columns[2:-1]], df['device_category']!='non_iot')
    print('IoT v. non-IoT feature importances:')
    for ft, imp in zip(df.columns[2:-1], clf.feature_importances_):
        print('{0}: {1:.3f}'.format(ft, imp))
    print('----------------------------------')
    from sklearn import tree
    tree.export_graphviz(clf, 
        out_file='non-v-iot.dot',
        feature_names=df.columns[2:-1],
        class_names=['IoT' if c else 'non-IoT' for c in clf.classes_])

    clf = DecisionTreeClassifier(criterion='entropy')
    clf.fit(df[df.columns[2:-1]], df['device_category'])
    print('Device category feature importances:')
    for ft, imp in zip(df.columns[2:-1], clf.feature_importances_):
        print('{0}: {1:.3f}'.format(ft, imp))
    print('----------------------------------')
    tree.export_graphviz(clf, 
        out_file='dev-cat.dot', 
        feature_names=df.columns[2:-1],
        class_names=clf.classes_)

    print('Execution finished')
