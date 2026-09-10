import h5py
f = h5py.File('models/cnnCat2.h5', 'r')
print(f.attrs.get('model_config'))
