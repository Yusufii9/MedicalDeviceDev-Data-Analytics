import pandas as pd
import numpy as np

from tsfresh import extract_features
from tsfresh.utilities.dataframe_functions import impute

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

from matplotlib import pyplot as plt

import warnings

warnings.filterwarnings('ignore')


def preprocess_df(df):
    processed_df_list = []

    grouped = df.groupby(['SensorCart', 'Channel'])

    for group_name, group_data in grouped:
        time_series = group_data['SensorCartAge'].to_list()
        response_series = group_data['Slope'].to_list()

        temp_df = pd.DataFrame(
            {'SensorCart_Channel': ['{}_{}'.format(group_name[0], group_name[1])] * len(time_series),
             'Time': time_series,
             'Response': response_series})

        processed_df_list.append(temp_df)

    processed_df = pd.concat(processed_df_list,
                             ignore_index=True)

    return processed_df


def remove_outliers(df, k):
    q3, q1 = np.percentile(df['Response'], [75, 25])
    iqr = q3 - q1

    df['Outlier'] = df['Response'].apply(
        lambda x: 'Outlier' if ((q1 - k * iqr) > x or (q3 + k * iqr) < x) else 'Include')

    return df


def clean_data(path_to_raw_csv,
               analyte,
               fluid_name,
               k=1):
    raw_df = pd.read_csv(path_to_raw_csv)
    raw_df['DeviceType'] = raw_df['DeviceSN'].apply(lambda x: x[:3]) 

    raw_df = raw_df[
        (raw_df['HasSlope'] == 'Yes') &
        (raw_df['Timestamp'] > '2023-03-01') &
        (raw_df['DeviceType'] == 'BB4') &
        (raw_df['Analyte'] == analyte) &
        (raw_df['Name'] == fluid_name) &
        ((raw_df['SensorCartAge'] > 50) & (raw_df['SensorCartAge'] < 730))]

    df = preprocess_df(raw_df)

    processed_df = remove_outliers(df, k)



    return processed_df.to_csv('SlopeData_{}_{}_{}.csv'.format(analyte, fluid_name, k),
                               index=False)


def cluster_data(path_to_processed_df,
                 analyte,
                 fluid_name,
                 k):

    df = pd.read_csv(path_to_processed_df)
    df = df[df["Outlier"] == 'Include']
    df.drop("Outlier", inplace=True, axis=1)
    extracted_features = extract_features(df, column_id='SensorCart_Channel', column_sort='Time')
    imputed_features = impute(extracted_features)
    filtered_features = imputed_features.loc[:, imputed_features.var() != 0]
    linkage_matrix = linkage(filtered_features, 'ward')

    dendrogram(linkage_matrix, labels=filtered_features.index)
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('Sample index')
    plt.ylabel('Distance')
    plt.show()

    distance = float(input("Enter Distance: "))

    clusters = fcluster(linkage_matrix, distance, criterion='distance')
    filtered_features['Cluster'] = clusters
    clustered_df = pd.merge(df, filtered_features['Cluster'], left_on='SensorCart_Channel', right_index=True)
    clustered_df.to_csv('ClusteredData_{}_{}_{}_{}.csv'.format(analyte, fluid_name, distance, k), index=False)


if __name__ == '__main__':
    clean_data(r'C:\Users\z004mybr\Documents\Time Series\ViewMEGAResultsDiff.csv',
               'pH',
               '2PT_CAL',
               0.5)

    cluster_data(path_to_processed_df='SlopeData_pH_2PT_CAL.csv',
                 analyte='pH',
                 fluid_name='2PT_CAL',
                 k=0.5)
