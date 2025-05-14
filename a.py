import requests

response = requests.post('http://127.0.0.1:3000/converse', json = {
    "chat_history": [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How can I assist you today?"},
        {"role": "user", "content": "I'm looking for information about a specific topic."}
    ]
})

print(response)