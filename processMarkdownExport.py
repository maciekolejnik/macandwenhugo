import argparse
import os
import re
from datetime import datetime

parser = argparse.ArgumentParser()
# parser.add_argument("mdFilename")
parser.add_argument("folderName")
parser.add_argument("activityDate")
args = parser.parse_args()
# mdFilename = args.mdFilename
mdFilename = "post.md"
folderName = args.folderName

mdFilePath = "/Users/macio/Downloads/" + folderName + "/" + mdFilename
with open(mdFilePath) as mdInFile:
	mdInContent = mdInFile.readlines()

totalLines = len(mdInContent)

def generateImageURL(folderName, imgFileName):
	return "https://macandwen-media.s3.eu-west-2.amazonaws.com/" + folderName + "/" + imgFileName

def generateFrontMatter(title, publishdate, activitydate, coverImgURL, smallImgURL):
	def generateLine(key, value):
		return key + ": \"" + value + "\"\n"
	result = "---\n"
	result += generateLine("title", title)
	result += generateLine("publishdate", publishdate)
	result += generateLine("date", activitydate)
	result += generateLine("featured_image", coverImgURL)
	result += generateLine("small_image", smallImgURL)
	result += "---\n\n"
	return result

def retrieveTitle(titleLine):
	# format '# <title>'
	return titleLine.rstrip()[2:]

title = retrieveTitle(mdInContent[0])
publishdate = datetime.today().strftime('%Y-%m-%d')
activityDate = args.activityDate
coverImgURL = generateImageURL(folderName, "cover.jpeg")
smallImgURL = generateImageURL(folderName, "small.jpeg")

output = generateFrontMatter(title, publishdate, activityDate, coverImgURL, smallImgURL)

# skip the title line
lineIndex = 1

# skip any notion fields or empty lines
strippedLine = mdInContent[lineIndex].rstrip()
while lineIndex < totalLines and (len(strippedLine) == 0 or re.match(r'\w+: \w+', strippedLine)):
	lineIndex += 1
	strippedLine = mdInContent[lineIndex].rstrip()

output += "\n"
# now we are at content
while lineIndex < totalLines:
	inLine = mdInContent[lineIndex]
	imageURI = r'[-a-zA-Z0-9()@:%_\+.~#?&\/=]*\/([-a-zA-Z0-9()@:%_]+\.[a-z]{1,6})'
	if inLine.startswith("<iframe "):
		match = re.search(r'https?:\/\/(www\.)?([-a-zA-Z0-9@:%._\+~#=]{1,256})\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/=]*)', inLine)
		assert match is not None
		url = match.group()
		source = match.group(2)
		iframeUpdated = re.sub(r'src=(\'|\")\[.+\]\(.+\)(\'|\")', "src=\"" + url + "\"", inLine)
		div = "<div class=\"" + source + "-container\">\n"
		outLine = div + iframeUpdated + "</div>\n"
	elif re.match(r'!\[.+\]\(.+\)', inLine):
		match = re.search(imageURI, inLine)
		if match:
			filename = match.group(1)
			imageURL = generateImageURL(folderName, filename)
			output += "![](" + imageURL + ")\n"
			# check if image has description, if it does fix
			if (lineIndex+2 < totalLines):
				lineAfter = mdInContent[lineIndex+2].rstrip()
				# selection criteria - rather short and no dot at the end
				if len(lineAfter) < 100 and re.match(r'[A-Za-z][^.]*', lineAfter):
					output += "*" + lineAfter + "*\n"
					lineIndex += 2
	elif re.match(r'^[-*+]', inLine):
		# it's a list item, check for description in next line
		outLine = inLine.rstrip()
		if (lineIndex+1 < totalLines):
			lineAfter = mdInContent[lineIndex+1]
			if re.match(r'^[-*+]', lineAfter) is None:
				# if next line is description, enter two spaces to force newline
				outLine += "  "
		outLine += "\n"
	else:
		outLine = inLine
	output += outLine
	lineIndex += 1

# create a file to write to in posts directory
assert os.path.exists("content/post")
foutPath = "content/post/" + folderName + ".md" 

with open(foutPath, "w+") as fout:
	fout.write(output)

print("Succesfully written file " + foutPath)