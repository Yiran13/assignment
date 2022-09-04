import pandas as pd
import numpy as np
import plotly as py

import plotly.express as px
import plotly.graph_objs as go


def get_individual_returns(data: pd.DataFrame, n: int) -> pd.DataFrame:
    return pd.DataFrame(data.iloc[:, 1:n + 1].values,
                        index=data.iloc[:, 0],
                        columns=data.columns[1:n + 1])


def get_portfolio_return(data: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    calculate equal-weight portfolio return
    with the assumption:balancing portfolio periodically
    """
    return pd.DataFrame((data / n).sum(axis=1), columns=[f'return_with_{n}_stock'])


def get_weighted_individual_variance(data: pd.DataFrame, n: int) -> pd.DataFrame:
    return pd.DataFrame({'': (data.var() / n ** 2).sum(), }, index=[n])


def portfolio_pipeline(data_path: str, portfolio_num: int) -> pd.DataFrame:
    return (pd
            .read_excel(data_path, header=5)
            .pipe(lambda x: get_individual_returns(x, portfolio_num))
            .pipe(lambda x: get_portfolio_return(x, portfolio_num))
            )


def portfolio_weighted_variance(data_path: str, portfolio_num: int) -> pd.DataFrame:
    return (pd
            .read_excel(data_path, header=5)
            .pipe(lambda x: get_individual_returns(x, portfolio_num))
            .pipe(lambda x: get_weighted_individual_variance(x, portfolio_num))
            )


def all_sample_vol(data: pd.DataFrame, date: str) -> pd.DataFrame:
    return pd.DataFrame({'all_sample_vol': data.loc[:date].std().values}, index=[date])


def one_year_vol(data: pd.DataFrame, date: str) -> pd.DataFrame:
    return pd.DataFrame({'past_one_year_vol': data.loc[:date].iloc[-12:].std().values}, index=[date])


def estimate_stock_vol(data: pd.DataFrame, stock_name: str) -> pd.DataFrame:
    dates = data.index.astype('str').to_list()
    stock_ret = data[[stock_name]]
    all_sample = pd.concat(list(map(lambda date: all_sample_vol(stock_ret, date), dates)))
    one_year = pd.concat(list(map(lambda date: one_year_vol(stock_ret, date), dates)))
    return pd.concat([all_sample, one_year], axis=1)


def plot_estimated_vol(vol_data: pd.DataFrame, filename: str = ''):
    fig_all_sample_var = go.Scatter(
        x=vol_data.index,
        y=vol_data.all_sample_vol,
        name='all sample')
    fig_1year_sample_var = go.Scatter(
        x=vol_data.index,
        y=vol_data.past_one_year_vol,
        name='1-year sample')
    py.offline.plot([fig_1year_sample_var, fig_all_sample_var], filename=filename, auto_open=False)


# Problem1-Q1
portfolios = pd.concat(
    list(map(lambda portfolio_num: portfolio_pipeline('Problem_Set1_2022.xlsx', portfolio_num),
             [5, 10, 25, 50]
             )
         ),
    axis=1)

portfolio_statistics = pd.DataFrame({
    'mean': portfolios.apply(np.mean).values,
    'std': portfolios.apply(np.std).values}
    , index=[5, 10, 25, 50])

portfolio_std = pd.DataFrame({
    'std': portfolios.apply(np.std).values,
    'stock_num': [5, 10, 25, 50]})

fig_std = px.line(data_frame=portfolio_std,
                  x='stock_num',
                  y='std',
                  title='stock num vs portfolio return standard deviation ')
py.offline.plot(fig_std, filename='portfolio_return_std.html', auto_open=False)

# Problem1-Q2
portfolio_5 = get_individual_returns(pd
                                     .read_excel('Problem_Set1_2022.xlsx', header=5), 5)

weighted_variances = pd.concat(
    list(map(lambda portfolio_num: portfolio_weighted_variance('Problem_Set1_2022.xlsx', portfolio_num),
             [5, 10, 25, 50]
             )
         ),
    axis=0)

portfolios_variance_contributions = pd.DataFrame(
    weighted_variances.values.reshape(-1, 1) / portfolios.var().values.reshape(-1, 1),
    columns=['variance_contribution'],
    index=[5, 10, 25, 50])
fig_var_contribution = px.line(data_frame=portfolios_variance_contributions,
                               x=portfolios_variance_contributions.index,
                               y='variance_contribution',
                               title='stock num vs variance contribution')
py.offline.plot(fig_var_contribution, filename='portfolio_variance_contributions.html', auto_open=False)

# Problem2-Q1


data = (pd
        .read_excel('Problem_Set1_2022.xlsx', header=5)
        .set_index('date')
        )

vol_txn = estimate_stock_vol(data, 'TXN')
vol_market = estimate_stock_vol(data, 'Market (Value Weighted Index)')

plot_estimated_vol(vol_market, 'market_vol.html')
plot_estimated_vol(vol_txn, 'txn_vol.html')
