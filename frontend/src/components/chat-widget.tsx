'use client'

import { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/auth-context';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ChatMessage {
    id: number;
    message: string;
    is_admin: boolean;
    created_at: string;
}

export default function ChatWidget() {
    const { user } = useAuth();
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [newMessage, setNewMessage] = useState('');
    const [unreadCount, setUnreadCount] = useState(0);
    const [guestId, setGuestId] = useState<string>('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Guest ID 생성 (비로그인 사용자용)
    useEffect(() => {
        if (!user) {
            let storedGuestId = localStorage.getItem('chat_guest_id');
            if (!storedGuestId) {
                storedGuestId = `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
                localStorage.setItem('chat_guest_id', storedGuestId);
            }
            setGuestId(storedGuestId);
        }
    }, [user]);

    // 메시지 폴링 (3초마다)
    useEffect(() => {
        if (isOpen) {
            fetchMessages();
            const interval = setInterval(fetchMessages, 3000);
            return () => clearInterval(interval);
        }
    }, [isOpen, user, guestId]);

    // 자동 스크롤
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const fetchMessages = async () => {
        try {
            let response;
            if (user) {
                response = await axios.get(`${API_URL}/chat/messages`);
            } else if (guestId) {
                response = await axios.get(`${API_URL}/chat/messages/guest/${guestId}`);
            } else {
                return;
            }

            const fetchedMessages = response.data.reverse(); // 오래된 것부터 표시
            setMessages(fetchedMessages);

            // 읽지 않은 메시지 카운트
            const unread = fetchedMessages.filter((m: ChatMessage) => m.is_admin && !isOpen).length;
            setUnreadCount(unread);
        } catch (err) {
            console.error('Failed to fetch messages:', err);
        }
    };

    const sendMessage = async () => {
        if (!newMessage.trim()) return;

        try {
            await axios.post(`${API_URL}/chat/messages`, {
                message: newMessage,
                guest_id: user ? null : guestId
            });

            setNewMessage('');
            fetchMessages();
        } catch (err) {
            console.error('Failed to send message:', err);
            alert('메시지 전송에 실패했습니다.');
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const toggleChat = () => {
        setIsOpen(!isOpen);
        if (!isOpen) {
            setUnreadCount(0);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-50">
            {/* Chat Window */}
            {isOpen && (
                <Card className="mb-4 w-[380px] h-[500px] shadow-2xl border-2 border-blue-500 flex flex-col">
                    <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-lg pb-4">
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-lg">💬 채팅 상담</CardTitle>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={toggleChat}
                                className="text-white hover:bg-white/20"
                            >
                                <X className="w-5 h-5" />
                            </Button>
                        </div>
                        <p className="text-sm text-blue-100 mt-1">
                            {user ? `${user.username}님` : '게스트'}
                        </p>
                    </CardHeader>

                    <CardContent className="flex-1 overflow-y-auto p-4 bg-gray-50">
                        {messages.length === 0 ? (
                            <div className="text-center text-gray-500 mt-8">
                                <MessageCircle className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                                <p>채팅을 시작해보세요!</p>
                                <p className="text-sm mt-1">관리자가 실시간으로 답변드립니다.</p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {messages.map((msg) => (
                                    <div
                                        key={msg.id}
                                        className={`flex ${msg.is_admin ? 'justify-start' : 'justify-end'}`}
                                    >
                                        <div
                                            className={`max-w-[75%] rounded-lg px-4 py-2 ${msg.is_admin
                                                    ? 'bg-white border border-gray-200 text-gray-900'
                                                    : 'bg-blue-600 text-white'
                                                }`}
                                        >
                                            {msg.is_admin && (
                                                <p className="text-xs text-blue-600 font-semibold mb-1">관리자</p>
                                            )}
                                            <p className="text-sm whitespace-pre-wrap">{msg.message}</p>
                                            <p className={`text-xs mt-1 ${msg.is_admin ? 'text-gray-400' : 'text-blue-100'}`}>
                                                {new Date(msg.created_at).toLocaleTimeString('ko-KR', {
                                                    hour: '2-digit',
                                                    minute: '2-digit'
                                                })}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                                <div ref={messagesEndRef} />
                            </div>
                        )}
                    </CardContent>

                    {/* Input Area */}
                    <div className="p-4 border-t bg-white rounded-b-lg">
                        <div className="flex gap-2">
                            <textarea
                                value={newMessage}
                                onChange={(e) => setNewMessage(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="메시지를 입력하세요..."
                                className="flex-1 resize-none border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                rows={2}
                            />
                            <Button
                                onClick={sendMessage}
                                disabled={!newMessage.trim()}
                                className="bg-blue-600 hover:bg-blue-700 self-end"
                            >
                                <Send className="w-4 h-4" />
                            </Button>
                        </div>
                    </div>
                </Card>
            )}

            {/* Floating Button */}
            <Button
                onClick={toggleChat}
                className="relative w-16 h-16 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-2xl"
            >
                {isOpen ? (
                    <X className="w-7 h-7 text-white" />
                ) : (
                    <>
                        <MessageCircle className="w-7 h-7 text-white" />
                        {unreadCount > 0 && (
                            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center animate-pulse">
                                {unreadCount}
                            </span>
                        )}
                    </>
                )}
            </Button>
        </div>
    );
}
