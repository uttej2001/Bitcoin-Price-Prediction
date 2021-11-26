#!/usr/bin/env python
# coding: utf-8

# In[1]:

# importing essential libraries
from flask import Flask, render_template, request, url_for
from keras.models import model_from_json
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler



# In[2]:

# load json and create model
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)
# load weights into new model
model.load_weights("model.h5")
print("Loaded model from disk")

model.compile(loss='mean_squared_error', optimizer='adam')
# In[3]:


df = pd.read_pickle('./dfe.pkl')


# In[4]:

app= Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/predict', methods=['POST','GET'])
def predict():
    if request.method== 'POST':
        
        date = request.form['date']
        n = int(request.form['n'])
        
        
        loc = df.index.get_loc(date)
        prev_data = df.iloc[loc-15:loc].Price.astype(float)
        #orig_data = df.iloc[loc:loc+n].Price.astype(float)
        
        min_max_scaler = MinMaxScaler(feature_range=(0, 1))
        ds = min_max_scaler.fit_transform(prev_data.values.reshape(-1, 1))
        ds = ds.reshape(1,15,1)
        

        look_back=15
        x_input = ds[len(ds)-look_back:].reshape(1,-1)

        temp_input=list(x_input)
        temp_input=temp_input[0].tolist()
        
        lst_output=[]
        i=0
        #n=15   # next number of days for which we are predicting
        while(i<n):

            if(len(temp_input)>look_back):
                x_input=np.array(temp_input[1:])
                x_input=x_input.reshape(1,-1)
                x_input = x_input.reshape((1, look_back, 1))
                yhat = model.predict(x_input, verbose=0)
                temp_input.extend(yhat[0].tolist())
                temp_input=temp_input[1:]
                lst_output.extend(yhat.tolist())
                i=i+1
            else:
                x_input = x_input.reshape((1, look_back,1))
                yhat = model.predict(x_input, verbose=0)
                temp_input.extend(yhat[0].tolist())
                lst_output.extend(yhat.tolist())
                i=i+1

        res = min_max_scaler.inverse_transform(lst_output)
        
        #day_new=np.arange(1, look_back+1)
        #day_pred=np.arange(look_back+1, look_back+n+1)

        #trainScore = math.sqrt(mean_squared_error(orig_data, res))
        
        return render_template('result.html', res=res, len=len(res), n=n, date=date)


if __name__ == "__main__":
    app.run()


# In[ ]:



