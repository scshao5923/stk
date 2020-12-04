from bottle import route, run, static_file, request, template, response
import datetime
import json
import locale
import os
import random
import re
import stk
import sqlite3
import sys
if sys.platform != 'ios':
	from gtts import gTTS
	#設定語系
	locale.setlocale(locale.LC_ALL,locale='zh_TW.UTF-8')
#設定資料路徑
DB='dict.db'
DATA_PATH='./'

def getDat():
	tdy=datetime.date.today()
	return "{0:04}{1:02}{2:02}".format(tdy.year,tdy.month,tdy.day)

@route('/add')
@route('/webdict/add')
def addPg():
    return template('add.html', {'ip':request.urlparts.netloc,})

@route('/runAdd',method='POST')
@route('/webdict/runAdd',method='POST')
def addRec():
    name = request.POST.name
    ty = request.POST.ty
    pron = request.POST.pron
    ch = request.POST.ch
    sc1 = request.POST.sc1
    ex1 = request.POST.ex1
    
    conn = sqlite3.connect(DATA_PATH+DB)
    cursor = conn.cursor()
    cursor.execute('select " " dummy from newword where name=?',(name,))
    values = cursor.fetchone()
    if not values:
        cursor.execute('select max(id) dummy from newword where id like ?',(getDat()+'%',))
        ID=cursor.fetchone()[0]
        cursor.execute(
            'insert into newword (id, name, ty, pron, ch, sc1, ex1) values (?, ?, ?, ?, ?, ?, ?)'
            ,(str(int(ID)+1) if ID else str(int(getDat())*100), name, ty, pron, ch, sc1, ex1)
        )
        msg='新增完成!'
    else:
        msg="<div style='background-color:orange;'>"+'<div>'+name+'</div><div>'+ex1+'</div><div>資料已存在!!!</div></div>'
    cursor.close()
    conn.commit()
    conn.close()
    return "<p>"+msg+"</p><input id='addContinue' type='button' value='繼續'>"

@route('/qry',method='GET')
@route('/webdict/qry',method='GET')
#def qryRec():
def qryRec(name):
	conn = sqlite3.connect(DATA_PATH+DB)
	c = conn.cursor()
	#name=request.GET.name
	c.execute("SELECT * FROM newword where name like ? ORDER BY lower(name)",('%'+name+'%',))
	result = c.fetchall()
	c.execute("update newword set qry=ifnull(qry,0)+1, adat=? where lower(name)=? and ifnull(adat,'99991231')<>?",(getDat(), name.lower(),getDat(),))
	conn.commit()
	c.close()
	conn.close()
	#return template('make_table.html', {'rows':result,'ip':request.urlparts.netloc,})
	#print(template('make_table.html', {'rows':result,'ip':request.urlparts.netloc,}))
	f = open("result.txt", "w",encoding='utf8')
	f.write(template('make_table.html', {'rows':result,'ip':request.urlparts.netloc,}))
	f.close()

@route('/edit/<name>', method='GET')
@route('/webdict/edit/<name>', method='GET')
def edit_item(name):
	if request.GET.save:
		ty = request.GET.ty
		pron = request.GET.pron
		ch = request.GET.ch
		sc1 = request.GET.sc1
		ex1 = request.GET.ex1
		sc2 = request.GET.sc2
		ex2 = request.GET.ex2
		sc3 = request.GET.sc3
		ex3 = request.GET.ex3
		conn = sqlite3.connect(DATA_PATH+DB)
		c = conn.cursor()
		c.execute("UPDATE newword SET ty=?, pron=?, ch=?, sc1=?, ex1=?, sc2=?, ex2=?, sc3=?, ex3=?, txdat=? WHERE name=?", (ty, pron, ch, sc1, ex1, sc2, ex2, sc3, ex3, getDat(), name))
		c.close()
		conn.commit()
		conn.close()
		return template('''
			<p>{{msg}}</p>
			<input id='editContinue' type="button" value="繼續"">
			'''
			,{'msg':'更正完成!' if True else '', 'ip':request.urlparts.netloc,} 
		)
	else:
		conn = sqlite3.connect(DATA_PATH+DB)
		c = conn.cursor()
		c.execute("SELECT * FROM newword WHERE name=?", (name,))
		row = c.fetchone()
		c.close()
		conn.close()
		return template('edit.html', {'old':row, 'name':name, 'ip':request.urlparts.netloc,})

