from dash import Dash, dash_table, dcc, html, Input, Output, callback, ctx
from dash.exceptions import PreventUpdate
import pandas as pd
from loader import load
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from html_parser import parse_html_prefs, parse_primary_segments
from forechester import score
from functions import get_accessibility_increase

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

params2 = ['product_name', 'market share', 'units sold to segment', 'revision date', 'stock out', 'performance', 'size',
           'list price', 'mtbf', 'age dec 31', 'promo budget', 'awareness', 'sales budget', 'accessibility', 'dec cust survey']
params_editable = ['product_name', 'revision date', 'performance', 'size',
                   'list price', 'mtbf', 'promo budget', 'sales budget']


def generate_style_conditions(df):
    conditions = []
    for i in range(len(df)):
        if df.iloc[i]['product'].startswith('c'):
            conditions.append({
                'if': {'row_index': i},
                'backgroundColor': 'blue',
                'color': 'white',
            })
    return conditions

app.layout = html.Div([
    html.H1("Segment Forecasting"),
    html.Div([
        dcc.Dropdown(
            ['high-end', 'low-end', 'performance', 'size', 'traditional'], id='segment-dropdown', value='high-end', style={'width': '200px', 'display': 'inline-block', 'text-align': 'center'}
        ),
        dcc.Dropdown(
            {i: "Forecasting from round " + str(i) for i in range(9)}, id='round-dropdown', value=1, style={'width': '400px', 'display': 'inline-block', 'text-align': 'center'}
        ),
    ], style={'width': '80%', 'display': 'flex'}),
    html.H3("December 31 Data"),
    dash_table.DataTable(
        id='table-display-simple',
        columns=(
            [{'id': p, 'name': p} for p in params2]
        ),
        editable=False,
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_data_conditional=[{
            'if': {'column_editable': False},
            'backgroundColor': 'rgb(90,90,90)',
            'color': 'white'
        }],
        style_header_conditional=[{
            'if': {'column_editable': False},
            'backgroundColor': 'rgb(90,90,90)',
            'color': 'white'
        }],
    ),
    html.H3("Projected Segment Data for Next Round"),
    dash_table.DataTable(id='table-editing-simple',
                         columns=(
                             [{'id': p, 'name': p, 'editable': True, "type": 'numeric' if p !=
                                 'product_name' else 'text'} for p in params_editable]
                         ),
                         editable=True,
                         style_table={'height': '700px',
                                      'overflowY': 'auto', 'width': '100%'},
                         ),
    html.Div([
        html.Button('Calculate Scores', id='btn-calc',
                    n_clicks=0, formAction='calculate()'),
        html.Button('Use Actual Data from Next Round',
                    id='btn-debug', n_clicks=0, formAction='debug()'),
    ], style={"width": "100%", "display": "flex", "justify-content": "center", "align-items": "center"}),

    dcc.Graph(id='animated-graph', style={'height': '1000px',
                                          'width': '100%'}),
    html.Div([
        dash_table.DataTable(
            id='table-display-results',
            columns=(
                [{'id': p, 'name': p} for p in ['month', 'product_name',
                                                'score', 'market share', 'sales', 'cumulative sales']]
            ),
            editable=False,
            style_table={'height': '300px', 'overflowY': 'auto'}
        ),

        dash_table.DataTable(
            id='table-display-eoy',
            columns=(
                [{'id': p, 'name': p} for p in ['product', 'sales', 'share']]
            ),
            editable=False,
            style_table={'height': '300px', 'overflowY': 'auto'},
            # style_data_conditional=[
            #     {
            #         # Condition: If 'Score' column value is greater than 90
            #         'if': {
            #             'filter_query': '{product} ilike "%c" ',
            #             'column_id': 'product'
            #         },
            #         # Formatting: Change the background color of the row
            #         'backgroundColor': 'blue',
            #         # Optional: Change text color to improve contrast
            #         'color': 'white'
            #     }
            # ]
        )
    ], style={"width": "100%", "display": "flex", "justify-content": "center", "align-items": "center"})
])


