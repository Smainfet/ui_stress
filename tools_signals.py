import csv
import math
import os
from datetime import datetime, timedelta
from typing import Tuple

import antropy as ent
import matplotlib.pyplot as plt
import neurokit2 as nk
import numpy as np
import pandas as pd
import pywt
import scipy
import scipy.io as sio
import tsfel
# import hrvanalysis
from hrv.classical import frequency_domain, non_linear, time_domain
from mat4py import loadmat
from neurokit2.hrv.hrv_utils import _hrv_get_rri, _hrv_sanitize_input
from scipy import signal
from scipy.interpolate import interp1d
from scipy.io import savemat
from scipy.stats import entropy
from sklearn.utils import resample


class ManagerTools():

    def __init__(self):
        pass

    def SCR_features(self, SCR_feat):
        features1_df = pd.DataFrame(SCR_feat, index=['SCR_mean_Amplitude', 'SCR_mean_Height', 'SCR_mean_Recovery',
                                                     'SCR_mean_RiseTime'])
        SCR_features1_df = features1_df.mean(axis=1)
        SCR_features1_df['SCR_number'] = 100 * features1_df.iloc[0].count()
        SCR_features1_df = pd.DataFrame(SCR_features1_df).transpose().fillna(0)

        return (SCR_features1_df)

    def signal_features(self, signals1,signalType,infoSignal):

        if(signalType=="EDA"):
            signals1 = signals1[['EDA_Raw', 'EDA_Clean', 'EDA_Tonic', 'EDA_Phasic']]
            ss = signals1[['EDA_Clean']].to_numpy().flatten(order='C')
        if(signalType=="PPG"):
            signals1 = signals1[['PPG_Raw', 'PPG_Clean', 'PPG_Rate', 'PPG_Peaks','PPG_HRV']]
            ss = signals1[['PPG_Clean']].to_numpy().flatten(order='C')
            hrv_signal=signals1["PPG_HRV"].to_numpy()
            hrv_signal=[num for num in hrv_signal if num!=0]
            hrv_feat=hrv_features(hrv_signal,False)
            print(hrv_feat)

        # Define signal for EMD
        

        # Execute EMD on signal

        # ********************** Add IMF1 to signals ********************
        # signals1 = pd.concat([signals1,IMFs])
        signals1 = pd.concat([signals1])
        
        # ********************** Signal features ************************
        mins = signals1.min(axis=0)
        mins = pd.DataFrame(mins).transpose().fillna(0)
        

        means = signals1.mean(axis=0)
        means = pd.DataFrame(means).transpose().fillna(0)


        medians = signals1.median(axis=0)
        medians = pd.DataFrame(medians).transpose().fillna(0)
        


        maxs = signals1.max(axis=0)
        maxs = pd.DataFrame(maxs).transpose().fillna(0)
       


        variances = signals1.var(axis=0)
        variances = pd.DataFrame(variances).transpose().fillna(0)
        

        stds = signals1.std(axis=0)
        stds = pd.DataFrame(stds).transpose().fillna(0)
        

        energy = pd.Series(np.power(signals1, 2).sum())
        energy = pd.DataFrame(energy).transpose()
        


        RMSE = (energy / len(signals1)) ** (1 / 2)
       

        kurts = signals1.kurtosis(axis=0)
        kurts = pd.DataFrame(kurts).transpose().fillna(0)

        skews = signals1.skew(axis=0)
        skews = pd.DataFrame(skews).transpose().fillna(0)
        # N_imfs = len(IMF)

        if(signalType=="PPG"):
            mins["PPG_HRV"]=pd.concat([hrv_feat["lf/hf_WT"]]).mean(axis=0)
            medians["PPG_HRV"]=hrv_feat.at[0,"rmssd"]
            maxs["PPG_HRV"]=hrv_feat.at[0,"pnn50"]
            variances["PPG_HRV"]=hrv_feat.at[0,'sdnn']
            energy["PPG_HRV"]=pd.concat([hrv_feat["hf_WT"]]).mean(axis=0)
            RMSE["PPG_HRV"]=pd.concat([hrv_feat["lf_WT"]]).mean(axis=0)

        feat = ['RMSE', 'energy', 'min', 'mean', 'median', 'max', 'var', 'std', 'kurt', 'skew']

        signals1_features = pd.concat(
            [RMSE, energy, mins, means, medians, maxs, variances, stds, kurts, skews], keys=feat, axis=1)
        
        if(signalType=="EDA"):
            signals1_features.columns = ['RMSE_raw', 'RMSE_clean', 'RMSE_tonic', 'RMSE_phasic',
                                        'energy_raw', 'energy_clean', 'energy_tonic', 'energy_phasic',
                                        'min_raw', 'min_clean', 'min_tonic', 'min_phasic',
                                        'mean_raw', 'mean_clean', 'mean_tonic', 'mean_phasic',
                                        'median_raw', 'median_clean', 'median_tonic', 'median_phasic',
                                        'max_raw', 'max_clean', 'max_tonic', 'max_phasic',
                                        'var_raw', 'var_clean', 'var_tonic', 'var_phasic',
                                        'std_raw', 'std_clean', 'std_tonic', 'std_phasic',
                                        'kurt_raw', 'kurt_clean', 'kurt_tonic', 'kurt_phasic',
                                        'skew_raw', 'skew_clean', 'skew_tonic', 'skew_phasic'
                                        ]
        elif(signalType=="PPG"):
            signals1_features.columns = ['RMSE_raw', 'RMSE_clean', 'RMSE_tonic', 'RMSE_phasic','LF_hrv',
                                        'energy_raw', 'energy_clean', 'energy_tonic', 'energy_phasic','HF_hrv',
                                        'min_raw', 'min_clean', 'min_tonic', 'min_phasic','LF/HF_hrv',
                                        'mean_raw', 'mean_clean', 'mean_tonic', 'mean_phasic','mean_hrv',
                                        'median_raw', 'median_clean', 'median_tonic', 'median_phasic','RMSSD_hrv',
                                        'max_raw', 'max_clean', 'max_tonic', 'max_phasic','PNN50_hrv',
                                        'var_raw', 'var_clean', 'var_tonic', 'var_phasic','SDNN_hrv',
                                        'std_raw', 'std_clean', 'std_tonic', 'std_phasic','std_hrv',
                                        'kurt_raw', 'kurt_clean', 'kurt_tonic', 'kurt_phasic','kurt_hrv',
                                        'skew_raw', 'skew_clean', 'skew_tonic', 'skew_phasic','skew_hrv'
                                        ]

        # signals1_features["N_IMFs"] = N_imfs

        # print(signals1_features)
        return (signals1_features)

    def EDA_processing(self, eda_signal3, timestamps, fs):
        [eda_signal3, timestamps_resampled] = signal.resample(eda_signal3, int(len(eda_signal3) / 16), timestamps)
        eda_signal3_filt = nk.signal_filter(eda_signal3, sampling_rate=fs, highcut=0.05, method='butterworth',
                                            order=4)

        # Process the raw EDA signal
        # signals, info = nk.eda_process(eda_signal,method='neurokit')
        signals3, info3 = nk.eda_process(eda_signal3_filt)

        # Extract clean EDA and SCR features ***************************************

        cleaned3 = signals3["EDA_Clean"]
        features3 = [info3["SCR_Onsets"], info3["SCR_Peaks"], info3["SCR_Recovery"]]

        # Select SCR features according to conditions ***************************************
        #     min_SCRamplitude = 0.01

        for i in range(1, len(info3["SCR_Onsets"])):
            diff = info3["SCR_Onsets"][i] - info3["SCR_Peaks"][i - 1]
            if diff < 1000:
                if info3["SCR_Height"][i] < info3["SCR_Height"][i - 1]:

                    info3["SCR_Amplitude"][i - 1] = info3["SCR_Amplitude"][i] + info3["SCR_Amplitude"][i - 1]

                    info3["SCR_Onsets"][i] = 0
                    info3["SCR_Recovery"][i] = 0
                    info3["SCR_Peaks"][i] = 0
                    info3["SCR_RiseTime"][i] = 0
                    info3["SCR_Height"][i] = 0

                else:
                    info3["SCR_Amplitude"][i] = info3["SCR_Amplitude"][i] + info3["SCR_Amplitude"][i - 1]

                    info3["SCR_Onsets"][i - 1] = 0
                    info3["SCR_Recovery"][i - 1] = 0
                    info3["SCR_Peaks"][i - 1] = 0
                    info3["SCR_RiseTime"][i - 1] = 0
                    info3["SCR_Height"][i - 1] = 0

        #             info3["SCR_Amplitude"][i-1] = max(info3["SCR_Amplitude"][i], info3["SCR_Amplitude"][i-1])

        #             amp_cond3 = np.where(info3["SCR_Onsets"][i] < diff_min, 0, info3["SCR_Amplitude"])

        amp_cond3 = np.where(info3["SCR_Amplitude"] < 0.05, 0, info3["SCR_Amplitude"])

        info3["SCR_Onsets"] = info3["SCR_Onsets"][amp_cond3 > 0]
        info3["SCR_Recovery"] = info3["SCR_Recovery"][amp_cond3 > 0]
        info3["SCR_Peaks"] = info3["SCR_Peaks"][amp_cond3 > 0]
        info3["SCR_RiseTime"] = info3["SCR_RiseTime"][amp_cond3 > 0]

        info3["SCR_Amplitude"] = info3["SCR_Amplitude"][amp_cond3 > 0]
        info3["SCR_Height"] = info3["SCR_Height"][amp_cond3 > 0]

        SCR_features3 = [info3["SCR_Amplitude"], info3["SCR_Height"], info3["SCR_Recovery"], info3["SCR_RiseTime"]]

        features3 = [info3["SCR_Onsets"], info3["SCR_Peaks"], info3["SCR_Recovery"]]

        # Visualize SCR features in cleaned EDA signal ***************************************
        plot = nk.events_plot(features3, cleaned3, color=['red', 'blue', 'orange'])

        # Filter phasic and tonic components ***************************************
        data3 = nk.eda_phasic(nk.standardize(eda_signal3_filt, robust=True))
        # eda_phasic = data["EDA_Phasic"].values

        # Plot EDA signal ***************************************

        return (signals3, SCR_features3, timestamps_resampled)

    
                

    def PPG_processing(self, ppg_signal3, timestamps, fs):

        [ppg_signal3, timestamps_resampled] = [ppg_signal3, timestamps]
        signals3, info3 = nk.ppg_process(ppg_signal3,513)
        HRV_signal = np.zeros(len(signals3["PPG_Peaks"])) 

        index_precedent=0
        for i in range(len(signals3["PPG_Peaks"])):
    
            if(signals3["PPG_Peaks"][i]==1 and i!=0) :
                HRV_signal[index_precedent]=timestamps_resampled[i]-timestamps_resampled[index_precedent]
                index_precedent=i

        signals3.insert(4, "PPG_HRV", HRV_signal)

        tempo=-1 
        for i in range(len(signals3["PPG_Peaks"])):
            if (signals3["PPG_Peaks"][i]!=0) :
                tempo=2
            elif(tempo>0) :
                tempo=tempo-1
            elif(tempo==0) : 
                signals3["PPG_Peaks"][i-5:i-1]=1
                tempo=-1
        
    
        return (signals3, timestamps_resampled,info3)


