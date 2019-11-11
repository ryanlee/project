#  keep jinja2 for web since flask_admin use it, no plan to migrate, mako only used for cli
#  from flask_mako import MakoTemplates, render_template
#  mako = MakoTemplates(bp)

from flask import Blueprint
bp = Blueprint('views', __name__)

from flask import render_template, url_for

@bp.route('/')
@bp.route('/index.html')
def home():
    charts = draw()
    return render_template('index.html',charts=charts)

# temp examples
@bp.route('/index1.html')
def index1():
    return render_template('index1.html')
@bp.route('/index2.html')
def index2():
    return render_template('index2.html')
@bp.route('/index3.html')
def index3():
    return render_template('index3.html')

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import CDN as BOKEH # INLINE TODO : how to specify stable version?
from bokeh.util.string import encode_utf8

import holoviews as hv
hv.extension('bokeh')
renderer = hv.renderer('bokeh')
import numpy as np

import pprint

@bp.route('/bokeh')
def draw():
    charts = {}

    # init a basic bar chart:
    # http://bokeh.pydata.org/en/latest/docs/user_guide/plotting.html#bars
    fig = figure(plot_width=800, plot_height=200)
    fig.vbar(
        x=[1, 2, 3, 4],
        width=0.5,
        bottom=0,
        top=[1.7, 2.2, 4.6, 3.9],
        color='navy'
    )
    charts['bar.script'] , charts['bar'] = components(fig)

    hmap = hv.HoloMap({i: hv.Curve(np.random.rand(10)*i) for i in range(1,5)})
    hv_comp , charts['application/vnd.holoviews_exec.v0+json'] = renderer.components(hmap)
    charts['hv.script'] = '<script type="text/javascript">\n' + hv_comp['application/javascript'] + '\n</script>'
    charts['hv'] = hv_comp['text/html']

    charts['script'] = BOKEH.render_js() + BOKEH.render_css() + charts['bar.script'] + charts['hv.script']
    return charts
    #  html = render_template( 'bokeh/index.html', charts=charts)
    #  return encode_utf8(html)