@route('/del/<name>', method='GET')
@route('/webdict/del/<name>', method='GET')
def del_item(name):
    if request.GET.save:
        conn = sqlite3.connect(DATA_PATH+DB)
        c = conn.cursor()
        c.execute("DELETE FROM newword WHERE name=?", (name, ))
        c.close()
        conn.commit()
        conn.close()
        return template('''
            <p>{{msg}}</p>
            <input id='delContinue' type="button" value="繼續"/>
            '''
            ,{'msg':'刪除完成!' if True else '', 'ip':request.urlparts.netloc, } 
        )
    else:
        conn = sqlite3.connect(DATA_PATH+DB)
        c = conn.cursor()
        c.execute("SELECT * FROM newword WHERE name=?", (name,))
        row = c.fetchone()
        c.close()
        conn.close()
        return template('del.html', {'old':row, 'name':name, 'ip':request.urlparts.netloc, })

@route('/pronounce/<name>', method='GET')
@route('/webdict/pronounce/<name>', method='GET')
def pronounce_item(name):
	if sys.platform == 'ios':
		return ""
	else:
		fileName='./tmp/'+name.replace(' ','_')+'.mp3'
		if not os.path.exists(fileName):
			tts=gTTS(text=name,lang='en')
			tts.save(fileName)
		return template("<audio src='http://{{ip}}/tmp/{{file}}' autoplay>",{'file':name.replace(' ','_')+'.mp3', 'ip':request.urlparts.netloc,})

@route('/test')
@route('/webdict/test')
def myTest():
    return template('test.html',{'name':'邵世昌'})

@route('/stk/imp')
@route('/webdict/stk/imp')
def stkImp():
	stk.imp()
	return json.dumps({'result': '轉檔成功！！！'})

@route('/stk/qry/<data>')
@route('/webdict/stk/qry/<data>')
def stkQry(data):
	return json.dumps({'result': stk.qry(data)})

@route('/main.html')
def main_html():
    #return template('/var/www/webdict/main.html')
    return template('./main.html')

@route('/tmp/<filename>')
def get_mp3(filename):
    response.content_type = 'audio/mp3'
    #with open('/var/www/webdict/tmp/'+filename, 'rb') as fh:
    with open('./tmp/'+filename, 'rb') as fh:
        content = fh.read()
    response.set_header('Content-Length', str(len(content)))
    return content

@route('/jpg/<filename>')
def get_jpg(filename):
    response.content_type = 'image/jpg'
    #with open('/var/www/webdict/jpg/'+filename, 'rb') as fh:
    with open('./jpg/'+filename, 'rb') as fh:
        content = fh.read()
    response.set_header('Content-Length', str(len(content)))
    return content

