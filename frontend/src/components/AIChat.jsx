import React, { useState, useEffect } from 'react';
import { Card } from './ui/card.jsx';
import { Button } from './ui/button.jsx';
import { Input } from './ui/input.jsx';
import { ScrollArea } from './ui/scroll-area.jsx';
import { AlertTriangle, Send } from 'lucide-react';

export function AIChat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm Relief AI, your disaster response assistant. I can help you with safety questions, find nearby resources, and provide emergency guidance. How can I help you today?",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const quickQuestions = [
    "Is my area safe right now?",
    "Where is the nearest shelter?",
    "What should I do in a flood?",
    "How to prepare for evacuation?",
    "Are the roads safe to travel?"
  ];

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: inputMessage
        })
      });

      const data = await res.json();
      const aiMessage = {
        id: messages.length + 2,
        text: data.response || 'Sorry, I could not understand that.',
        sender: 'ai',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('API error:', error);
      setMessages(prev => [...prev, {
        id: messages.length + 2,
        text: "Sorry, something went wrong while fetching the response.",
        sender: 'ai',
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickQuestion = (question) => {
    setInputMessage(question);
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="p-6 pb-24 space-y-6 h-screen flex flex-col">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-2xl">AI Safety Assistant</h1>
        <p>Ask questions about disaster safety</p>
      </div>

      {/* Chat Messages */}
      <Card className="flex-1 p-4">
        <ScrollArea className="h-80">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${
                    message.sender === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                  <p className={`text-xs mt-1 ${
                    message.sender === 'user' 
                      ? 'text-primary-foreground/70' 
                      : 'text-muted-foreground'
                  }`}>
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="text-sm text-muted-foreground">Thinking...</div>
            )}
          </div>
        </ScrollArea>
      </Card>

      {/* Quick Questions */}
      <div className="space-y-3">
        <h3 className="">Quick Questions:</h3>
        <div className="flex flex-wrap gap-2">
          {quickQuestions.map((question, index) => (
            <Button
              key={index}
              variant="outline"
              size="sm"
              onClick={() => handleQuickQuestion(question)}
              className="text-xs h-8"
            >
              {question}
            </Button>
          ))}
        </div>
      </div>

      {/* Message Input */}
      <div className="flex gap-2">
        <Input
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask about safety, shelters, or emergency procedures..."
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          className="flex-1"
          disabled={loading}
        />
        <Button onClick={handleSendMessage} size="icon" disabled={loading}>
          <Send className="h-4 w-4" />
        </Button>
      </div>

      {/* Emergency Disclaimer */}
      <Card className="p-3 bg-yellow-50 border-yellow-200">
        <div className="flex items-start gap-2">
          <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-yellow-800">
            <strong>Important:</strong> This AI assistant provides general guidance only. 
            In life-threatening emergencies, call 911 or Disaster Team immediately.
          </p>
        </div>
      </Card>
    </div>
  );
}
