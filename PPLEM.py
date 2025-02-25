
import numpy as np
from math import sqrt

import matplotlib.pyplot as plt_demand
import matplotlib.pyplot as plt_state
import matplotlib.pyplot as plt_price
import matplotlib.pyplot as plt

from phe import paillier
from timeit import default_timer as timer

import pandas as pd

import random
import sys

#import winsound
frequency = 1500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second

numToPlot = 10;

for i in range(numToPlot):
    globals()[f'price{i}'] = []
    globals()[f'demand{i}'] = []
	
for i in range(numToPlot):
	globals()[f'state{i}'] = []	



PLOT_TIME = 12
FiT= 8 ;
SupPrice = 40;

eta_1 = 3
eta_2 = 0.0001;
Theta = 25;
Lambda= 40.1;

STOP_difference = 0.05;

DATES = "_21_April"; Total_TIME = 24;
#DATES = "_6_November"; Total_TIME = 24;
#DATES = "_August"; Total_TIME = 744;
#DATES = "_January"; Total_TIME = 744;
#DATES = ""; Total_TIME = 8784;


def main(numUsers, ratProsumers):  

	percentageProsumers = ratProsumers;
	percentageBuyers = 100 - ratProsumers;

	numProsumers = int(numUsers * percentageProsumers / 100);
	numBuyers = int (numUsers * percentageBuyers / 100);
	
	Overall_Buyers_Demand = 0;
	Overall_BuyerFromP2P = 0;
 
	Overall_numSellers = 0;
	Overall_numProsumers = 0;

	Overall_pro_seller_consumption = 0;
	Overall_Total_Supplies = 0;
	Overall_pro_seller_ToP2P = 0 ;
	
	Overall_pro_consumer_from_Self = 0;
	Overall_pro_consumer_from_Supp = 0;

	Overall_Total_P2P_Profit = 0;

	File_Path_Generated  = "./PV_Generated_4KWp"+DATES+".csv"
	File_Path_Seller_Consumed= "./prosumer"+DATES+".csv"
	File_Path_Buyer_Consumed= "./buyer"+DATES+".csv"
	
	df_gen = pd.read_csv(File_Path_Generated,sep = ',',low_memory=False)		
	df_gen = df_gen.iloc[: , 2:]
	
	df_prosumer_con = pd.read_csv(File_Path_Seller_Consumed,sep = ',',low_memory=False)
	df_prosumer_con = df_prosumer_con.iloc[: , 2:]

	df_buyer_con = pd.read_csv(File_Path_Buyer_Consumed,sep = ',',low_memory=False)
	df_buyer_con = df_buyer_con.iloc[: , 2:]
	
	
	for time in range(0, Total_TIME):

		print(f"time {time} ---------- ")
		
		V_gen = df_gen.iloc[time].to_numpy()[0:numProsumers]
		V_prosumer_con = df_prosumer_con.iloc[time].to_numpy()[0:numProsumers]
		V_buyer_con = df_buyer_con.iloc[time].to_numpy()[0:numBuyers]
	
	
		energyDifference = [V_gen[i] - V_prosumer_con[i] for i in range(numProsumers)]

		Prosumer_isSellerArr = [diff > 0 for diff in energyDifference]	

		numSellers = sum(Prosumer_isSellerArr);
		
		Overall_numSellers +=numSellers;		
		Overall_numProsumers += numProsumers;
	
		Supplies= []

		for i in range(numProsumers):
			if Prosumer_isSellerArr[i]: # Seller
				
				Supplies.append(energyDifference[i])
				Overall_pro_seller_consumption += V_prosumer_con[i]

			else: # consumer				
				Overall_pro_consumer_from_Self += V_gen[i] 
				Overall_pro_consumer_from_Supp += V_prosumer_con[i] - V_gen[i] 
	
		TotalSupply = sum(Supplies);
		Overall_Total_Supplies += TotalSupply;

		TotalDemand = sum(V_buyer_con);
		Overall_Buyers_Demand += TotalDemand

		Overall_BuyerFromP2P += TotalDemand if TotalDemand <= TotalSupply else TotalSupply
		
		if(TotalSupply>TotalDemand):
			Supplies_to_P2P = [TotalDemand * supply/ TotalSupply for supply in Supplies]
			P2P_TOT = TotalDemand;
		else:
			Supplies_to_P2P = Supplies;	
			P2P_TOT = TotalSupply;
		
			
		if(sum(Supplies_to_P2P)):

			Overall_pro_seller_ToP2P += sum(Supplies_to_P2P)
			Overall_Total_P2P_Profit +=  LEM(Supplies_to_P2P, P2P_TOT, numBuyers,numSellers,time);
			
		
	BuyerFromSupp = Overall_Buyers_Demand  - Overall_BuyerFromP2P
	consumer_ratio = (Overall_numSellers)/Overall_numProsumers *100
	prosumer_seller_toGrid = Overall_Total_Supplies - Overall_pro_seller_ToP2P
		
	
	#print(Overall_BuyerFromP2P)
	#print(BuyerFromSupp)
	#print(consumer_ratio)
	
	#print(Overall_pro_seller_ToP2P)
	#print(prosumer_seller_toGrid)
	#print(Overall_pro_seller_consumption)
	#print(Overall_pro_consumer_from_Self);
	#print(Overall_pro_consumer_from_Supp);

	#print(Overall_Buyers_Demand * SupPrice/ 100 ,end=',  ')
	#print(Overall_pro_consumer_from_Supp *SupPrice/100,end=',  ')
	#print(Overall_Total_Supplies * FiT/100,end=',  ')

	#print(( Overall_Total_P2P_Profit )/100,end=',  ')
	#print((BuyerFromSupp * SupPrice  )/100,end=',  ')

	#print(( Overall_pro_consumer_from_Supp *SupPrice ) /100 ,end=',  ')
	#print(( Overall_Total_P2P_Profit )/100,end=',  ')
	#print((prosumer_seller_toGrid * FiT ) /100 ,end=',  ')


	
	
	
	