def calculate_real_time(rrs):
    acc = 0
    real_time = []

    for rr in rrs:
        real_time.append(acc)
        acc = acc + rr

    return real_time



def calc_true_hr(rrs):
    hrs = []
    for rr in rrs:
        hr = 60 * 1000 / rr
        hrs.append(hr)
    return hrs


def calc_true_time_domain(rrs, log):
    cumulDecalage = 0
    index_decalage = [0]
    output = pd.DataFrame()

    for i in range(0, len(rrs)):

        if (cumulDecalage + rrs[i]) < 60:
            cumulDecalage += rrs[i]
        else:
            index_decalage.append(i)
            cumulDecalage = 0
            if log:
                print('index_decalage  : ', index_decalage)

    j=5  # On prend la cinquièment valeur
    if log:
        print("index_decalage[j-4], index_decalage[j] : --> ", index_decalage[j - 5], index_decalage[j])
        print("window length --> ", sum(rrs[index_decalage[j - 5]:index_decalage[j]]) / 1000)
        
    # Time Domain Features    

    tdom = time_domain(rrs[index_decalage[j - 5]:index_decalage[j]])
    
    # Non linear Domain

    nl = non_linear(rrs[index_decalage[j - 5]:index_decalage[j]])
    
    # TSFEL statistical
    ll = rrs[index_decalage[j - 5]:index_decalage[j]]
    vect = ll
    