def get_month_data(df_new, df_old, sales_budgets, segment, round_no):
    TEST_PROD = ''
    month_data = []
    for p, row in df_new.iterrows():
        r, prc, mtn, pfn, szn = map(float, map(row.get, [
            'revision date', 'list price', 'mtbf', 'performance', 'size']))

        new_product = p not in df_old.index

        if new_product:
            old_size, old_perf, mto, ago, awa = 0, 0, 0, 0, 0
            acc = df_old[df_old.index.astype(
                str).str[0] == p[0]]['accessibility'].mean()
        else:
            old_size, old_perf, mto, ago, awa, acc = map(float, df_old.loc[p, [
                'size', 'performance', 'mtbf', 'age dec 31', 'awareness', 'accessibility']])

        update = old_size != szn or old_perf != pfn

        # print(mtn, mto, old_size, ago, szn, old_perf, pfn, row['promo budget'], df_old.loc[p, 'awareness'], row['sales budget'], df_old.loc[p, 'accessibility'])
        css = score(prc=prc, seg=segment, rvm=r, mto=mto, mtn=mtn,  ago=ago, szo=old_size, szn=szn,
                    pfo=old_perf, pfn=pfn, prm=float(row['promo budget']), awa=awa, arp=45,
                    sal=sales_budgets[p[0]], acc=acc, test=p==TEST_PROD, rd=round_no, up=update, new=new_product, debug=p==TEST_PROD)
        
        if p == TEST_PROD:
            print(css[0], prc, segment, r, mto, mtn, old_size, ago, szn, old_perf, pfn,
                  row['promo budget'], awa, sales_budgets[p[0]], acc, 0, round_no, update, new_product, 1)

            with pd.option_context('display.max_rows', None,
                                    'display.max_columns', None,
                                    'display.precision', 3,
                                    ):
                spdf = pd.DataFrame([css[0][i:i + 12]
                                        for i in range(0, 48, 12)], index=['price', 'mtbf', 'age', 'position'])
                print(spdf.to_string())
                exit()

        for m in range(1, 13):
            vals = [m, old_size if m < r else szn,
                    old_perf if m < r else pfn, p[0], p, css[m-1], 5]
            month_data.append(pd.DataFrame(
                [vals], columns=['month', 'size', 'performance', 'team', 'product', 'score', 'dot_size']))
    return pd.concat(month_data, ignore_index=True)

def get_results_df(df, segment, round_no):
    dfmod = df.copy()
    dfmod = dfmod.groupby('month')
    # loop through months
    demand, growth_rate = load(segment=segment, round_no=round_no)[2:]
    monthly_demand = (demand * (1 + growth_rate)) / 12
    res_data = []
    for month, data in dfmod:
        # get sum of score column
        score_sum = data['score'].sum()
        # iterate through products in data
        for index, row in data.iterrows():
            # calculate market share
            market_share = row['score'] / score_sum
            # calculate sales
            sales = market_share * monthly_demand
            vals_to_add = [month, row['product'],
                           round(row['score'], 0), round(market_share, 2), round(sales, 0), 0]
            res_data.append(pd.DataFrame([vals_to_add], columns=[
                            'month', 'product_name', 'score', 'market share', 'sales', 'cumulative sales']))
    return pd.concat(res_data)

def get_eoy_dict(dfres):
    dfbyproduct = dfres.groupby('product_name')
    eoy_prod_data = {
        product: {
            'sales': 0,
            'share': 0
        } for product in dfres['product_name'].unique()
    }
    industry_sales = 0
    for product, data in dfbyproduct:
        total_sales = data['sales'].sum()
        eoy_prod_data[product]['sales'] = total_sales
        industry_sales += total_sales

    for product in eoy_prod_data:
        eoy_prod_data[product]['share'] = eoy_prod_data[product]['sales'] / industry_sales

    res_dict = [
        {'product': product, 'sales': round(eoy_prod_data[product]['sales'], 0), 'share': str(round(eoy_prod_data[product]['share'], 2) * 100) + '%'} for product in eoy_prod_data
    ]

    return res_dict

