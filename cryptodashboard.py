import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# Función para obtener los datos históricos
def obtener_datos_historicos(cripto, dias):
    url = f"https://api.coingecko.com/api/v3/coins/{cripto}/market_chart?vs_currency=usd&days={dias}&interval=daily"
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()  # Lanza una excepción si hay un error en la respuesta
        datos = respuesta.json()
        precios = datos['prices']
        df = pd.DataFrame(precios, columns=["timestamp", "price"])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener los datos de {cripto}: {e}")
        return None

# Calcular el promedio móvil
def calcular_promedio_movil(df, ventana=14):
    df['SMA'] = df['price'].rolling(window=ventana).mean()

# Calcular el RSI (Índice de Fuerza Relativa)
def calcular_rsi(df, ventana=14):
    delta = df['price'].diff(1)
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)
    media_ganancia = ganancia.rolling(window=ventana).mean()
    media_perdida = perdida.rolling(window=ventana).mean()
    rs = media_ganancia / media_perdida
    df['RSI'] = 100 - (100 / (1 + rs))

# Graficar con Plotly
def graficar(df, cripto):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['price'], mode='lines', name=f'Precio de {cripto}', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['SMA'], mode='lines', name='Promedio Móvil', line=dict(color='red')))
    fig.update_layout(
        title=f'Precio de {cripto} y Promedio Móvil',
        xaxis_title='Fecha',
        yaxis_title='Precio en USD',
        xaxis=dict(tickformat="%Y-%m-%d", rangeslider=dict(visible=True)),
        template="plotly_dark"
    )
    st.plotly_chart(fig)

# Función principal del dashboard
def main():
    # Título del dashboard
    st.title("Dashboard de Criptomonedas")

    # Selector de criptomoneda y número de días
    cripto = st.selectbox('Selecciona una criptomoneda', ['bitcoin', 'ethereum', 'dogecoin', 'litecoin', 'ripple'])
    dias = st.slider('Selecciona el número de días', min_value=7, max_value=365, value=30)

    # Obtener los datos históricos de la criptomoneda seleccionada
    df = obtener_datos_historicos(cripto, dias)
    
    if df is not None:
        # Calcular indicadores
        calcular_promedio_movil(df)
        calcular_rsi(df)

        # Mostrar la tabla con los datos
        st.subheader('Datos Históricos')
        st.write(df.tail())

        # Graficar los resultados
        graficar(df, cripto)

        # Mostrar el último valor de RSI
        st.subheader('Índice de Fuerza Relativa (RSI)')
        st.write(f"El último RSI de {cripto} es: {df['RSI'].iloc[-1]:.2f}")

        # Mostrar el precio actual
        st.subheader('Precio Actual')
        st.write(f"El precio actual de {cripto} es: ${df['price'].iloc[-1]:.2f}")

if __name__ == "__main__":
    main()
