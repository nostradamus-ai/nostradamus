import math
import logging
import fbprophet
import pandas as pd

from datetime import datetime, timedelta

logger = logging.getLogger('models.prophet')

class Prophet(object):
    """ TBD """

    def __init__(self, 
                 train_df,
                 forecast_horizon,
                 forecast_frequency):
        self._failed = False
        self.train_df = train_df
        self.forecast_horizon = forecast_horizon
        self.forecast_frequency = forecast_frequency

        #calculate frequency in pandas format
        self.freq_value, self.freq_unit=self.calcUnit(self.forecast_frequency)            
        
        #calculate proper periods count with specified frequency
        self.periods = self.calcPeriods(
            self.forecast_frequency,
            self.forecast_horizon
        )
        logger.debug(
            f'Periods:{self.periods},Freq:{self.freq_value}{self.freq_unit}'
        )    

        # Choose proper growth function
        # In case of y values are below 1 then use logistic
        # Cap is max value +10% but not less than 1
        # Floor is min value -10%
        floor, cap = 0, 1
        max_val = float(self.train_df['y'].max())
        if max_val == 0:
            # temporary workaround for https://github.com/facebook/prophet/issues/1032
            p_growth = 'linear'
        elif max_val > 0 and max_val <= 1:
            cap = max(max_val * 1.1, 1)
            floor = float(self.train_df['y'].min()) * 0.9
            p_growth = 'logistic'
            self.train_df['cap'] = cap
            self.train_df['floor'] = floor        
        else:
            p_growth = 'linear'
        logger.debug(f'growth function: {p_growth}')
        logger.debug(self.train_df.head(30))         

        try:
            self.model = fbprophet.Prophet(growth=p_growth)
            self.model.fit(self.train_df)
            self.future = self.model.make_future_dataframe(
                periods=self.periods,
                freq=self.freq_value+self.freq_unit
            )
            self.future['cap'] = cap
            self.future['floor'] = floor
                
        except Exception as e:
            logger.error(f'Failed to create/fit model: {e}')           
            self._failed = True
       

    def predict(self):
        if self._failed:
            return -1, None
        try:
            data = self.model.predict(self.future)

            #remove old values
            data = data.loc[data['ds'] >= \
                datetime.utcnow() - timedelta(minutes=10)]

            #replace negative values with zeros
            data[['yhat','yhat_lower','yhat_upper']] = \
            data[['yhat','yhat_lower','yhat_upper']].clip(lower=0).round(4)

            #rename column
            data = data.rename(columns={'ds': 'ds_from'})
            
            #calculate end of period (ds_to)
            data[['ds_to']] = data[['ds_from']] + pd.Timedelta(
                    value=int(self.freq_value), 
                    unit=self.freq_unit
                )

            #convert dataframe to dict of records            
            forecast = data[['ds_from',
                'ds_to',
                'yhat',
                'yhat_lower',
                'yhat_upper']].to_dict(orient='records')  

            return 0, forecast
        except Exception as e:
            logger.error(f'Forecast failed with: {e}')
            return -2, None


    @staticmethod
    def calcUnit(frequency):
        freq_val = int(frequency[0:-1])
        freq_unit = frequency[-1]

        freq_unit = freq_unit.replace('m','T')
        freq_unit = freq_unit.replace('h','H')
        freq_unit = freq_unit.replace('d','D')
        
        return str(freq_val), freq_unit


    @staticmethod
    def calcPeriods(frequency, horizon):
        freq_val = int(frequency[0:-1])
        freq_unit = frequency[-1]
        
        hor_val = int(horizon[0:-1])
        hor_unit = horizon[-1]

        if freq_unit == 'm' and hor_unit == 'm':
            periods = math.ceil(hor_val / freq_val)
        elif freq_unit == 'm' and hor_unit == 'h':
            periods = math.ceil(hor_val * 60 / freq_val)
        elif freq_unit == 'm' and hor_unit == 'd':
            periods = math.ceil(hor_val * 60 * 24 / freq_val)
       
        elif freq_unit == 'h' and hor_unit == 'h':
            periods = math.ceil(hor_val / freq_val)
        elif freq_unit == 'h' and hor_unit == 'd':
            periods = math.ceil(hor_val * 24 / freq_val)

        elif freq_unit == 'd' and hor_unit == 'd':
            periods = math.ceil(hor_val / freq_val)

        else:
            logger.error(
                'Invalid input horizon and frequency parameters specified'
            )
            periods = -1

        return periods
