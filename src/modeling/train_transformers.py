import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from sklearn.metrics import classification_report, confusion_matrix
from src.data_pipeline import get_prepared_data
from train_lstm import create_sequences # Reutilizamos la función de secuencias

# Bloque de Transformer
def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):
    # Attention and Normalization
    x = layers.MultiHeadAttention(key_dim=head_size, num_heads=num_heads, dropout=dropout)(inputs, inputs)
    x = layers.Dropout(dropout)(x)
    x = layers.LayerNormalization(epsilon=1e-6)(x + inputs)
    # Feed Forward Part
    ff_out = layers.Conv1D(filters=ff_dim, kernel_size=1, activation="relu")(x)
    ff_out = layers.Dropout(dropout)(ff_out)
    ff_out = layers.Conv1D(filters=inputs.shape[-1], kernel_size=1)(ff_out)
    return layers.LayerNormalization(epsilon=1e-6)(x + ff_out)

def build_transformer_model(input_shape, head_size, num_heads, ff_dim, num_transformer_blocks, mlp_units, dropout=0, mlp_dropout=0):
    inputs = tf.keras.Input(shape=input_shape)
    x = inputs
    for _ in range(num_transformer_blocks):
        x = transformer_encoder(x, head_size, num_heads, ff_dim, dropout)
    
    x = layers.GlobalAveragePooling1D(data_format="channels_first")(x)
    for dim in mlp_units:
        x = layers.Dense(dim, activation="relu")(x)
        x = layers.Dropout(mlp_dropout)(x)
    
    outputs = layers.Dense(1, activation="sigmoid")(x)
    return tf.keras.Model(inputs, outputs)

# 1. Cargar y preparar los datos
X_train_df, X_test_df, y_train, y_test = get_prepared_data()
TIME_STEPS = 60 # Los transformers pueden manejar secuencias más largas

X_train_seq, y_train_seq = create_sequences(X_train_df, y_train, TIME_STEPS)
X_test_seq, y_test_seq = create_sequences(X_test_df, y_test, TIME_STEPS)

# 2. Construir y compilar el modelo Transformer
print("\nConstruyendo modelo Transformer...")
model = build_transformer_model(
    input_shape=(X_train_seq.shape[1], X_train_seq.shape[2]),
    head_size=256,
    num_heads=4,
    ff_dim=4,
    num_transformer_blocks=4,
    mlp_units=[128],
    mlp_dropout=0.4,
    dropout=0.25,
)

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

# 3. Entrenar el modelo
print("\nEntrenando modelo Transformer...")
history = model.fit(
    X_train_seq, y_train_seq,
    epochs=40,
    batch_size=32,
    validation_split=0.1,
    verbose=1
)
print("Entrenamiento completado.")

# 4. Evaluar el modelo
print("\n--- Evaluación del Modelo Transformer ---")
y_pred_prob = model.predict(X_test_seq)
y_pred = (y_pred_prob > 0.5).astype(int)
print(classification_report(y_test_seq, y_pred))
print("Matriz de Confusión:")
print(confusion_matrix(y_test_seq, y_pred))