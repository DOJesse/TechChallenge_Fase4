# %%
!pip install sklearn
# %%
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, TensorDataset    
import mlflow
import mlflow.pytorch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error

# %%
# Set device configuration - check if is there a gpu
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

# %%
# list of hyperparameters
input_size = 1      # Number of features in the input data
hidden_size = 50     # Number of hidden units in the LSTM
num_layers = 2       # Number of LSTM layers
output_size = 1      # Number of output units (e.g., regression output)
num_epochs = 50
batch_size = 64
learning_rate = 0.001
sequence_length = 20  # Length of the input sequences
# %%
# get data
# Carregar os dados
data = pd.read_csv('../downloadData/data/PETR4.SA_data.csv')
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

# Ajustar as colunas relacionadas à moeda para duas casas decimais
for col in ['Close', 'High', 'Low', 'Open']:
    data[col] = data[col].round(2)

# Garantir que a coluna Volume seja tratada como número inteiro
data['Volume'] = data['Volume'].astype(int)

# Selecionar a coluna de fechamento ajustado
prices = data['Close'].values.reshape(-1, 1)

# %% 
# Normalizar os dados
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_prices = scaler.fit_transform(prices)

# %%
# Criar sequências para o modelo LSTM
def create_sequences(data, sequence_length):
    sequences = []
    labels = []
    for i in range(len(data) - sequence_length):
        sequences.append(data[i:i + sequence_length])
        labels.append(data[i + sequence_length])
    return np.array(sequences), np.array(labels)

sequence_length = 60
X, y = create_sequences(scaled_prices, sequence_length)

# Dividir os dados em conjuntos de treinamento e validação
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# %%
class LSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.rnn = nn.LSTM(input_size=input_size, hidden_size=128, num_layers=2, batch_first=True)
        self.output_layer = nn.Linear(128, 1)

    def forward(self, x):
        x, _ = self.rnn(x) # assume x is (batch_size, sequence_length, input_size)
        x = x[:, -1, :] # get the last time step output
        x = self.output_layer(x)
        return x
    
# %%
# Convertendo para tensores
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32)

# Dataset & DataLoader
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
test_dataset = TensorDataset(X_test_tensor, y_test_tensor)
train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False)


# %%
# Modelo, Loss e Optimizer
model = LSTM()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# %%
# Treinamento
def train_model():
    mlflow.set_experiment("Treinamento de Modelo LSTM")
    with mlflow.start_run():
        # Log model parameters
        mlflow.log_param("input_size", input_size)
        mlflow.log_param("hidden_size", hidden_size)
        mlflow.log_param("num_layers", num_layers)
        mlflow.log_param("output_size", output_size)
        mlflow.log_param("num_epochs", num_epochs)
        mlflow.log_param("batch_size", batch_size)
        mlflow.log_param("learning_rate", learning_rate)

        for epoch in range(num_epochs):
            model.train()
            running_loss = 0.0
            
            for i, (inputs, labels) in enumerate(train_loader):
                #inputs = inputs.squeeze(1).permute(0, 2, 1) # rearrange to (batch_size, 28, 28)
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()
                
                # forward pass
                outputs = model(inputs)
                loss = criterion(outputs, labels)

                # backward pass and optimization
                loss.backward()
                optimizer.step()

                running_loss += loss.item()

                # Log metrics every 100 batches
                if i % 100 == 0:
                    print(f"Epoch [{epoch+1}/{num_epochs}], Step [{i+1}/{len(train_loader)}], Loss: {loss.item():.4f}")
                    mlflow.log_metric("train_loss", running_loss / (i+1), step=epoch * len(train_loader) + i)

        # Save the model
        mlflow.pytorch.log_model(model, "lstm_artificial_data_model")

        return model

def evaluate_model(model, criterion):
    model.eval()
    predictions = []
    actuals = []

    test_loss = 0.0
    with torch.no_grad():
        for sequences, labels in test_loader:
            sequences, labels = sequences.to(device), labels.to(device)
            outputs = model(sequences)
            predictions.extend(outputs.cpu().numpy())
            actuals.extend(labels.cpu().numpy())

            loss = criterion(outputs, labels)
            test_loss += loss.item()

    # As saídas ainda estão normalizadas (de 0 a 1), então precisamos inverter a escala
    predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
    actuals = scaler.inverse_transform(np.array(actuals).reshape(-1, 1)).flatten()

    mae = mean_absolute_error(actuals, predictions)
    rmse = np.sqrt(mean_squared_error(actuals, predictions))
    mape = mean_absolute_percentage_error(actuals, predictions)

    average_test_loss = test_loss / len(test_loader)
    print(f"Test Loss: {average_test_loss:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAPE: {mape:.4f}")

    mlflow.log_metric("test_loss", average_test_loss)
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("mape", mape)

    return predictions, actuals

# %%
# Run the training and evaluation
model = train_model()
# Evaluate the model
predictions, actuals = evaluate_model(model, criterion)

# %%
# Como os primeiros 'sequence_length' valores não têm previsão,
# vamos criar um eixo de tempo compatível
plt.figure(figsize=(14, 6))
plt.plot(actuals, label="Real", color='blue')
plt.plot(predictions, label="Previsto", color='orange')
plt.title("Previsão de Preços de Ações com LSTM - Real vs Previsto")
plt.xlabel("Tempo")
plt.ylabel("Preço")
plt.legend()
plt.grid(True)
plt.show()