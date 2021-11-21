from flask import render_template, flash, redirect, url_for
from app import app
from app.grid import PythonGrid
from app.data import PythonGridDbData
from app.export import PythonGridDbExport

@app.route('/')
def index():
    grid = PythonGrid('SELECT * FROM items;', 'guid', 'items')

    grid.set_caption('Checklist')
    grid.set_col_title('category', 'Category')
    grid.set_col_title('subcategory', 'Subcategory')
    grid.set_col_hidden(['guid, graph_query_success, graph_query_failure'])
    grid.set_pagesize(20)
    grid.set_dimension(800, 400)
    grid.enable_search(True)
    grid.enable_rownumbers(True)
    grid.enable_pagecount(True)
    grid.set_col_align('status', 'center')
    grid.set_col_width('comments', 600)
    grid.enable_export()

    return render_template('grid.html', title='demo', grid=grid)

@app.route('/data', methods=['GET', 'POST'])
def data():
    data = PythonGridDbData('SELECT * FROM items;')
    return data.getData()

@app.route('/export', methods=['GET', 'POST'])
def export():
    exp = PythonGridDbExport('SELECT * FROM items;')
    return exp.export()