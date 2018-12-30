import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'


from sqlalchemy import create_engine



from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA

from ml.utils_ml import remove_outliers