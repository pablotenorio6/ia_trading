from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.compose import ColumnTransformer
import pandas as pd
import time
import joblib
import logging

from labelling import labelling_data
import utils as ut

mapping_dict = {'Gap-Buy': True, 'Buy': True, 'Gap-Sell': False, 'Sell': False, 'Threshold Limit': False}

models = {'DecisionTree': DecisionTreeClassifier(min_samples_leaf=4),
          'RandomForest': RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_split=5, min_samples_leaf=3, random_state=42),
          'GradientBoosting': GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3)}


def get_all_data(file_number: int) -> pd.DataFrame:
    df = pd.concat([pd.read_csv(f'labelled_data/202{i}_labelled_data.csv') for i in range(1, file_number)])
    return df


def model_score(y_test, y_pred) -> pd.DataFrame():
    matrix = confusion_matrix(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    return pd.DataFrame([{'matrix': matrix, 'accuracy': accuracy, 'precision': precision, 'recall': recall,'f1_score': f1}])


def model_training(model_type: str, df: pd.DataFrame) -> pd.DataFrame():
    ## Limit training to data from hours between 10 am and 4 pm, to reduce noise
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df[(df['timestamp'].dt.hour >= 10) & (df['timestamp'].dt.hour < 16)]

    df = df[~df['buy-sl'].isin(['Gap-Buy', 'Gap-Sell', 'Threshold Limit'])]
    df['buy-sl'] = df['buy-sl'].map(mapping_dict)

    ## Then we discretize features (+1, -1)
    # df = ut.discretize_features(df)
    scaler = ColumnTransformer(transformers=[
        ('minmax', MinMaxScaler(), ['RSI']),
        ('standard', StandardScaler(), ['MACD', 'EMA', 'MOM'])
    ])
    ## Chose features tu train
    features = df[['RSI', 'MACD', 'EMA', 'MOM']]
    features_scaled = scaler.fit_transform(features)
    target = df['buy-sl']

    x_train, x_test, y_train, y_test = train_test_split(features_scaled,
                                                        target.values,
                                                        test_size=0.2,
                                                        random_state=42)
    obj = models[model_type]
    _ = obj.fit(features_scaled, target.values)
    importances = obj.feature_importances_
    for feature, importance in zip(['RSI', 'MACD', 'EMA', 'MOM'], importances):
        print(f"{feature}: {importance:.2f}")
    # y_pred = obj.predict(x_test)
    # df_pred = model_score(y_test, y_pred)
    # df_pred['name'] = model_type
    joblib.dump(scaler, f'trained_models/{model_type}_scaler_2.pkl')
    joblib.dump(obj, f'trained_models/{model_type}_trained_2.pkl')
    return  df


def model_testing(model_path:str, scaler_path:str, df:pd.DataFrame()):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df[(df['timestamp'].dt.hour >= 10) & (df['timestamp'].dt.hour < 16)]
    # First we get model and scaler to try
    scaler = joblib.load(scaler_path)
    ml_model= joblib.load(model_path)

    # Get features and predict results
    features = df[['RSI', 'MACD', 'EMA', 'MOM']]
    y_pred = ml_model.predict(scaler.transform(features))
    df['model_prediction'] = y_pred

    # Transform original df into score results
    # df = df[~df['buy-sl'].isin(['Gap-Buy', 'Gap-Sell', 'Threshold Limit'])]
    df['buy-sl'] = df['buy-sl'].map(mapping_dict)
    test_df = model_score(df['buy-sl'], df['model_prediction'])
    logging.info('Testing done')


if __name__ == '__main__':
    ## We get the full data labelling raw data
    # total_data = labelling_data(total_data)
    # total_data = pd.read_csv('labelled_data/total_data_labelled.csv')

    ## Model Training
    # filtered_data = total_data[~total_data['buy-sl'].isin(['Gap-Buy', 'Gap-Sell', 'Threshold Limit'])]
    # filtered_data['buy-sl'] = filtered_data['buy-sl'].map(mapping_dict)
    # filtered_data_resume = model_training(model_type='RandomForest', scaler_path='', df=filtered_data)

    ## Model testing
    total_data = get_all_data(5)
    labelling_data(total_data, 1)
    df_train, df_test = train_test_split(total_data, test_size=0.2, random_state=42)
    model_training(model_type='RandomForest', df = df_train)
    model_testing(model_path='trained_models/RandomForest_trained_2.pkl', scaler_path='trained_models/RandomForest_scaler_2.pkl', df = df_test)
    time.sleep(60)