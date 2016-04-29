from flask import render_template, request
from app import app


@app.route('/lapfinder')
def lapfinder():
	return render_template("lapfinderindex.html")

@app.route('/lapfinderoutput')
def lapfinderoutput():
	#getting entered address
	try:
		startaddress = request.args.get('LFID')
		closepool, pooladdress, laphours, today, website, hours = zipcounter.addresscoord(startaddress)

		return render_template("lapfinderoutput.html", closepool=closepool, pooladdress=pooladdress, laphours =laphours, today=today, website=website, hours = hours)
	#getting direct pool choice from dropdown
	except:
		poolchoice = request.args.get('pool')
		if poolchoice == 'None':
			return render_template("lapfinderindexnone.html")
		else:
			closepool, pooladdress, laphours, today, website, hours = zipcounter.directpool(poolchoice)
		
			return render_template("lapfinderdirectoutput.html", closepool=closepool, pooladdress=pooladdress, laphours =laphours, today=today, website=website, hours = hours)
