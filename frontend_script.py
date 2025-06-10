import streamlit as st
import asyncio
import json
import os
import requests
import time
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Workshop IA", page_icon="🤖")
st.title("🤖 Mi primer agente de IA en AWS!")

if BACKEND_URL := st.text_input("Ingresa el link de la API que desplegamos previamente! :D"):
    # Inicializa historial si no existe
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Mostrar historial completo desde session_state
    for msg in st.session_state.chat_history:
        if msg["role"] == "user" and type(msg["content"]) != type('string') and msg["content"][0]["type"] == "tool_result":
            continue
        with st.chat_message(msg["role"]):
            try:
                for m in msg["content"]:
                    if m["type"] == "text":
                        st.markdown(m["text"])
                    elif m["type"] == "tool_use":
                        st.markdown(f"```Executing tool: {m['name']}...```")
            except:
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
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(user_input)

        execute_again = True
        while execute_again:
            execute_again = False
            # Añadir mensaje vacío del bot (se irá llenando)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": ""
            })

            # Mostrar mensaje del bot (usando la última entrada del historial)
            bot_container = st.chat_message("assistant")
            response_placeholder = bot_container.empty()

            # Referencia directa a la última entrada (del bot) en el historial
            bot_msg = st.session_state.chat_history[-1]
            
            response = requests.post(BACKEND_URL + "/converse", json={
                "chat_history": st.session_state.chat_history[:-1],  # Excluye el último mensaje vacío del bot
            })
            response = response.json()
            print(response)
            for ia_message in response["body"]["content"]:
                if ia_message["type"] == "text":
                    for chunk in ia_message["text"].split():
                        bot_msg["content"] += chunk + " "
                        response_placeholder.markdown(bot_msg["content"])
                        time.sleep(0.05)
                elif ia_message["type"] == "tool_use":
                    bot_msg["content"] += f"\n\n```Executing tool: {ia_message['name']}...```"
                    response_placeholder.markdown(bot_msg["content"])
                    st.session_state.chat_history[-1] = {
                        "role": "assistant",
                        "content": response["body"]["content"]
                    }
                    
                    ## Ejecutar la herramienta correspondiente
                    tool_response = requests.post(BACKEND_URL + "/tool", json={
                        "tool_name": ia_message["name"],
                        "tool_input": ia_message["input"],
                    })
                    
                    pprint(tool_response.json())
                    
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": ia_message["id"],
                                "content": tool_response.json()["result"]
                            }
                        ]
                    })
                    
                    execute_again = True
                
    
    
    