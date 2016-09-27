import statsmodels.tsa.arima_model as ar
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings("ignore")



def getFt(input_array, k = 10):					#signal = input_array, the no. of terms to select from the fft is k

	sp = np.fft.fft(input_array)	
	for i in range(1,182-k):
		sp[i] = 0
		sp[182+k+i] = 0
	tp = np.fft.ifft(sp)
	return tp

def arima(input_array, start, k, order):							#start end are the values of dates for prediction
	x = getFt(input_array, k)
	inpt_array = input_array - x
	a = ar.ARIMA(inpt_array, order).fit()
	return a.predict(start, start+364)

def predict(input_array, start, k, order):
	X_t = abs(getFt(input_array, k).real) + abs(arima(input_array, start, k, order).real)
	plt.plot(input_array, 'r')
	plt.plot(X_t)
	plt.show()


def farima_predict(feature_count_array,feature):

        feature_array = []
        for i in range(1,366,1):
                feature_array.append(feature_count_array[feature][i])
	predict(feature_array, 1, 10, (2, 1,2))