@route('/dictTest')
@route('/webdict/dictTest')
def dictTest():
	conn = sqlite3.connect('./dict.db')
	cursor = conn.cursor()
	cursor.execute('select id from newword')
	dictKeys = cursor.fetchall()
	dictKey=random.choice(dictKeys)[0]
	cursor.execute('select name,ty,ch,pron,sc1,ex1,sc2,ex2,sc3,ex3 from newword where id=?',(dictKey,))
	dictRow = cursor.fetchone()
	m=re.compile('('+dictRow[0][0]+')('+dictRow[0][1:-1]+')('+dictRow[0][-1]+')',re.I)
	responseText='<div>提示：'+dictRow[2]+'</div>'
	for cnt in (4,6,8):
		if dictRow[cnt] and dictRow[cnt]!='None':
			responseText=responseText+'<div>來源：'+dictRow[cnt]+'</div>' \
				+ '<div>' \
				+ m.sub(r'\1'+'<span style="background-color: black;">'+r'\2'+r'</span>'+r'\3',dictRow[cnt+1]) \
				+ '</div>'
	responseText=responseText \
		+'<div><label>請輸入答案：</label><input id="ansText" type="text"/>'\
		+	'<button class="pron" style="width:30px;height:30px;background-image:url('\
		+	"'http://"+request.urlparts.netloc+"/jpg/speaker.jpg');background-size:cover;"+'"></button>'\
		+	"<span class='spk'></span>"\
		+'</div>'\
		+'<div>'\
		+	'<input id="btnAnsSubmit" type="button" value="提交"/>'\
		+'</div>'
	cursor.close()
	conn.close()
	return json.dumps({
		'responseText': responseText, 
		'id':dictKey,
		'name':dictRow[0], 
		'ty':dictRow[1], 
		'ch':dictRow[2],
		'pron':dictRow[3],
		'sc1':dictRow[4],
		'ex1':dictRow[5],
		'sc2':dictRow[6],
		'ex2':dictRow[7],
		'sc3':dictRow[8],
		'ex3':dictRow[9],
	})

@route('/dictAns',method='POST')
@route('/webdict/dictAns',method='POST')
def dictAns():
	idKey = request.POST.id
	name = request.POST.name
	ty = request.POST.ty
	pron = request.POST.pron
	ch = request.POST.ch
	sc1 = request.POST.sc1
	ex1 = request.POST.ex1
	sc2 = request.POST.sc2
	ex2 = request.POST.ex2
	sc3 = request.POST.sc3
	ex3 = request.POST.ex3
	ans = request.POST.ans
	conn = sqlite3.connect('./dict.db')
	cursor = conn.cursor()
	cursor.execute('select ifnull(pass,0),ifnull(fail,0),ifnull(qry,0) from newword where id=?',(idKey,))
	dictRow = cursor.fetchone()
	passCnt=dictRow[0]
	failCnt=dictRow[1]
	qryCnt=dictRow[2]
	if name==ans:
		passCnt=passCnt+1
		cursor.execute('update newword set pass=?, tdat=? where id=?',(passCnt,getDat(),idKey,))
		responseText="<div>你的答案:["+ans+"]正確!!!"+name+"答對次數:"+str(passCnt)+" 答錯次數:"+str(failCnt)+" 查詢次數:"+str(qryCnt)+'</div>'
	else:
		failCnt=failCnt+1
		cursor.execute('update newword set fail=?, tdat=? where id=?',(failCnt,getDat(),idKey,))
		responseText="<div style='background-color:orange;'>你的答案:["+ans+"]錯誤!!!"+name+"答對次數:"+str(passCnt)+" 答錯次數:"+str(failCnt)+" 查詢次數:"+str(qryCnt)+'</div>' 
	responseText=responseText+'<div>詞性：'+ty+'</div>'+'<div>中文：'+ch+'</div>'+'<div>音標：'+pron+'</div>'+'<div>來源：'+sc1+'</div>'+'<div>'+ex1+'</div>'
	if sc2 and sc2!='None':
		responseText=responseText+'<div>來源：'+sc2+'</div>'+'<div>'+ex2+'</div>'
	if sc3 and sc3!='None':
		responseText=responseText+'<div>來源：'+sc3+'</div>'+'<div>'+ex3+'</div>'
	responseText=responseText \
		+'<div>'\
		+	'<input id="testContinue" type="button" value="繼續"/>'\
		+'</div>'
	cursor.close()
	conn.commit()
	conn.close()
	return responseText

if __name__ == "__main__":
	# run(host='localhost', path='/webdict', port=8080, debug=True)
	print(stkQry('1907'))
