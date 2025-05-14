import streamlit as st
import asyncio
import websockets
import json
import os
import requests
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Workshop IA", page_icon="🤖")
st.title("🤖 Mi primer agente de IA en AWS!")

# Inicializa historial si no existe
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Mostrar historial completo desde session_state
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Escribe tu mensaje..."):
    print(st.session_state.chat_history)
    print()

    # Añadir mensaje del usuario
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    # Añadir mensaje vacío del bot (se irá llenando)
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": ""
    })

    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(user_input)

    # Mostrar mensaje del bot (usando la última entrada del historial)
    bot_container = st.chat_message("assistant")
    response_placeholder = bot_container.empty()

    # Referencia directa a la última entrada (del bot) en el historial
    bot_msg = st.session_state.chat_history[-1]

    # URL de la API Gateway
    BACKEND_URL = os.environ.get("BACKEND_URL")
    
    response = requests.post(BACKEND_URL, json={
        "chat_history": st.session_state.chat_history[:-1],  # Excluye el último mensaje vacío del bot
    })

    # async def stream_response():
    #     async with websockets.connect(WS_URL) as websocket:
    #         await websocket.send(json.dumps({
    #             "action": "sendmessage",
    #             "chat_history": st.session_state.chat_history[:-1],  # Excluye el último mensaje vacío del bot
    #         }))
    #         while True:
    #             try:
    #                 chunk = await websocket.recv()
    #                 bot_msg["content"] += chunk  # actualiza directamente el historial
    #                 response_placeholder.markdown(bot_msg["content"])
    #             except websockets.exceptions.ConnectionClosed:
    #                 break

    # # Ejecutar el stream
    # asyncio.run(stream_response())
    
    
    