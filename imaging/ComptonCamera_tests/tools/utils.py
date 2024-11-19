import cupy as cp

def remove_nans(cp_array):
    n_nans = cp.isnan(cp_array).sum()
    print(n_nans, 'NaNs in cp_array')
    if n_nans:
        print('Rows with Nans:\n', cp_array[cp.isnan(cp_array).any(axis=1)])
        print(cp_array.shape, 'shape before removing NaNs')
        cp_array = cp_array[~cp.isnan(cp_array).any(axis=1)]
        print(cp_array.shape, 'shape after removing NaNs')
    return cp_array
