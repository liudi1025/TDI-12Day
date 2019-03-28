from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
   return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        sticker = request.form['ticker']
        check_box = request.form.getlist('features')
        return redirect(url_for('graph', stock=sticker, price=check_box))
    return render_template('login.html')

@app.route('/graph/<stock>/<price>')
def graph(stock,price):
    import pandas as pd
    from bokeh.models import HoverTool, ColumnDataSource
    from bokeh.plotting import figure, show, output_file
    from bokeh.embed import components
    from bokeh.resources import CDN

    url_adj = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=' + stock + '&apikey=6J2GKBOI6CJIJHXB&datatype=csv'
    df_adj = pd.read_csv(url_adj)

    df_adj['timestamp'] = pd.to_datetime(df_adj['timestamp'], format="%Y-%m-%d")
    df_adj['date'] = df_adj['timestamp'].astype(str)
    df_adj['left'] = pd.DatetimeIndex(df_adj.timestamp) - pd.DateOffset(days=0.5)
    df_adj['right'] = pd.DatetimeIndex(df_adj.timestamp) + pd.DateOffset(days=0.5)

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", tools=TOOLS, title= stock + ' Stock Price')
    p.title.text_font_size = '20pt'
    p.title.align = 'center'

    p.background_fill_color = "#efefef"
    p.xgrid.grid_line_color = "#efefef"
    p.xaxis.axis_label = 'Time'
    p.xaxis.axis_label_text_font_size = '18pt'
    p.yaxis.axis_label = 'Price USD'
    p.yaxis.axis_label_text_font_size = '18pt'

    source = ColumnDataSource({
        'date': df_adj['date'].tolist(),
        'Date': df_adj['timestamp'].tolist(),
        'adj_close': df_adj['adjusted_close'].tolist(),
        'opening': df_adj['open'].tolist(),
        'closing': df_adj['close'].tolist(),
        'top': df_adj['high'].tolist(),
        'bottom': df_adj['low'].tolist(),
        'left': df_adj['left'].tolist(),
        'right': df_adj['right'].tolist()
    })

    if 'open' in price:
        y1_l = p.line(x='Date', y='opening', line_color='red', line_width=3, source=source, legend='Open Price')
        y1_c = p.circle(x='Date', y='opening', color='red', size=6, source=source)
        tooltips_list1 = [('date', '@date'), ('Open Price', '$@opening')]
        p.add_tools(HoverTool(renderers=[y1_c], tooltips=tooltips_list1))

    if 'close' in price:
        y2_l = p.line(x='Date', y='closing', source=source, line_color='grey', line_width=3, legend='Close Price')
        y2_c = p.circle(x='Date', y='closing', source=source, color='grey', size=6)
        tooltips_list2 = [('date', '@date'), ('Close Price', '$@closing')]
        p.add_tools(HoverTool(renderers=[y2_c], tooltips=tooltips_list2))

    if 'adj_close' in price:
        y3_l = p.line(x='Date', y='adj_close', source=source, line_color='blue', line_width=3,
                      legend='Adjusted Close Price')
        y3_c = p.circle(x='Date', y='adj_close', source=source, color='blue', size=6)
        tooltips_list3 = [('date', '@date'), ('Adj Close Price', '$@adj_close')]
        p.add_tools(HoverTool(renderers=[y3_c], tooltips=tooltips_list3))

    if 'high_low' in price:
        y4 = p.quad(top='top', bottom='bottom', left='left', right='right', source=source, color='black',
                    fill_alpha=0.1, legend='Price Range')
        tooltips_list4 = [('date', '@date'), ('Highest Price', '$@top'), ('Lowest Price', '$@bottom')]
        p.add_tools(HoverTool(renderers=[y4], tooltips=tooltips_list4))

    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    cdn_css = CDN.css_files[0]
    return render_template('graph.html', stock=stock, price=price, script1=script1,
                           div1=div1, cdn_js=cdn_js, cdn_css=cdn_css)

if __name__ == '__main__':
    app.run(debug=True)