def LEM(Supplies_to_P2P, P2P_TOT, numBuyers,numSellers,time):

	public_key, private_key = paillier.generate_paillier_keypair()

	global numToPlot;
	numToPlot = min(10,numSellers) ;
	
	thetas = [Theta for _ in range(numBuyers)]
	lambdas = [Lambda for _ in range(numBuyers)]
	
	#P2P_TOT = sum(Supplies_to_P2P);
	
	#prices = [random.randrange(FiT +1,SupPrice) for _ in range(numSellers)];

	prices = [28, 24, 29, 35, 35, 37, 21, 35, 19, 22, 24, 23, 37, 17, 30, 33, 23, 37, 15, 29, 38, 14, 27, 29, 16, 18, 27, 35, 31, 17, 20, 13, 23, 14, 15, 20, 34, 30, 39, 9, 15, 20, 34, 25, 15, 20, 14, 29, 30, 34, 25, 27, 34, 13, 10, 11, 16, 31, 22, 15, 26, 38, 27, 12, 36, 10, 23, 34, 25, 33, 23, 27, 28, 24, 30, 26, 13, 15, 19, 28, 10, 32, 31, 10, 27, 25, 30, 20, 18, 11, 10, 9, 34, 9, 13, 33, 31, 12, 33, 26, 33, 38, 9, 34, 14, 25, 33, 28, 18, 30, 15, 12, 15, 13, 33, 12, 15, 19, 35, 19, 28, 9, 30, 15, 32, 30, 16, 32, 31, 20, 37, 21, 10, 14, 23, 24, 26, 17, 24, 39, 15, 12, 9, 14, 10, 12, 24, 12, 18, 20, 16, 24, 10, 18, 29, 28, 37, 20, 32, 36, 26, 11, 28, 15, 36, 21, 21, 33, 20, 28, 38, 24, 13, 28, 39, 39, 12, 17, 26, 33, 19, 9, 13, 11, 35, 36, 37, 28, 25, 10, 22, 19, 29, 12, 37, 38, 22, 25, 12, 27]
	
	if(time==PLOT_TIME):
		Total_Worst_Case_Time_Sellers = 0;
		Total_Worst_Case_Time_Buyers = 0;
		Total_Buyer_aggregation_time = 0;

	numIter = 0
		
	while(True):		
		
		numIter +=1;
		appendPrices(prices);
		
		if(time==PLOT_TIME):
			Worst_Case_Time_Sellers = 0;

			timer_ENC_HC = 0;

			cipherPrices= [];
			for seller in range(0,numSellers):	
				ENC_HC_start = timer()
				cipherPrices.append(Enc(public_key,prices[seller]));
				ENC_HC_end = timer()
				if((ENC_HC_end-ENC_HC_start)>timer_ENC_HC):
					timer_ENC_HC = ENC_HC_end-ENC_HC_start;
			
			Worst_Case_Time_Sellers +=timer_ENC_HC;

			cipherWelfares , cipher_Wtot, Worst_Case_Time_Buyers, Buyer_aggregation_time = evolutionaryGame_Enc(public_key,private_key,cipherPrices,numBuyers,numSellers);

			sellerWelfares_RND = [];	

			timer_DEC_HC = 0;				

			for C_welfare in cipherWelfares:
				DEC_HC_start = timer()
				sellerWelfares_RND.append(round(Dec(private_key,C_welfare),2));
				DEC_HC_end = timer()
				if((DEC_HC_end-DEC_HC_start)>timer_DEC_HC):
					timer_DEC_HC = DEC_HC_end-DEC_HC_start;
			
			
			Wtot_dec = Dec(private_key,cipher_Wtot)
			Worst_Case_Time_Sellers +=timer_DEC_HC;

			#print('Worst_Case_Time_Sellers',Worst_Case_Time_Sellers)
			#print('Worst_Case_Time_Buyers',Worst_Case_Time_Buyers)
			#print('Buyer_aggregation_time',Buyer_aggregation_time)

			Total_Worst_Case_Time_Sellers += Worst_Case_Time_Sellers;
			Total_Worst_Case_Time_Buyers += Worst_Case_Time_Buyers;
			Total_Buyer_aggregation_time += Buyer_aggregation_time;
			

		#print('sellerWelfares_temp_RND',sellerWelfares_temp_RND);
		#print('sellerWelfares round',sellerWelfares_RND);

		#print('cipher_Wtot', Dec(private_key,cipher_Wtot))
		
		
		
		W_B_J , W_TOT = buyers_algorithm(prices, thetas, lambdas, numSellers);
		#print('W_B_J',W_B_J)
		#print('W_TOT',W_TOT)
		
		Demands = [P2P_TOT*W_B_J[s_j]/W_TOT for s_j in range(0,numSellers)]
		
		appendDemands(Demands);
		for seller in range(0,numSellers):	
			tempPrice = prices[seller]+eta_1*(Demands[seller]-Supplies_to_P2P[seller]);
			prices[seller] = min(SupPrice,max(FiT,tempPrice));	

	
		
		exit=1;
		for seller in range(0,numSellers):
			if(abs((Demands[seller]-Supplies_to_P2P[seller]))>STOP_difference):
				exit=0;
				break;
			
		
		if(exit==1):

			Total_P2P_Profit = 0;
			
			for seller in range(0,numSellers):	
				Total_P2P_Profit += Supplies_to_P2P[seller] * prices[seller];
			
			if(time==PLOT_TIME):
				print('Total_Worst_Case_Time_Sellers',Total_Worst_Case_Time_Sellers)
				print('Total_Worst_Case_Time_Buyers',Total_Worst_Case_Time_Buyers)
				print('Total_Buyer_aggregation_time',Total_Buyer_aggregation_time)
				print('numIter',numIter)
				print(prices)
				plotPrices();
				plotDemand();	
			
			clearPlots();
			return Total_P2P_Profit;
					




