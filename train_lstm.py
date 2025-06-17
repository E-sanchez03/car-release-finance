import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import classification_report, confusion_matrix
from data_pipeline import get_prepared_data

# Función para crear secuencias para la LSTM
def create_sequences(X, y, time_steps=30):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        v = X.iloc[i:(i + time_steps)].values
        Xs.append(v)
        ys.append(y.iloc[i + time_steps])
    return np.array(Xs), np.array(ys)

# 1. Cargar y preparar los datos
X_train_df, X_test_df, y_train, y_test = get_prepared_data()
TIME_STEPS = 30 # Usaremos los últimos 30 días para predecir el siguiente

X_train_seq, y_train_seq = create_sequences(X_train_df, y_train, TIME_STEPS)
X_test_seq, y_test_seq = create_sequences(X_test_df, y_test, TIME_STEPS)

print(f"\nForma de los datos de entrenamiento para LSTM: {X_train_seq.shape}")

# 2. Construir y compilar el modelo LSTM
print("\nConstruyendo modelo LSTM...")
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train_seq.shape[1], X_train_seq.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(units=50))
model.add(Dropout(0.2))
model.add(Dense(units=1, activation='sigmoid'))

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

# 3. Entrenar el modelo
print("\nEntrenando modelo LSTM...")
history = model.fit(
    X_train_seq, y_train_seq,
    epochs=20,
    batch_size=32,
    validation_split=0.1,
    verbose=1
)
print("Entrenamiento completado.")

# 4. Evaluar el modelo
print("\n--- Evaluación del Modelo LSTM ---")
y_pred_prob = model.predict(X_test_seq)
y_pred = (y_pred_prob > 0.5).astype(int)
print(classification_report(y_test_seq, y_pred))
print("Matriz de Confusión:")
print(confusion_matrix(y_test_seq, y_pred))