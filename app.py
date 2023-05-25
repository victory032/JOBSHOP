from flask import Flask,render_template,request,url_for,redirect,flash,jsonify
from werkzeug.utils import secure_filename
from jobShop import JobShop
import json
import os
import urllib.request
from werkzeug.utils import secure_filename
import re

UPLOAD_FOLDER = 'Files'
ALLOWED_EXTENSIONS = {'txt', 'xls','xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def longest(x):
    if isinstance(x,list):
        yield len(x)
        for y in x:
            yield from longest(y)
def read_txt(filename):
    l=[]
    mch_nb=0
    
    with open(filename,'r') as f:
        f1=f.readlines()
        for line_no, line in enumerate(open(filename)):
            myIntegers = [int(x) for x in line.split()] 
            mch_nb= len(myIntegers)
        f2=[]
        for line in f1:
            x=re.sub(' +', ' ',line)
            f2.append(x)
        l = [[int(num)  for num in line.split(" ")] for line in f2 ]
        logst=max(longest(l))
        resp=all([c.replace(" ","").replace("\n","").isdigit() for c in f2])
        if resp==True:           
            return logst,l,mch_nb
        else:
            return "Fichier non valide"



@app.route("/jobshop/home",methods=["GET"])
def home():
    return render_template("index.html")
@app.route('/', methods=["GET"])
def defaultRoot():
    return redirect(url_for("home"))
@app.route("/jobshop/manual", methods=["GET","POST"])
def manual():
    if request.method=="GET":
        return render_template("grid.html")
    else:
        data=request.get_json()["data"]
        data=data[1:]
        data1=[]
        for d1 in data:
            j=0
            data11=[]            
            for d2 in d1:
                t=(j,int(d2))
                data11.append(t)
                j+=1
            data1.append(data11)
        lst,tps=JobShop().MinimalJobshopSat(data1)      
        return  json.dumps({"time":tps,"data":lst})

@app.route("/jobshop/From_File",methods=["GET","POST"])
def from_file():
    if request.method=="GET":
        return render_template("file.html")
    else:
        # check if the post request has the file part
        if 'files[]' not in request.files:
            #
            resp = jsonify({'message' : 'Aucun fichier'})
            resp.status_code = 400
            return resp
        
        files = request.files.getlist('files[]')
        
        errors = {}
        success = False 
        filename=""       
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                success = True
            else:
                #errors[file.filename] = 'File type is not allowed'
                errors[file.filename] = 'Format du fichier non supporté'
        
        if success and errors:
            #errors['message'] = 'File(s) successfully uploaded'
            errors['message'] = 'Fichier téléchargé avec succès'
            resp = jsonify(errors)
            resp.status_code = 206
            return resp
        if success:
            resp = jsonify({"message":"Fichier téléchargé avec succès"})
            resp.status_code = 201
            if ".txt" in os.path.join(app.config['UPLOAD_FOLDER'], filename):
                lgst,data,mch_nb=read_txt(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                return jsonify({"message":"Fichier téléchargé avec succès","longueur":lgst,"Data":data,"mchnb":mch_nb})

        else:
            resp = jsonify(errors)
            #resp.status_code = 400
            return resp








if __name__=="__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    #sess.init_app(app)
    app.run(debug=True)