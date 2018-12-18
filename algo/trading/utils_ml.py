import pandas as pd

def remove_id_index(X_close):
    X_close = X_close.copy().reset_index()
    X_close = X_close.drop(['id_cryptocompare'], axis=1)
    X_close = X_close.set_index('timestamp')
    return X_close

def format_both_close_prices(X_train, X_test, id_cryptocompare):
    return format_close_prices(X_train, id_cryptocompare), format_close_prices(X_test, id_cryptocompare)

def format_close_prices(X_, id_cryptocompare):
    X_ = pd.DataFrame(X_)
    X_ = remove_id_index(X_.query('id_cryptocompare == "' + id_cryptocompare + '"'))
    return X_.close_price