#         cfg_file_stats = tsfel.get_features_by_domain('statistical') # If no argument is passed retrieves all available features
#         tsfel_feat_stats = tsfel.time_series_features_extractor(cfg_file_stats,vect)

    abs_energy =  tsfel.feature_extraction.features.abs_energy(vect)
    autocorr =  tsfel.feature_extraction.features.autocorr(vect) 
    mean =  tsfel.feature_extraction.features.calc_mean(vect) 
    median =  tsfel.feature_extraction.features.calc_median(vect) 
    std =  tsfel.feature_extraction.features.calc_std(vect)
    entropy =  tsfel.feature_extraction.features.entropy(vect) 
    interq_range =  tsfel.feature_extraction.features.interq_range(vect) 
    kurtosis =  tsfel.feature_extraction.features.kurtosis(vect) 
    mean_abs_dev =  tsfel.feature_extraction.features.mean_abs_deviation(vect) 
    mean_abs_diff =  tsfel.feature_extraction.features.mean_abs_diff(vect) 
    mean_diff =  tsfel.feature_extraction.features.mean_diff(vect) 
    median_abs_dev =  tsfel.feature_extraction.features.median_abs_deviation(vect) 
    median_abs_diff =  tsfel.feature_extraction.features.median_abs_diff(vect) 
    median_diff =  tsfel.feature_extraction.features.median_diff(vect) 
    skewness =  tsfel.feature_extraction.features.skewness(vect) 
    slope =  tsfel.feature_extraction.features.slope(vect) 