def appendPrices(prices):
    for i in range(numToPlot):
        globals()[f"price{i}"].append(prices[i])

def appendDemands(sellerDemands):
    for i in range(numToPlot):
        globals()[f"demand{i}"].append(sellerDemands[i])
	
def appendStates(states):
    for i in range(numToPlot):
        globals()[f"state{i}"].append(states[i])
	
def clearPlots():
	for i in range(numToPlot):	
		globals()[f"price{i}"].clear()
		globals()[f"demand{i}"].clear()
		globals()[f"state{i}"].clear()
	
def plotDemand():
	
	for i in range(0, numToPlot):
		plt_demand.plot(globals()[f"demand{i}"], label=f"S {i+1}")
	
	plt_demand.legend(ncol=5, bbox_to_anchor=(0.5, 1.13),loc='upper center', fontsize='small')
	plt_demand.xlabel("Seller Iteration")
	plt_demand.ylabel("Power Demands (kW)")
	plt_demand.show()

def plotStates():

	for i in range(numToPlot):
		plt_state.plot(globals()[f"state{i}"], label=f"S {i+1}")

	plt_state.legend(ncol=5, bbox_to_anchor=(0.5, 1.13),loc='upper center', fontsize='small')
	plt_state.xlabel("Seller Iteration")
	plt_state.ylabel("States")
	plt_state.show()

def plotPrices():
	
	for i in range(numToPlot):
		plt_price.plot(globals()[f"price{i}"], label=f"S {i+1}")	

	plt_price.legend(ncol=5, bbox_to_anchor=(0.5, 1.13),loc='upper center', fontsize='small')
	plt_price.xlabel("Seller Iteration")
	plt_price.ylabel("Power Price (cents / kWh)")
	plt_price.show()


class ciphertext:
    def __init__(self, a):
        self.a = a;
        self.B = [];

