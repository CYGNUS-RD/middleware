#!/usr/bin/env python3
#
# G. Mazzitelli 2022
#


def boke_history(time, yval, xlabe='tempo', ylabel='', title='', legend='', notebook=False):
    from bokeh.plotting import figure, output_notebook
    from bokeh.models import DatetimeTickFormatter
    if notebook: output_notebook()

    p = figure(title=title, x_axis_type='datetime', 
               y_axis_label=ylabel, 
               x_axis_label=xlabe,
               width=750, height=350)
    p.xaxis.major_label_orientation = 3.14/4
    # add a line renderer with legend and line thickness
    for i, y in enumerate(yval):
        p.line(time, y, line_width=2)
    p.xgrid.band_hatch_pattern = "/"
    p.xgrid.band_hatch_alpha = 0.6
    p.xgrid.band_hatch_color = "lightgrey"
    p.xgrid.band_hatch_weight = 0.5
    p.xgrid.band_hatch_scale = 10
    p.xaxis.formatter=DatetimeTickFormatter(
            hours=["%d %B %Y"],
            days=["%d %B %Y"],
            months=["%d %B %Y"],
            years=["%d %B %Y"],
        )
    return p
    
def main():
    import pandas as pd
    from bokeh.plotting import output_file, save
    from bokeh.layouts import row, column, gridplot
    from bokeh.plotting import figure, output_notebook
    from bokeh.models import DatetimeTickFormatter

    import numpy as np
    import datetime
    filein = "./gas.txt"
    df = pd.read_csv(filein, delimiter=' ')

    date = [datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S') for x in df.date]
    output_notebook()
    p = figure(title='ttt', x_axis_type='datetime', 
               y_axis_label='yyy', 
               x_axis_label='date',
               width=750, height=350)
    p.xaxis.major_label_orientation = 3.14/4
    for i in range(2, len(df.columns)):
        p = boke_history(time=date, yval=df.iloc[:,i], notebook=True)
    p.xgrid.band_hatch_pattern = "/"
    p.xgrid.band_hatch_alpha = 0.6
    p.xgrid.band_hatch_color = "lightgrey"
    p.xgrid.band_hatch_weight = 0.5
    p.xgrid.band_hatch_scale = 10
    p.xaxis.formatter=DatetimeTickFormatter(
            hours=["%d %B %Y"],
            days=["%d %B %Y"],
            months=["%d %B %Y"],
            years=["%d %B %Y"],
        )
    grid_layout = column([p])
    output_file("./plots.html")
    save(grid_layout)
    
if __name__ == "__main__":
    main()
