from flask import Flask,render_template,request,url_for,redirect,send_file

app=Flask(__name__)

@app.route("/",methods=["POST","GET"])
def home():
    return render_template("index.html")

@app.route('/download')
def download():
	path = "BrokenLinks.csv"
	return send_file(path, as_attachment=True)

app.run(debug=True)