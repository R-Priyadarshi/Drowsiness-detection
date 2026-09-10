from keras.models import load_model
try:
    model = load_model('models/cnnCat2.h5')
    print("Model loaded successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()
