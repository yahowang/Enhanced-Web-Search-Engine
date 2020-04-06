from flask import Flask,render_template,request
import json
import nltk
import heapq
from collections import defaultdict
from nltk.corpus import stopwords
import re
app = Flask(__name__)
with open("bookkeeping.json") as bookkeep:
    bookKeepDict = json.load(bookkeep)
with open("index.json") as dictionary:
    invertedIndex = json.load(dictionary)


class Retriver:
    def __init__(self, rawText):
        self.stopw = set(stopwords.words("english"))
        self.wnl = nltk.stem.WordNetLemmatizer()
        self.terms = self._cleanText(rawText)

    def getTopK(self, k):
        global bookKeepDict
        minheap = []
        localIndex = defaultdict(list)

        for docID in bookKeepDict:
            score = -self._calcCosine(docID)
            if score < 0:
                if score not in minheap:
                    heapq.heappush(minheap, score)
                localIndex[score].append(docID)

        result = []
        count = 0
        while True:
            if minheap == []:
                return result
            for docID in localIndex[heapq.heappop(minheap)]:
                if count < k:
                    count += 1
                    result.append(docID)
                else:
                    return result

    def showIndex(self):
        for term in self.terms:
            return invertedIndex[term]

    def _cleanText(self, rawText):
        return self._cleanStopwords([self.wnl.lemmatize(token.lower()) for token in re.findall(r"[a-zA-Z0-9]+", rawText)])

    def _cleanStopwords(self,terms):
        return [term for term in terms if term not in self.stopw]

    def _calcCosine(self, docID):
        score = 0
        for term in self.terms:
            for doc in invertedIndex[term]:
                if doc[0] == docID:
                    score += doc[1]
                    break
        return score


@app.route('/helloworld')
def hello_world():
    return 'Hello World!'


# @app.route("/index")
# def homepage():
#     return render_template("index.html")

@app.route("/index")
def passvalue():
    getparam = request.args["res"]
    resulttext = Retriver(getparam)
    topkres = resulttext.getTopK(10)
    fullres = []
    for i in topkres:
        fullrestext = i+'\n' + "http://"+bookKeepDict[i]
        fullres.append(fullrestext)
    return render_template("index.html",name = "\n".join(fullres))


if __name__ == '__main__':
    app.run()
