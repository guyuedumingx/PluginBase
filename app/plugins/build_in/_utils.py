from app.plug import *
import pandas as pd
import numpy as np

@Plug.register('_pandas_show')
class PandasShow(Plugin):
    """
    显示一个pandas DataFrame
    data: DataFrame
    """
    def process(self, data: pd.DataFrame, **kwargs):
        return Plug.run(plugins=("_tableUI",),
                               columns=data.columns.values,
                               data=data.values.tolist(),
                               **kwargs)