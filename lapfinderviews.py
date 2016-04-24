from flask import render_template, request
from app import app


@app.route('/lapfinder')
def lapfinder():
	return render_template("lapfinderindex.html")


@app.route('/lapfinderoutput')
def lapfinderoutput():
	startaddress = request.args.get('LFID')
	closepool, pooladdress, laphours, today, website, hours = zipcounter.addresscoord(startaddress)
	
	return render_template("lapfinderoutput.html", closepool=closepool, pooladdress=pooladdress, laphours =laphours, today=today, website=website, hours = hours)
	


