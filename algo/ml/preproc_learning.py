import pandas as pd
import pytz

from datetime import datetime, timedelta

from ml.preproc_load import PreprocLoad
from ml.preproc_prepare import PreprocPrepare
from ml.utils_ml import save_obj

from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA


pd.options.mode.chained_assignment = None  # default='warn'
utc=pytz.UTC


#Calcul y + split data
class PreprocLearning:

    @staticmethod
    def get_global_datasets_for_cryptos(connection, ids_cryptocompare_crypto):
        dict_df = {}
        for id_crypto in ids_cryptocompare_crypto:
            print('Crypto : ' + str(id_crypto))
            try:
                df = PreprocPrepare.get_global_dataset_for_crypto(connection, id_crypto)
                if df.empty:
                    print('ALERT : Empty dataframe')
                else:
                    dict_df[str(id_crypto)] = df
            except Exception as e:
                print('ERROR : get_global_dataset_for_crypto() for crypto : ' + str(id_crypto))
                print(str(e))

        return dict_df

    @staticmethod
    def get_global_datasets_for_top_n_cryptos(connection, top_n=20):
        # TODO : To be passed in args
        df = PreprocLoad.get_dataset_ids_top_n_cryptos(connection, top_n)
        return PreprocLearning.get_global_datasets_for_cryptos(connection, df.id_cryptocompare.tolist())

    @staticmethod
    def calcul_values_of_y(df, dict_hours_labels, increase_target_pct):
        increase_target_pct = increase_target_pct / 100

        for key in dict_hours_labels:
            label_value = 'y_+' + dict_hours_labels[key] + '_value'
            label_classif = 'y_+' + dict_hours_labels[key] + '_classif'
            # calcul several y searched (value)
            df[label_value] = df.close_price.shift(-key)

            # perform calcul to use binary classification
            if increase_target_pct > 0:
                df[label_classif] = ((df[label_value] - df['close_price']) / df['close_price']) >= increase_target_pct
            else:
                df[label_classif] = ((df[label_value] - df['close_price']) / df['close_price']) <= increase_target_pct

        return df

    @staticmethod
    def do_split_data(df_p, columns_nb_p, min_index, nb_days):
        date_split = min_index + timedelta(days=round(nb_days * 0.75))  # 75 / 25 %
        df_train = df_p[df_p.index.get_level_values(0) <= date_split]
        df_test = df_p[df_p.index.get_level_values(0) > date_split]

        # separe x,y
        X_train = df_train.iloc[:, range(0, columns_nb_p)]
        y_train = df_train.iloc[:, range(columns_nb_p, len(df_p.columns))]

        X_test = df_test.iloc[:, range(0, columns_nb_p)]
        y_test = df_test.iloc[:, range(columns_nb_p, len(df_p.columns))]

        return X_train, X_test, y_train, y_test

    @staticmethod
    # TODO : Do split learning specific / inference and learning standard
    def get_preprocessed_data_learning(dict_df, dict_hours_labels, close_price_increase_targeted, predict_only_one_crypto,
                                       do_scale=True, do_pca=True, id_cryptocompare=0, useless_features=None):
        if useless_features is None:
            useless_features = []
        columns_nb = 0
        df_new_dict = {}
        df_new_list = []

        min_index = utc.localize(datetime.max)
        max_index = utc.localize(datetime.min)

        # calcul y for each crypto
        columns = None
        for key_id_cryptocompare, df_one_crypto in dict_df.items():

            # delete useless columns if needed
            if len(useless_features) > 0:
                df_one_crypto = df_one_crypto.drop(useless_features, axis=1)

            if columns is None:
                columns = df_one_crypto.columns

            # used to be able to split the dataset between train & test data
            mini = df_one_crypto.index.get_level_values(0).min()
            maxi = df_one_crypto.index.get_level_values(0).max()
            if mini < min_index:
                min_index = mini
            if maxi > max_index:
                max_index = maxi

            # number of columns before adding y values - could be done once only
            columns_nb = len(df_one_crypto.columns)

            # calcul all y values we are interested in and add it to the dataframe
            df_one_crypto = PreprocLearning.calcul_values_of_y(df_one_crypto.copy(),
                                                               dict_hours_labels, close_price_increase_targeted)

            # remove rows where y can't be calculed (need more data in the future)
            # TODO : Attention ! Ok pour testing mais pas pour production car on perd la data de la fin !
            df_one_crypto.dropna(subset=list(df_one_crypto.iloc[:, range(columns_nb, len(df_one_crypto.columns))]),
                                 inplace=True)

            df_new_dict[key_id_cryptocompare] = df_one_crypto
            df_new_list.append(df_one_crypto)

            # date to split dataset
        nb_days = (max_index - min_index).days

        # concat to get only one dataframe instead of a list of dataframes
        df_global = pd.concat(df_new_list).sort_index()

        # All cryptos
        X_train, X_test, y_train, y_test = PreprocLearning.do_split_data(df_global, columns_nb, min_index, nb_days)

        # One crypto
        if predict_only_one_crypto:
            # The one to predict
            X_train_one_crypto, X_test_one_crypto, y_train_one_crypto, \
                y_test_one_crypto = PreprocLearning.do_split_data(df_new_dict[id_cryptocompare], columns_nb,
                                                                  min_index, nb_days)
            X_test = X_test_one_crypto
            y_test = y_test_one_crypto

        # ------------------ PRE-PROCESSING ------------------ #

        X_train_close_price = X_train.close_price
        X_test_close_price = X_test.close_price

        # Scaling Data
        if do_scale:
            scaler = MinMaxScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

            # save scaler fo reuse with model
            save_obj(scaler, 'scaler_learning')
            save_obj('tmp_obj_learning')

        # PCA to reduce dimensionality
        if do_pca:
            pca = PCA(n_components=35)  # approx 97% variance
            X_train = pca.fit_transform(X_train)
            X_test = pca.transform(X_test)

            # save scaler fo reuse with model
            save_obj(pca, 'pca_learning')

        # re-index
        X_train = pd.DataFrame(X_train)
        X_train.index = y_train.index
        X_test = pd.DataFrame(X_test)
        X_test.index = y_test.index

        # retrieve columns name (useful for feature importance / feature engineering)
        if not do_pca:
            X_train.columns = columns
            X_test.columns = columns

        return X_train, X_test, y_train, y_test, X_train_close_price, X_test_close_price
