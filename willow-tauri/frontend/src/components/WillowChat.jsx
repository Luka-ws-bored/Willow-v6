import React, { useState, useRef, useEffect } from "react";
import styles from "./WillowChat.module.css";

const WillowChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  const addMessage = (text, isUser = false) => {
    setMessages((prev) => [...prev, { text, isUser }]);
  };

  const sendMessageToBackend = async (message) => {
    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      const data = await response.json();
      addMessage(data.response);
    } catch (err) {
      addMessage("Error: Backend not responding");
    }
  };

  const handleSend = () => {
    if (!input.trim()) return;
    addMessage(input, true);
    const userMessage = input;
    setInput("");
    sendMessageToBackend(userMessage);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSend();
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className={styles.chatContainer}>
      <div className={styles.messages}>
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`${styles.message} ${msg.isUser ? styles.user : ""}`}
          >
            {msg.text}
          </div>
        ))}
        <div ref={messagesEndRef}></div>
      </div>
      <div className={styles.inputContainer}>
        <input
          type="text"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default WillowChat;
