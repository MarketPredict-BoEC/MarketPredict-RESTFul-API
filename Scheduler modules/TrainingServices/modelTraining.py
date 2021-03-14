from datetime import datetime
from dataProvidingServices.dataProviding import prepairDataForLoad
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, LSTM, LSTM, BatchNormalization, concatenate
from tensorflow.keras.layers import Dense, Input, Dropout, LSTM, Activation, Embedding, Conv1D, MaxPooling1D, Flatten, \
    GlobalMaxPooling1D

Training = True


def train_model(category, pair):
    two_years_ago = 63072000
    endDate = int(datetime.utcnow().timestamp())
    startDate = endDate - two_years_ago
    train_x, train_y, train_news_x, dates = prepairDataForLoad(category,
                                                               pair, startDate, endDate, Training=True)

    # trade data RNN

    dim = train_x.shape[1]  # 7 delay window

    # define our RNN network for technical indicator feature extraction
    marketModel = Sequential()
    marketModel.add(LSTM(128, input_shape=(train_x.shape[1:])))
    marketModel.add(Dropout(0.2))
    # marketModel.add(Activation("relu"))

    # In[16]:

    from tensorflow.keras.regularizers import l2

    # news data recurrent convolution network
    inputShape = (train_news_x.shape[1], train_news_x.shape[2])
    inputs = Input(shape=inputShape)
    x = Conv1D(filters=64, kernel_size=3,
               activation='relu', padding='same',
               input_shape=inputShape, kernel_regularizer=l2(15e-3))(inputs)  # kernel_regularizer =l2(5e-2)
    x = MaxPooling1D(pool_size=2)(x)
    x = Dropout(0.2)(x)
    # x = Activation("relu")(x)
    x = LSTM(128)(x)  # , kernel_regularizer =l2(5e-2),recurrent_regularizer=l2(5e-2))
    BoEC_RCNN = Model(inputs, x)

    # In[17]:

    # concatenate news and market output

    combinedInput = concatenate([marketModel.output, BoEC_RCNN.output])
    # x = Dense(2, activation="softmax")(combinedInput)

    x = Dense(1,  kernel_regularizer=l2(15e-3) )(combinedInput)

    model = Model(inputs=[marketModel.input, BoEC_RCNN.input], outputs=x)

    # In[18]:

    from tensorflow.keras.optimizers import Adam
    opt = tf.keras.optimizers.Adam(lr=0.001, decay=1e-6)

    model.compile(
        loss=tf.keras.losses.MeanAbsolutePercentageError(),
        optimizer=opt

    )
    '''
    model.compile(loss="binary_crossentropy",
                  optimizer='Adam',
                  metrics=['accuracy'])
    '''

    model.summary()

    # In[19]:

    # train the model
    callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=5)
    history = model.fit(
        [train_x, train_news_x], train_y,
        epochs=60, batch_size=32)

    modelName = pair.upper() + 'WithNewsHourly.h5'
    model.save(modelName)
