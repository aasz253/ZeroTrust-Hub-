import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, MessageSquare, Trash2 } from 'lucide-react';
import { ai } from '../services/api';
import type { Message, Conversation } from '../types';

export default function AIAssistant() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConv, setActiveConv] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    ai.conversations().then(setConversations).catch(console.error);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadConversation = async (id: number) => {
    setActiveConv(id);
    const msgs = await ai.messages(id);
    setMessages(msgs);
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const msg = input;
    setInput('');

    const tempMsg: Message = { id: Date.now(), role: 'user', content: msg, created_at: new Date().toISOString() };
    setMessages((prev) => [...prev, tempMsg]);
    setLoading(true);

    try {
      const result = await ai.chat({ message: msg, conversation_id: activeConv || undefined });
      setActiveConv(result.conversation_id);
      const convs = await ai.conversations();
      setConversations(convs);
      const msgs = await ai.messages(result.conversation_id);
      setMessages(msgs);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), role: 'assistant', content: 'Sorry, an error occurred. Please try again.', created_at: new Date().toISOString() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const newChat = () => {
    setActiveConv(null);
    setMessages([]);
  };

  return (
    <div className="flex gap-6 h-[calc(100vh-8rem)]">
      <div className="w-72 flex-shrink-0 glass p-4 overflow-y-auto scrollbar-thin">
        <button onClick={newChat} className="w-full btn-primary text-sm mb-4 flex items-center justify-center gap-2">
          <MessageSquare className="w-4 h-4" /> New Chat
        </button>
        <div className="space-y-2">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => loadConversation(conv.id)}
              className={`w-full text-left p-3 rounded-xl text-sm transition-colors ${
                activeConv === conv.id ? 'bg-cyber-accent/10 border border-cyber-accent/20' : 'hover:bg-gray-800/50'
              }`}
            >
              <p className="text-gray-300 truncate">{conv.title || 'New conversation'}</p>
              <p className="text-xs text-gray-600 mt-1">{new Date(conv.created_at).toLocaleDateString()}</p>
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col glass">
        <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Bot className="w-16 h-16 text-cyber-accent/30 mb-4" />
              <h2 className="text-xl font-semibold text-white mb-2">ZeroTrust AI Assistant</h2>
              <p className="text-gray-500 max-w-md">
                Ask me about vulnerabilities, CVEs, security best practices, incident response, or secure coding.
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-lg bg-cyber-accent/10 border border-cyber-accent/20 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-cyber-accent" />
                </div>
              )}
              <div className={`max-w-[80%] p-4 rounded-2xl ${
                msg.role === 'user'
                  ? 'bg-cyber-accent/10 border border-cyber-accent/20 text-gray-200'
                  : 'bg-gray-800/50 text-gray-300'
              }`}>
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-cyber-secondary/10 border border-cyber-secondary/20 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-cyber-secondary" />
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t border-gray-800/50">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask anything about cybersecurity..."
              className="input-field flex-1"
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="btn-primary disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
