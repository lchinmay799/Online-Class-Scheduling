import mysql.connector
from flask import Flask,request,render_template,redirect,url_for
from datetime import datetime
import smtplib

connection=mysql.connector.connect(host="localhost",user="root",database="scheduling",password="p@55w06d")
cursor = connection.cursor(buffered=True)
app=Flask(__name__)

@app.route('/')
def index():
	return render_template("page1.html")

@app.route('/page1')
def page1():
	return render_template("page1.html")

@app.route('/studentlogin')
def index1():
	return render_template("studentlogin.html")

@app.route('/teacherlogin')
def index2():
	return render_template("teacherlogin.html")

@app.route('/tforgot')
def tforgot():
	return render_template("tforgot.html")

@app.route('/sforgot')
def sforgot():
	return render_template("sforgot.html")

@app.route('/ssuccess',methods=["POST"])
def ssuccess():
	u=request.form.get("usn")
	email=request.form.get("email")
	p=request.form.get("password")
	cp=request.form.get("cpassword")
	if p==cp:
		sql="update student set password='"+str(p)+"' where sid="+u+";"
		cursor.execute(sql)
		connection.commit()
		return render_template("ssuccess.html",message="Password Updated Successfully...")
	else:
		return render_template("ssuccess.html",message="Passwords Don't Match...")

@app.route('/tsuccess',methods=["POST"])
def tsuccess():
	email=request.form.get("email")
	p=request.form.get("password")
	cp=request.form.get("cpassword")
	if p==cp:
		sql="update teacher set password='"+str(p)+"' where email='"+email+"';"
		cursor.execute(sql)
		connection.commit()
		return render_template("tsuccess.html",message="Password Updated Successfully...")
	else:
		return render_template("tsuccess.html",message="Passwords Don't Match...")

@app.route('/spage2',methods=["POST"])
def studentlogin():
	u=request.form.get("usn")
	e=request.form.get("email")
	p=request.form.get("password")
	sql="select password,email,sname,cid from student where sid="+str(u)+";"
	cursor.execute(sql)
	record=cursor.fetchone()
	if record[0]==p and record[1]==e:
		name,cid=record[2],record[3]
		current=datetime.now()
		sql1="select start,finish,tid,subid from schedules where cid="+str(cid)+" and start >'"+str(current)+"' order by start;"
		cursor.execute(sql1)
		record=cursor.fetchall()
		if record==None or len(record)==0:
			return render_template("spage2.html",m="You Don't have any Classes Scheduled...")
		else:
			l=[]
			for i in record:
				sql2="select subname from subject where subid="+str(i[3])+";"
				cursor.execute(sql2)
				sname=cursor.fetchone()
				sql3="select tname from teacher where tid="+str(i[2])+";"
				cursor.execute(sql3)
				tname=cursor.fetchone()
				l.append([sname[0],i[0].strftime("%d/%m/%Y, %H:%M:%S"),i[1].strftime("%d/%m/%Y, %H:%M:%S"),tname[0]])
			return render_template("spage2.html",l=l,n="You Have The Following Classes : ")
	else:
		m="Sorry...!\n Wrong USN or Email or Password..."
		n="Enter the Correct USN, Email and Password..."
		return render_template("supdate.html",m=m,n=n)

@app.route('/tpage2',methods=["POST"])
def teacherlogin():
	u=request.form.get("temail")
	p=request.form.get("tpassword")
	sql="select password from teacher where email='"+str(u)+"';"
	cursor.execute(sql)
	record=cursor.fetchone()
	if record[0]==p:
		return render_template("tpage2.html",m=u)
	else:
		m="Sorry...!\n Wrong Email or Password..."
		n="Enter the Correct Email and Password..."
		return render_template("tupdate.html",m=m,n=n)

@app.route('/tpage3ii/<email>')
def tpage3ii(email):
	current=datetime.now()
	sql="select tid from teacher where email='"+email+"';"
	cursor.execute(sql)
	e=request.form.get("email")
	record=cursor.fetchone()
	tid=record[0]
	sql2="select start,finish,cid,subid from schedules where tid="+str(tid)+" order by start;"
	cursor.execute(sql2)
	record=cursor.fetchall()
	if record==None or len(record)==0:
		return render_template("tpage3ii.html",m="You Don't have any Classes Scheduled...")
	else:
		l=[]
		for i in record:
			sql3="select subname from subject where subid="+str(i[3])+";"
			cursor.execute(sql3)
			sname=cursor.fetchone()
			sql4="select bname from branches where bid=(select bid from class where cid="+str(i[2])+");"
			cursor.execute(sql4)
			bname=cursor.fetchone()
			sql5="select cname from class where cid="+str(i[2])+";"
			cursor.execute(sql5)
			cname=cursor.fetchone()
			l.append([sname[0],i[0].strftime("%d/%m/%Y, %H:%M:%S"),i[1].strftime("%d/%m/%Y, %H:%M:%S"),bname[0],cname[0]])
		return render_template("tpage3ii.html",l=l,n="You Have The Following Classes : ")

