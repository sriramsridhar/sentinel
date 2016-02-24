import peewee as pw

myDB = pw.MySQLDatabase("sentinel", host="localhost", user="root", passwd="svss1995")


class MySQLModel(pw.Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = myDB


class Product(MySQLModel):
    prod_id=pw.IntegerField()
    Prod_title=pw.CharField()
    Prod_desc=pw.TextField()
    time=pw.DateTimeField()
    prod_p_value=pw.DoubleField()
    prod_n_value=pw.DoubleField()
    # etc, etc
    class Meta:
        order_by = ('prod_id',)

class Comments(MySQLModel):
    time = pw.DateTimeField()
    article_id=pw.IntegerField()
    cmmnt_type = pw.CharField()
    cmmnt_content = pw.TextField()
    p_value = pw.DoubleField()
    n_value = pw.DoubleField()

    class Meta:
        order_by = ('article_id',)

# when you're ready to start querying, remember to connect
myDB.connect()
myDB.create_tables([Product, Comments], safe=True)
