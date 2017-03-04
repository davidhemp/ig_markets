#For loading and saving data
class loader:
	def __init__(self,quiet=True):
		self.quiet = quiet

	def generatefilename(self,ending=".txt"):
		from datetime import datetime
		filename = datetime.now().strftime("%Y%m%d-%H%M%S") + ending
		return filename

	def savedata(self,data,filename=None,path="./"):
		from functions import arrayshape
		if filename == None:
			filename = self.generatefilename()
		savename = path + filename
		with open(savename,'w') as fw:
			if not self.quiet:
				fw.write(\
					raw_input("Please write any comments you have:") + "\n")
			for i in range(len(data[0])):
				line = ""
				for j in range(len(arrayshape(data))):
					line += "%s," %data[j][i]
				fw.write(line[:-1] + "\n")

	def loaddata(self,filename):
		data = []
		with open(filename) as f:
			i=0
			data = []
			for line in f:
				loadline = []
				linedata = line.strip().split(',')
				if len(linedata) >= 2:
					for j in range(7):
						loadline.append(linedata[j])
					i+=1
				data.append(loadline)
		return data