@app.route('/tpage3i/<email>')
def tpage3i(email):
	sql="select tid from teacher where email='"+email+"';"
	cursor.execute(sql)
	tid=cursor.fetchone()
	sql="select subname,subid from subject where subid in (select subid from taught_by where tid="+str(tid[0])+");"
	cursor.execute(sql)
	s=cursor.fetchall()
	sql="select cname from class where cid in (select cid from taught_by where tid="+str(tid[0])+");"
	cursor.execute(sql)
	c=cursor.fetchall()
	c.sort()
	return render_template("tpage3i.html",m=email,subject=s,cls=c)

@app.route('/tpage3i/<email>',methods=["POST"])
def tpage3i1(email):
	sql="select tid from teacher where email='"+email+"';"
	cursor.execute(sql)
	tid=cursor.fetchone()
	sql="select subname,subid from subject where subid in (select subid from taught_by where tid="+str(tid[0])+");"
	cursor.execute(sql)
	s=cursor.fetchall()
	sql="select cname from class where cid in (select cid from taught_by where tid="+str(tid[0])+");"
	cursor.execute(sql)
	c=cursor.fetchall()
	c.sort()
	return render_template("tpage3i.html",m=email,subject=s,cls=c)

@app.route('/tpage4/<email>',methods=["POST"])
def tpage4(email):
	sql="select tid,tname from teacher where email='"+email+"';"
	cursor.execute(sql)
	t=cursor.fetchone()
	sql="select subname,subid from subject where subid in (select subid from taught_by where tid="+str(t[0])+");"
	cursor.execute(sql)
	sub=cursor.fetchall()
	sql="select cname from class where cid in (select cid from taught_by where tid="+str(t[0])+");"
	cursor.execute(sql)
	c=cursor.fetchall()
	c.sort()
	sid=request.form.get("subject")
	sql="select subname from subject where subid="+str(sid)+";"
	cursor.execute(sql)
	subject=cursor.fetchone()
	subject=subject[0]
	cname=request.form.get("class")
	stime=request.form.get("starttime")
	ftime=request.form.get("finishtime")
	sdate=request.form.get("startdate")
	fdate=request.form.get("finishdate")
	link=request.form.get("link")
	start=datetime.strptime(sdate+" "+stime,"%Y-%m-%d %H:%M:%S")
	finish=datetime.strptime(fdate+" "+ftime,"%Y-%m-%d %H:%M:%S")
	if start>datetime.now() and finish>datetime.now() and finish>start:
		sql="select bid from teacher where email='"+email+"';"
		cursor.execute(sql)
		bid=cursor.fetchone()
		sql="select bname from branches where bid="+str(bid[0])+";"
		cursor.execute(sql)
		bname=cursor.fetchone()
		sql="select cid from class where cname='"+cname+"' and bid="+str(bid[0])+";"
		cursor.execute(sql)
		cid=cursor.fetchone()
		cid,bid,tname,tid,bname=cid[0],bid[0],t[1],t[0],bname[0]
		sql="select subid,start,finish from schedules where cid="+str(cid)+" and ('"+str(start)+"'>=start and '"+str(start)+"'<=finish) or ('"+str(finish)+"'>=start and '"+str(finish)+"'<=finish);"
		cursor.execute(sql)
		record=cursor.fetchone()
		if record==None or len(record)==0:
			sql2="select email from student where cid="+str(cid)+";"
			cursor.execute(sql2)
			record=cursor.fetchall()
			li=[]
			for i in record:
				li.append(i[0])
			sql="insert into schedules (cid,tid,subid,start,finish) values(%s,%s,%s,%s,%s)"
			val=(cid,tid,sid,start,finish)
			cursor.execute(sql,val)
			connection.commit()
			password="jai bhajarangabali"
			message="""Hello,

			You have a {} class scheduled between {} and {} by {}

				Link for the Meet is :
					{}
			""".format(subject,start,finish,tname,link)
			m="You have Successfully Scheduled a class for {} {} Section between {} and {}".format(bname,cname,start,finish)
			server=smtplib.SMTP_SSL("smtp.gmail.com",465)
			server.login("lchinmay777@gmail.com",password)
			server.sendmail("lchinmay777@gmail.com",li,message)
			server.quit()
			return render_template("tpage4.html",bname=bname,cname=cname,start=start,finish=finish,subject=subject)
		else:
			m=""" Sorry,

					Students of {} {} Section already have a class between {} and {}""".format(bname,cname,start,finish) 
			return render_template("tpage3i.html",message=m,subject=sub,cls=c,m=email)
	else:	
		m="""Invalid Date and Time...

				Try Again..."""
		return render_template("tpage3i.html",o=m,subject=sub,cls=c,m=email)

if __name__=='__main__':
	app.run(debug=True)