#         kurtosis =  tsfel.feature_extraction.features.features.kurtosis(vect) 
#         kurtosis =  tsfel.feature_extraction.features.features.kurtosis(vect) 
#         kurtosis =  tsfel.feature_extraction.features.features.kurtosis(vect) 
#         kurtosis =  tsfel.feature_extraction.features.features.kurtosis(vect) 
    

    
    tsfel_feat = {'abs_energy':abs_energy,'autocorr':autocorr,'mean':mean,'median':median,'std':std,'entropy':entropy,
                    'interq_range':interq_range,'mean_abs_dev':mean_abs_dev,'mean_abs_diff':mean_abs_diff,
                    'mean_diff':mean_diff,'median_abs_dev':median_abs_dev,'median_abs_diff':median_abs_diff,
                    'median_diff':median_diff, 'kurtosis':kurtosis,'skewness':skewness,'slope':slope}


    
#         # TSFEL Time
#         cfg_file_time = tsfel.get_features_by_domain('temporal') # If no argument is passed retrieves all available features
#         tsfel_feat_time = tsfel.time_series_features_extractor(cfg_file_time,vect)
    
    # TSFEL frequency
    
    up_sampled_signal = up_sample(rrs, 8)
    vect = up_sampled_signal[index_decalage[j - 5]:index_decalage[j]]
    
    bw = tsfel.feature_extraction.features.power_bandwidth(vect, 8)
    spec_ent = tsfel.feature_extraction.features.spectral_entropy(vect, 8)
    spec_centroid = tsfel.feature_extraction.features.spectral_centroid(vect, 8)
    spec_decr = tsfel.feature_extraction.features.spectral_decrease(vect, 8)
    spec_dist = tsfel.feature_extraction.features.spectral_distance(vect, 8)
    spec_kurt = tsfel.feature_extraction.features.spectral_kurtosis(vect, 8)
    spec_roll_95 = tsfel.feature_extraction.features.spectral_roll_off(vect, 8)
    spec_skew = tsfel.feature_extraction.features.spectral_skewness(vect, 8)
    spec_var = tsfel.feature_extraction.features.spectral_variation(vect, 8)  
    energy =  tsfel.feature_extraction.features.total_energy(vect, 8)
    freq =  tsfel.feature_extraction.features.fundamental_frequency(vect, 8)
    med_freq =  tsfel.feature_extraction.features.median_frequency(vect, 8)
    auc =  tsfel.feature_extraction.features.auc(vect, 8) 
    h_e =  tsfel.feature_extraction.features.human_range_energy(vect, 8) 
    
    

    
    tsfel_feat_spec = {'bw':bw,'spec_ent':spec_ent,'spec_decr':spec_decr,' spec_dist': spec_dist,'spec_kurt':spec_kurt,
                        ' spec_roll_95': spec_roll_95,'spec_skew':spec_skew,'spec_var':spec_var,'spec_centroid':spec_centroid,
                        'energy':energy,'fundamental_freq':freq,'med_freq':med_freq,'auc':auc,'human_energy':h_e}

