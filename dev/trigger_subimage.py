import numpy as np
import cygno as cy

def gaussian_convergence(data, threshold = 5, attempts = 5):
    data_conv = data.copy()
    convergence = 0
    for k in range(attempts):
        mean = np.mean(data_conv)
        std = np.std(data_conv)
        
        bool_test1 = data_conv > (mean + threshold*std)
        bool_test2 = data_conv < (mean - threshold*std)
        
        bool_test = bool_test1 + bool_test2
        
        if any(bool_test):
            data_conv = data_conv[~bool_test]
        else:
            #convergence = True
            break
        convergence += 1
    return data_conv, convergence

def find_stdArray(img_arr, divisions, overlap = 30):
    
    n_evs = np.shape(img_arr)[0]
    size = np.shape(img_arr)[1]
    div_size = size/divisions
    
    std_arr = np.zeros([n_evs, divisions[0]*divisions[1]], dtype = float)
    
    for ev in range(n_evs):
        img = img_arr[ev]

        x, y = np.meshgrid(np.arange(divisions[0]), np.arange(divisions[1]))

        #print("Image: %.3f \u00B1 %.3f" %(np.mean(img.flatten()), np.std(img.flatten())))
        for k in range(divisions[0]*divisions[1]):
            xx = x.flatten()[k]
            yy = y.flatten()[k]

            x_begin = int(xx*div_size[0])
            x_end = int((xx+1)*div_size[0])

            y_begin = int(yy*div_size[1])
            y_end = int((yy+1)*div_size[1])

            x_begin = x_begin - (overlap if x_begin != 0 else 0)
            x_end = x_end + (overlap if x_end != 2304 else 0)

            y_begin = y_begin - (overlap if y_begin != 0 else 0)
            y_end = y_end + (overlap if y_end != 2304 else 0)


            img_div = img[x_begin:x_end, y_begin:y_end].flatten()  
            std_arr[ev,k] = np.std(img_div)

    return std_arr

def find_threshold(std_arr, threshold = 5):
    
    div = np.shape(std_arr)[1]
    threshold_arr = np.zeros(div, dtype = float)
    
    for k in range(div):
        hist_arr_plot = std_arr[:,k]
        data_conv, convergence = gaussian_convergence(hist_arr_plot)
        mu = np.mean(data_conv)
        sigma = np.std(data_conv)

        threshold_arr[k] = mu+(threshold*sigma)

    return threshold_arr

def trigger(std_arr, threshold):
    
    trigger_arr = std_arr > threshold
    if trigger_arr.any():
        return 1
    else:
        return 0