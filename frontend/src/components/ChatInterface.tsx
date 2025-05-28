import React, { useState, useRef } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [userId, setUserId] = useState('customer123');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      user: userId,
      message: currentMessage,
      timestamp: new Date().toISOString(),
      type: 'user',
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user: userId,
          message: currentMessage,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to get response: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      const aiMessage = {
        id: Date.now() + 1,
        user: 'AI Assistant',
        message: data.response,
        timestamp: new Date().toISOString(),
        type: 'ai',
        sentiment: data.sentiment,
        actions: data.actions_taken,
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        user: 'System',
        message: `Error: Failed to send message, please try again. (${error instanceof Error ? error.message : 'Unknown error'})`,
        timestamp: new Date().toISOString(),
        type: 'error',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setCurrentMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const testPaymentMessage = () => {
    setCurrentMessage('I need to pay invoice #123');
  };

  const testRefundMessage = () => {
    setCurrentMessage('I need a refund for my recent purchase');
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h3>Customer Service Chat</h3>
        <div className="user-selector">
          <label>User ID:</label>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Enter user ID"
          />
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.type}`}>
            <div className="message-header">
              <span className="message-user">{msg.user}</span>
              <span className="message-time">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <div className="message-content">{msg.message}</div>
            {msg.sentiment && (
              <div className="message-sentiment">
                Sentiment: {Object.entries(msg.sentiment).map(([key, value]) => (
                  <span key={key} className={`sentiment-${key}`}>
                    {key}: {(value as number).toFixed(2)}
                  </span>
                ))}
              </div>
            )}
            {msg.actions && msg.actions.length > 0 && (
              <div className="message-actions">
                Actions: {msg.actions.join(', ')}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="message ai loading">
            <div className="message-content">AI is thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <div className="quick-actions">
          <button onClick={testPaymentMessage}>Test Payment</button>
          <button onClick={testRefundMessage}>Test Refund</button>
        </div>
        <div className="input-area">
          <textarea
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <button onClick={sendMessage} disabled={isLoading || !currentMessage.trim()}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
