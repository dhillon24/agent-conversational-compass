import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { MessageCircle, Send, Bot, User, Activity } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, apiConfig } from '../config/api';

interface Message {
  id: string;
  type: 'user' | 'ai' | 'system';
  content: string;
  timestamp: Date;
  sentiment?: Record<string, number>;
  actions?: string[];
}

interface SystemHealth {
  status: string;
  services?: Record<string, string>;
}

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userId] = useState('demo-user-123');
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    checkSystemHealth();
    // Add welcome message
    setMessages([{
      id: 'welcome',
      type: 'system',
      content: 'Welcome to Customer Service AI! I can help you with payments, questions, and more. Try asking me about invoice payments or refunds.',
      timestamp: new Date()
    }]);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const health = await apiRequest(apiConfig.endpoints.health);
      setSystemHealth(health);
    } catch (error) {
      console.error('Health check failed:', error);
      setSystemHealth({ status: 'unhealthy' });
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setCurrentMessage('');

    try {
      const data = await apiRequest(apiConfig.endpoints.chat, {
        method: 'POST',
        body: JSON.stringify({
          user: userId,
          message: currentMessage,
        }),
      });

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: data.response,
        timestamp: new Date(),
        sentiment: data.sentiment,
        actions: data.actions_taken,
      };

      setMessages(prev => [...prev, aiMessage]);

      if (data.actions_taken?.some((action: string) => action.includes('payment'))) {
        toast({
          title: "Payment Processed",
          description: "Your payment has been initiated successfully.",
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickActions = [
    { label: 'Pay Invoice #123', message: 'I need to pay invoice #123' },
    { label: 'Request Refund', message: 'I need a refund for my recent purchase' },
    { label: 'Account Help', message: 'I need help with my account' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                <Bot className="w-8 h-8 text-blue-600" />
                Customer Service AI
              </h1>
              <p className="text-gray-600 mt-1">AI-powered customer support with payment processing</p>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              <Badge variant={systemHealth?.status === 'healthy' ? 'default' : 'destructive'}>
                {systemHealth?.status || 'checking...'}
              </Badge>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <Card className="h-[600px] flex flex-col">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageCircle className="w-5 h-5" />
                  Live Chat Support
                </CardTitle>
                <CardDescription>
                  Get instant help with payments, refunds, and account questions
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col p-0">
                {/* Messages */}
                <div className="flex-1 p-4 overflow-y-auto space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[80%] ${
                        message.type === 'user' 
                          ? 'bg-blue-600 text-white' 
                          : message.type === 'ai'
                          ? 'bg-gray-100 text-gray-900'
                          : 'bg-yellow-50 text-yellow-800 border border-yellow-200'
                      } rounded-lg p-3`}>
                        <div className="flex items-start gap-2">
                          {message.type === 'user' ? (
                            <User className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          ) : message.type === 'ai' ? (
                            <Bot className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          ) : null}
                          <div className="flex-1">
                            <p className="text-sm">{message.content}</p>
                            {message.sentiment && (
                              <div className="mt-2 text-xs opacity-75">
                                Sentiment: {Object.entries(message.sentiment)
                                  .map(([key, value]) => `${key}: ${(value as number).toFixed(2)}`)
                                  .join(', ')}
                              </div>
                            )}
                            {message.actions && message.actions.length > 0 && (
                              <div className="mt-2">
                                {message.actions.map((action, idx) => (
                                  <Badge key={idx} variant="secondary" className="text-xs mr-1">
                                    {action}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="text-xs opacity-60 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <Bot className="w-4 h-4" />
                          <div className="animate-pulse">AI is thinking...</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Input Area */}
                <div className="p-4 border-t">
                  <div className="flex gap-2">
                    <Textarea
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type your message... (Press Enter to send)"
                      className="flex-1 min-h-[80px] resize-none"
                      disabled={isLoading}
                    />
                    <Button 
                      onClick={sendMessage} 
                      disabled={isLoading || !currentMessage.trim()}
                      className="px-4"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
                <CardDescription>Try these common requests</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {quickActions.map((action, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => setCurrentMessage(action.message)}
                    disabled={isLoading}
                  >
                    {action.label}
                  </Button>
                ))}
              </CardContent>
            </Card>

            {/* System Status */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">System Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Overall</span>
                    <Badge variant={systemHealth?.status === 'healthy' ? 'default' : 'destructive'}>
                      {systemHealth?.status || 'checking...'}
                    </Badge>
                  </div>
                  {systemHealth?.services && Object.entries(systemHealth.services).map(([service, status]) => (
                    <div key={service} className="flex justify-between items-center">
                      <span className="text-sm capitalize">{service}</span>
                      <Badge variant={status === 'healthy' || status === 'connected' ? 'default' : 'secondary'} className="text-xs">
                        {status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* User Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Session Info</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="font-medium">User ID:</span> {userId}
                  </div>
                  <div>
                    <span className="font-medium">Messages:</span> {messages.filter(m => m.type !== 'system').length}
                  </div>
                  <div>
                    <span className="font-medium">Session:</span> Active
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