def add_segment_prefs(fig, seg_prefs, ideal, center):
    fig.add_trace(go.Scatter(
        x=[seg_prefs['pfmn']['value'] + center['pfmn']/12*i for i in [1, 12]], y=[seg_prefs['size']['value'] + center['size']/12*i for i in [1, 12]],
        mode="markers", marker=dict(color="green", size=10), name="ideal", fill='none'
    ))

    fig.update_traces(textposition='top center')

    r = 2.5
    cx = seg_prefs['pfmn']['value'] - ideal['pfmn']
    cy = seg_prefs['size']['value'] - ideal['size']
    fig.add_shape(type="circle",
                  xref="x", yref="y",
                  x0=cx - r, y0=cy - r, x1=cx + r, y1=cy + r,
                  line_color="Red",
                  fillcolor="rgba(0,0,0,0)")
    r = 4
    fig.add_shape(type="circle",
                  xref="x", yref="y",
                  x0=cx - r, y0=cy - r, x1=cx + r, y1=cy + r,
                  line_color="Red", line=dict(dash="dot"),
                  fillcolor="rgba(0,0,0,0)")
    cx = seg_prefs['pfmn']['value'] - ideal['pfmn'] + center['pfmn']
    cy = seg_prefs['size']['value'] - ideal['size'] + center['size']
    fig.add_shape(type="circle",
                  xref="x", yref="y",
                  x0=cx - r, y0=cy - r, x1=cx + r, y1=cy + r,
                  line_color="Blue", line=dict(dash="dot"),
                  fillcolor="rgba(0,0,0,0)")
    r = 2.5
    fig.add_shape(type="circle",
                  xref="x", yref="y",
                  x0=cx - r, y0=cy - r, x1=cx + r, y1=cy + r,
                  line_color="Blue",
                  fillcolor="rgba(0,0,0,0)")
    return fig

@callback(
    Output('animated-graph', 'figure'),
    Output('table-display-results', 'data'),
    Output('table-display-eoy', 'data'),
    Input('table-editing-simple', 'data'),
    Input('table-display-simple', 'data'),
    Input('btn-calc', 'n_clicks'),
    Input('segment-dropdown', 'value'),
    Input('round-dropdown', 'value')

)
def display_animated_graph(new_data, old_data, nclicks, segment, round_no):
    if ctx.triggered_id != 'btn-calc':
        raise PreventUpdate

    # Convert data to DataFrames and set index
    df_new = pd.DataFrame(new_data).query("product_name != ''").set_index('product_name')
    df_old = pd.DataFrame(old_data).set_index('product_name')

    sales_budgets = {
        let: df_new[df_new.index.astype(str).str[0] == let]['sales budget'].sum() for let in ['A', 'B', 'C', 'D', 'E', 'F']
    }


    print(sales_budgets)
    for k, v in sales_budgets.items():
        print(k, get_accessibility_increase(v, 2),
              get_accessibility_increase(v, 1))

    df = get_month_data(df_new, df_old, sales_budgets, segment, round_no)

    dfres = get_results_df(df, segment, round_no)

    eoy_dict = get_eoy_dict(dfres)

    fig = px.scatter(
        df, y="size", x="performance", animation_frame="month",
        animation_group="team", size='dot_size', color="score",
        hover_name="product", size_max=10,
        color_continuous_scale=px.colors.sequential.Viridis,
        range_color=[0, 75],
        text='product',
        range_x=[df['performance'].min() - 2, df['performance'].max() + 2], range_y=[df['size'].min() - 2, df['size'].max() + 2])
    
    # Process segment preferences and ideal spots
    seg_prefs, ideal, center = parse_html_prefs(round_no, segment)
    fig = add_segment_prefs(fig, seg_prefs, ideal, center)

    return fig, dfres.to_dict('records'), eoy_dict

@callback(
    Output('table-display-simple', 'data'),
    Input('segment-dropdown', 'value'),
    Input('round-dropdown', 'value')
)
def show_december_data(segment, rd):
    seg_data, seg_prefs, market_size, growth_rate = load(rd, segment, 'C')

    dec_data_dict = [{**{param: product[i]
                         for i, param in enumerate(params2)}} for product in seg_data]
    return dec_data_dict


@callback(
    Output('table-editing-simple', 'data'),
    Input('segment-dropdown', 'value'),
    Input('round-dropdown', 'value'),
    Input('btn-debug', 'n_clicks')
)
def show_december_data2(segment, rd, nclicks):
    if ctx.triggered_id == 'btn-debug':
        seg_data, seg_prefs, market_size, growth_rate = load(
            int(rd)+1, segment, 'C')
    else:
        seg_data, seg_prefs, market_size, growth_rate = load(rd, segment, 'C')

    dec_data_dict = [{**{param: product[i]
        for i, param in enumerate(params2) if param in params_editable}} for product in seg_data]
    
    if ctx.triggered_id != 'btn-debug':
        for d in dec_data_dict:
            d['list price'] -= .5
    # add 3 blank rows to dec_data_dict
    for i in range(5):
        dec_data_dict.append({param: '' for param in params_editable})
    return dec_data_dict


if __name__ == '__main__':
    app.run(debug=True)
