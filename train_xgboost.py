import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix
from data_pipeline import get_prepared_data

# 1. Cargar y preparar los datos
X_train, X_test, y_train, y_test = get_prepared_data()

# 2. Inicializar y entrenar el modelo XGBoost
print("\nEntrenando modelo XGBoost...")
model = xgb.XGBClassifier(
    objective='binary:logistic',
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    use_label_encoder=False,
    eval_metric='logloss'
)
model.fit(X_train, y_train)
print("Entrenamiento completado.")

# 3. Evaluar el modelo
print("\n--- Evaluación del Modelo XGBoost ---")
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
print("Matriz de Confusión:")
print(confusion_matrix(y_test, y_pred))