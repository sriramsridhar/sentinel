from flask import Flask, render_template, request, url_for, Response
import dbcon
import itertools
import datetime
import unicodedata
from senti_classifier import senti_classifier
app = Flask(__name__)

def give_stats():
    check=dbcon.Product.select().count()
    result = dbcon.Product.select().order_by(dbcon.Product.prod_id)
    j=[]
    for i in result:
        ccount=dbcon.Comments.select().where(dbcon.Comments.article_id == i.prod_id).count()
        comment_parse=dbcon.Comments.select().where(dbcon.Comments.article_id == i.prod_id)
        pcount=ncount=0
        for t in comment_parse:
            if t.p_value>t.n_value:
                pcount=pcount+1
            else:
                ncount=ncount+1
        k={'id':i.prod_id,'prod':i.Prod_title,'time':i.time,'desc':i.Prod_desc,'p_value':i.prod_p_value,'n_value':i.prod_n_value,'comment_count':ccount,'pcount':pcount,'ncount':ncount}
        j.append(k)
    return j,check


# def graph():
#     result=dbcon.Product.select().order_by(dbcon.Product.prod_id)
#     pos_data=neg_data=""
#     column_name=[]
#     for i in result:
#         column_name.append('"'+i.Prod_title+'"')
#         pos_data+=str(i.prod_p_value)+","
#         neg_data+=str(i.prod_n_value)+","
#     return column_name,pos_data[:-1],neg_data[:-1]

@app.route('/admin/')
def admin():
    data,check=give_stats()
    # column_name,p_data,n_data=graph()
    return render_template('admin.html', data=data, check=check)

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

@app.route('/delproduct/<int:variable>')
def delproduct(variable):
    query=dbcon.Product.delete().where(dbcon.Product.prod_id == variable)
    query.execute()
    cmtdeletequery=dbcon.Comments.delete().where(dbcon.Comments.article_id == variable)
    cmtdeletequery.execute
    return render_template('delete_success.html')
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
@app.route('/index/')
def index():
    count=dbcon.Product.select().count()
    result = dbcon.Product.select().order_by(dbcon.Product.prod_p_value.desc())
    return render_template('form_submit.html',count=count,result=result)

@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Not found</h3>'), 404
if __name__ == '__main__':
	app.jinja_env.cache = {}
	app.run(debug=True,host="0.0.0.0")


