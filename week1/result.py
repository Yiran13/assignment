import pandas as pd
import numpy as np
import plotly as py
import plotly.graph_objs as go
import plotly.express as px


def get_individual_returns(data: pd.DataFrame, n: int) -> pd.DataFrame:
    return pd.DataFrame(data.iloc[:, 1:n + 1].values,
                        index=data.iloc[:, 0],
                        columns=data.columns[1:n + 1])


def get_portfolio_return(data: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    calculate equal-weight portfolio return
    with the assumption:balancing portfolio periodically
    """
    return pd.DataFrame((data * 1 / n).sum(axis=1), columns=[f'return_with_{n}_stock'])


def portfolio_pipeline(data_path: str, portfolio_num: int) -> pd.DataFrame:
    return (pd
            .read_excel(data_path, header=5)
            .pipe(lambda x: get_individual_returns(x, portfolio_num))
            .pipe(lambda x: get_portfolio_return(x, portfolio_num))
            )


def portfolio_variance_contribution(data_path: str, portfolio_num: int) -> pd.DataFrame:
    pass


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
