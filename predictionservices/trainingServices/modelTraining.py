from datetime import datetime
from dataProvidingServices.dataProviding import prepairDataForLoad
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import concatenate
from tensorflow.keras.layers import Dense, Input, Dropout, LSTM, Conv1D, MaxPooling1D
from tensorflow.keras.regularizers import l2
from matplotlib import pyplot as plt
import errors
import pathlib
Training = True
from tensorflow.keras.callbacks import EarlyStopping


def train_model(category, pair, newsKeywords,
                provider=['fxstreet'], concept_number=210,
                resolution=60, SEQ_LEN_news=7,
                SEQ_LEN=7, max_L=15, conceptsType='pair'
                , epoch=60, learningRate=0.001, decay=1e-6, batch_size=32):
    try:
        print('-------------Start Model Training for currency pair {a} with news keywords {b}--------------------------'.format(a = pair,b=newsKeywords))
        endDate =int( datetime.utcnow().timestamp())
        threeYearsTS = 94867200
        twoYearsTS = 63072000
        startDate = endDate - twoYearsTS
        train_x, train_y, train_news_x, dates = prepairDataForLoad(category,
                                                                   pair, startDate, endDate,
                                                                   newsKeywords, provider=provider,
                                                                   concept_number=concept_number, resolution=resolution,
                                                                   SEQ_LEN_news=SEQ_LEN_news, SEQ_LEN=SEQ_LEN,
                                                                   max_L=max_L, Training=True
                                                                   , conceptsType=conceptsType)

        # trade data RNN

        dim = train_x.shape[1]  # 7 delay window

        # define our RNN network for technical indicator feature extraction
        marketModel = Sequential()
        marketModel.add(LSTM(128, input_shape=(train_x.shape[1:])))
        marketModel.add(Dropout(0.2))

        inputShape = (train_news_x.shape[1], train_news_x.shape[2])
        inputs = Input(shape=inputShape)
        x = Conv1D(filters=64, kernel_size=3,
                   activation='relu', padding='same',
                   input_shape=inputShape)(inputs) #, kernel_regularizer=l2(15e-3)) # kernel_regularizer =l2(5e-2)
        x = MaxPooling1D(pool_size=2)(x)
        x = Dropout(0.2)(x)
        # x = Activation("relu")(x)
        x = LSTM(128)(x)  # , kernel_regularizer =l2(5e-2),recurrent_regularizer=l2(5e-2))
        BoEC_RCNN = Model(inputs, x)

        # concatenate news and market output

        combinedInput = concatenate([marketModel.output, BoEC_RCNN.output])
        # x = Dense(2, activation="softmax")(combinedInput)

        #x = Dense(1, activation='sigmoid', kernel_regularizer=l2(15e-3), )(combinedInput)
        x = Dense(1, kernel_regularizer=l2(15e-3) )(combinedInput)

        model = Model(inputs=[marketModel.input, BoEC_RCNN.input], outputs=x)

        opt = tf.keras.optimizers.Adam(lr=learningRate, decay=decay)

        model.compile(
            loss=tf.keras.losses.MeanAbsolutePercentageError(),
            optimizer=opt

        )

        model.summary()
        callback = EarlyStopping(monitor='val_loss', patience=30 , min_delta=0.00001,)
        history = model.fit(
            [train_x, train_news_x], train_y,
            epochs=epoch, batch_size=batch_size,
            validation_split=0.2,callbacks=[callback])
        plot_loss(history)
        plt.show()
        modelName = pair.upper() + 'WithNewsHourly.h5'
        current_Path = pathlib.Path().absolute()
        filePath = str(current_Path)+'/outputFiles/' + category + '/' + pair + '/' + modelName
        model.save(filePath)
        print('-------------successfully completed!--------------------------')
    except errors.DataProvidingException as err:
        print(err.message)
        return False
    except:
        print("Something Went Wrong!")
        return False



def plot_loss(history):
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    # plt.ylim([0, 10])
    plt.xlabel('Epoch')
    plt.ylabel('Loss [Close]')
    plt.legend()
    plt.grid(True)


def main():

    train_model(category='Forex', pair='USDJPY', newsKeywords='USDJPY',
                provider=['fxstreet'], concept_number=210,
                resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                epoch=150,learningRate=0.001,decay=1e-6,batch_size=32)
    return


if __name__ == "__main__":
    main()
