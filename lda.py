import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

ati=pd.read_csv('extracted data.csv',sep=',')

def my_tokenizer(doc):
    keywords=doc.split(';')
    return keywords


vectorizer = CountVectorizer(tokenizer=my_tokenizer)
X = vectorizer.fit_transform(ati['Research areas'])

for feature in vectorizer.get_feature_names():
    if(feature=="['n/a']"):
        mask.append(False)
    else:
        mask.append(True)
mask=np.array(mask)
X=X[:,mask] #remove ['n/a'] feature
X=X[:,1:]#remove first columns as it is not a valuable feature


lda = LatentDirichletAllocation(n_components=5,
    random_state=0)
lda.fit(X)

#transform the features to get a probability mask
lda.transform(X)