def Enc(public_key,m):
	
	return ciphertext(public_key.encrypt(m));

def Dec(private_key,ciphertext):
	
	decVal=private_key.decrypt(ciphertext.a);
	for b in ciphertext.B:
		decVal+= ( private_key.decrypt(b) **2 )
	return decVal;

def Add(c1,c2):
	cRet = ciphertext(c1.a + c2.a);
	cRet.B.extend(c1.B);
	cRet.B.extend(c2.B);
	return cRet;

def Smul(cipher,k):
	cRet = ciphertext(cipher.a * k)
	
	for i in range(len(cipher.B)):
		cRet.B.append(cipher.B[i] *sqrt(k));

	return cRet;

def Squaring(public_key,cipher):
	
	if(len(cipher.B) != 0):
		print('B should be empty');
		exit()

	r = random.randint(1,10);

	B = cipher.a + (-1) * r; # m-r

	a = (-1) * (r**2) + 2*r * cipher.a ;  # -r ^ 2 + 2rm

	cRet = ciphertext(a);
	cRet.B.append(B);

	return cRet;

def buyers_algorithm(prices, thetas, lambdas, numSellers):
    
	
    N_B = len(lambdas)
    N_S = numSellers
   	
    X = [[0] * N_B for _ in range(N_S)]
    W_B_J = [0] * N_S
     
    
    for j in range(N_S):
        for i in range(N_B):
            X[j][i] = (lambdas[i] - prices[j]) / thetas[i]; #print(f'No X[{j}][{i}]',X[j][i])           
        W_B_J[j] = 0.5 * sum(thetas[i] * X[j][i]**2 for i in range(N_B))
    
    W_TOT = sum(W_B_J)
    
    
    return W_B_J, W_TOT


def evolutionaryGame_Enc(public_key,private_key,Enc_prices,numBuyers,numSellers):
	
	
	N_B = numBuyers
	N_S = numSellers
   	
	X_Enc = [[0] * N_B for _ in range(N_S)]
	W_B_J = [0] * N_S


	Enc_welfares=[];
	
	Worst_Case_Time_Buyers = 0 ;

	for i in range(0,numBuyers):
		Buyer_HC_start = timer()
		for j in range(0,numSellers):
			X_Enc[j][i] = ciphertext (((-1) * Enc_prices[j].a + Lambda ) * (1/Theta));	
		Buyer_HC_end = timer()
		if((Buyer_HC_end-Buyer_HC_start)>Worst_Case_Time_Buyers):
					Worst_Case_Time_Buyers = Buyer_HC_end-Buyer_HC_start;

	#print("Worst_Case_Time_Buyers",Worst_Case_Time_Buyers);

	aggregation_time=0;

	for j in range(0,numSellers):
		#for i in range(0,numBuyers):
		#	print(f'X_Enc[{j}][{i}]',Dec(private_key, X_Enc[j][i]))
					
				
		agg_start = timer();
		W_B_J[j] = Smul(Squaring(public_key,X_Enc[j][0]),(Theta/2));
	
		for buyer in range(1,numBuyers):

			W_B_J[j] = Add( W_B_J[j] , Smul(Squaring(public_key,X_Enc[j][buyer]),(Theta/2)))	

		agg_end = timer();

		aggregation_time += agg_end - agg_start;

	

	Wtot_start = timer();
	W_TOT = W_B_J[0]; 
	for j in range(1,numSellers):
		W_TOT= Add(W_TOT,W_B_J[j])
	Wtot_end = timer();

	Wtot_time = Wtot_end - Wtot_start;

	aggregation_time += Wtot_time

	#print("aggregation_time",aggregation_time);

	return W_B_J, W_TOT, Worst_Case_Time_Buyers, aggregation_time;

if __name__ == '__main__':	
	

	public_key, private_key = paillier.generate_paillier_keypair()
	X = Enc(public_key,23434234)
	
	print(sys.getsizeof(X ))
	quit()
	print("40,25")
	main(40,25)
	print("80,25")
	main(80,25)	
	print("120,25")
	main(120,25)
	print("160,25")
	main(160,25)
	print("200,25")
	main(200,25)

	print("40,50")
	main(40,50)
	print("80,50")
	main(80,50)
	print("120,50")
	main(120,50)
	print("160,50")
	main(160,50)
	print("200,50")
	main(200,50)

	print("40,75")
	main(40,75)
	print("80,75")
	main(80,75)
	print("120,75")
	main(120,75)
	print("160,75")
	main(160,75)
	print("200,75")
	main(200,75)	
	
	#winsound.Beep(frequency, duration)

	print("Finished MMM!")
	




	