#         print(tsfel_feat_spec)



    time = []

    for i in range(0, len(rrs[index_decalage[j - 5]:index_decalage[j]])):
        time.append(float(i))

    fdom = frequency_domain(
        rri=rrs[index_decalage[j - 5]:index_decalage[j]],
        time=time,
        fs=8.0,
        method='welch',
        interp_method='linear',
        detrend='constant'
    )

    tps = {'Tps': j - 5}

    output = output.append({**tdom,**tsfel_feat, **nl, **fdom,**tsfel_feat_spec,**tps},
                            ignore_index=True)
#         output = output.append({**tps, **tdom, **nl, **fdom}, ignore_index=True)

    return output


def up_sample(rr_intervals, frequency):
    
    time = calculate_real_time(rr_intervals)

    cs = interp1d(time, rr_intervals)
    xs = np.arange(0, time[-1], 1 /frequency)

    cubic_spline = cs(xs)

    return cubic_spline


def normalize(up_sampled_rrs):
    df_out = pd.DataFrame()

    for i in range(0, len(up_sampled_rrs), 480):
        if i >= 2400:
            # print("Original : ", up_sampled_rrs[i-512:i-502])
            mean = np.mean(up_sampled_rrs[i - 2400:i])
            rr_minus_mean = [abs(x - mean) for x in up_sampled_rrs[i - 2400:i]]
            # ("Array minus mean : ", rr_minus_mean[0:10])
            root_of_squares_sum = math.sqrt(sum(map(lambda x: math.pow(x, 2), rr_minus_mean)))
            rr_div_sqrt = [x / root_of_squares_sum for x in rr_minus_mean]
            # print("Array div by racine des carrés : ", rr_div_sqrt[0:10])

            a8, d8, d7, d6, d5, d4, d3, d2, d1 = pywt.wavedec(rr_div_sqrt, 'db2', level=8)
            lf_norm = sum(map(lambda x: math.pow(x, 2), d3)) + sum(map(lambda x: math.pow(x, 2), d4)) + sum(
                map(lambda x: math.pow(x, 2), d5))
            hf_norm = sum(map(lambda x: math.pow(x, 2), d7)) + sum(map(lambda x: math.pow(x, 2), d6))

            a8, d8, d7, d6, d5, d4, d3, d2, d1 = pywt.wavedec(up_sampled_rrs[i - 2400:i], 'db2', level=8)
            # print(a8, "a8", d8, "d8", d7, "d7", d6, "d6", d5, "d5", d4, "d4", d3, "d3", d2, "d2", d1, "d1")
            lf = sum(map(lambda x: math.pow(x, 2), d3)) + sum(map(lambda x: math.pow(x, 2), d4)) + sum(
                map(lambda x: math.pow(x, 2), d5))
            hf = sum(map(lambda x: math.pow(x, 2), d7)) + sum(map(lambda x: math.pow(x, 2), d6))

#             output = {'Tps': ((i / 8) / 60) - 5, 'hf_WT_norm': hf_norm, 'lf_WT_norm': lf_norm,
#                       'lf/hf_WT_norm': lf_norm / hf_norm, 'hf_WT': hf, 'lf_WT': lf, 'lf/hf_WT': lf / hf}

            
            output = {'Tps': ((i / 8) / 60) - 5, 'hf_WT': hf, 'lf_WT': lf, 'lf/hf_WT': lf / hf}

            df_out = df_out.append(output, ignore_index=True)

    return df_out




def hrv_features(hrv_signal, log=False):

    df_time_features = calc_true_time_domain(hrv_signal, log)

    up_sampled_signal = up_sample(hrv_signal, 8)
    df_frequency_features = normalize(up_sampled_signal)
    
    if log:
        print(hrv_signal)
        print(df_time_features.head())
        print(df_frequency_features.head())

    df_features = df_frequency_features.merge(df_time_features, on='Tps', how='left')
#     print(foo)
#     print(df_features)
    

    return df_features

    
    