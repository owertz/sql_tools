import sys
sys.path.insert(0, 'C:\\Users\\owertz\\OneDrive - Sopra Steria\\Documents\\TICKETING\\PYTHON\Scripts\\sql_tools\\sql_tools')
#sys.path.insert(0, '/home/python-code/sql_tools/sql_tools')

from flask import Flask, render_template, request

from sql_query_formatter import main_formatter
from sqlplus_output_formatter import mainFromServer

app = Flask(__name__)
app.config['SECRET_KEY'] = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/sqlplusformatter', methods=('GET', 'POST'))
def sqlplusformatter(sqlplus_input=None):
    if sqlplus_input is None:
        sqlplus_input = ''

    if request.method == 'POST':
        sqlplus_input_formatted = mainFromServer(request.form['content'].replace('\r', ''))
        return render_template('sqlplusformatter.html', myquerymysqlplusoutput=sqlplus_input_formatted)

    return render_template('sqlplusformatter.html', myquerymysqlplusoutput=sqlplus_input)

@app.route('/queryformatter', methods=('GET', 'POST'))
def sqlqueryformatter(myquery=None):
    if myquery is None:
        myquery = ''

    if request.method == 'POST':
        print("OWEOWE: |", request.form['content'],"|")
        query_formatted = main_formatter(request.form['content'])
        print(query_formatted)
        return render_template('sqlqueryformatter.html', myquery=query_formatted)
    return render_template('sqlqueryformatter.html', myquery=myquery)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)    #--> local
    #app.run(debug=True, host='10.7.169.98', port=5000) #--> environment LUX