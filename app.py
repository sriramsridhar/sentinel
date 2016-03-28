from flask import Flask, render_template, request, url_for, Response
import dbcon
import itertools
import datetime
import unicodedata
from senti_classifier import senti_classifier
app = Flask(__name__)

@app.route('/admin/')
def admin():
    check=dbcon.Product.select().count()
    
    return render_template('admin.html')

@app.route('/create_product/',methods=['POST'])
def create_product():
    check = dbcon.Product.select().count()
    title=request.form['prodname']
    ftitle=str(unicodedata.normalize('NFKD', title).encode('ascii','ignore'))
    desc=request.form['proddesc']
    fdesc=str(unicodedata.normalize('NFKD', desc).encode('ascii','ignore'))
    print dbcon.Product.create(time = datetime.datetime.now(), prod_id = check+1, Prod_title = ftitle, Prod_desc = fdesc,prod_p_value=0,prod_n_value=0)
    content="Product"
    return render_template('success.html',content=content)


@app.route('/prod/<int:variable>')
def prod(variable):
    presult=dbcon.Product.select().where(dbcon.Product.prod_id == variable)
    ccount=dbcon.Comments.select().count()
    if ccount != None:
        check='Y'
    else:
        check='N'
    cresult=dbcon.Comments.select().where(dbcon.Comments.article_id == variable)
    return render_template('form_action.html',product=presult[0],comment=cresult,check=check)

@app.route('/addcomment/<int:variable>',methods=['POST'])
def addcomment(variable):
    cmmnt1=[]
    cmmnt=request.form['comment']
    cmmnt1.append(str(cmmnt))
    p,n = senti_classifier.polarity_scores(cmmnt1)
    if p>n:
        t="positive"
    else:
        t="negative"
    dbcon.Comments.create(time = datetime.datetime.now(),article_id=variable,cmmnt_type = t,cmmnt_content = cmmnt,p_value = p,n_value=n)
    count=dbcon.Comments.select().where(dbcon.Comments.article_id == variable).count()
    result = dbcon.Comments.select().where(dbcon.Comments.article_id == variable)
    totp=0.0
    totn=0.0
    for n in result:
        totp+=n.p_value
        totn+=n.n_value
    prod_p_value=totp/count
    prod_n_value=totn/count
    query = dbcon.Product.update(prod_p_value=prod_p_value,prod_n_value=prod_n_value).where(dbcon.Product.prod_id == variable)
    query.execute() 
    content="Comment"
    return render_template('success.html',content=content)

@app.route('/')
def form():
    count=dbcon.Product.select().count()
    result = dbcon.Product.select().order_by(dbcon.Product.prod_p_value.desc())
    return render_template('form_submit.html',count=count,result=result)

@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Not found</h3>'), 404
if __name__ == '__main__':
	app.jinja_env.cache = {}
	app.run(debug=True,host="0.0.0.0")


