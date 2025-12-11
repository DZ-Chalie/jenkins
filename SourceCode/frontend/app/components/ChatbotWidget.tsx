"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";
import styles from "./ChatbotWidget.module.css";

type Drink = {
    name: string;
    image_url: string;
    description: string;
    abv: string;
    volume: string;
};

type Message = {
    id: number;
    text: string;
    sender: "user" | "bot";
    drinks?: Drink[];
};

export default function ChatbotWidget() {
    const [isOpen, setIsOpen] = useState(true); // Default to open
    const [messages, setMessages] = useState<Message[]>([
        { id: 1, text: " 🍶\n무엇을 드릴까유?", sender: "bot" }
    ]);
    const suggestions = [
        "오늘의 전통주 추천해줘",
        "인기 있는 술은 뭐야?",
        "전통주 칵테일 레시피",
        "오늘 날씨에 맞는 술 추천해줘"
    ];
    const [inputText, setInputText] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen, isLoading]);

    const handleSendMessage = async (text: string = inputText) => {
        if (!text.trim()) return;

        const userMsg: Message = { id: Date.now(), text: text, sender: "user" };
        setMessages((prev) => [...prev, userMsg]);
        setInputText("");
        setIsLoading(true);

        try {
            const response = await fetch('/api/python/chatbot/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text }),
            });

            if (response.ok) {
                const data = await response.json();
                const botMsg: Message = {
                    id: Date.now() + 1,
                    text: data.answer,
                    sender: "bot",
                    drinks: data.drinks
                };
                setMessages((prev) => [...prev, botMsg]);
            } else {
                throw new Error("Failed to get response");
            }
        } catch (error) {
            const errorMsg: Message = {
                id: Date.now() + 1,
                text: "아이고, 머리가 아파서 잠시 생각을 못하겠구만유. 다시 물어봐주시오.",
                sender: "bot"
            };
            setMessages((prev) => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter") {
            handleSendMessage();
        }
    };

    const handleSuggestionClick = (suggestion: string) => {
        handleSendMessage(suggestion);
    };

    return (
        <>
            <div className={styles.container}>
                {!isOpen && (
                    <button className={styles.button} onClick={() => setIsOpen(true)}>
                        <Image
                            src="/이리오너라.png"
                            alt="이리오너라"
                            width={36}
                            height={36}
                            style={{ borderRadius: '50%', marginRight: '8px' }}
                        />
                        <span>이리오너라~</span>
                    </button>
                )}
            </div>

            {isOpen && (
                <div className={styles.modalOverlay} onClick={() => setIsOpen(false)}>
                    <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
                        <div className={styles.header}>
                            <div className={styles.headerTitle}>
                                <span>🍶</span>
                                <h2>주모 (Jumo)</h2>
                            </div>
                            <button className={styles.closeButton} onClick={() => setIsOpen(false)}>
                                ×
                            </button>
                        </div>

                        <div className={styles.content}>
                            {messages.map((msg) => (
                                <div
                                    key={msg.id}
                                    style={{
                                        display: 'flex',
                                        gap: '0.5rem',
                                        alignItems: 'flex-end',
                                        justifyContent: msg.sender === "bot" ? 'flex-start' : 'flex-end'
                                    }}
                                >
                                    {msg.sender === "bot" && (
                                        <div className={styles.avatar}>🍶</div>
                                    )}
                                    <div
                                        style={{
                                            maxWidth: '70%',
                                            padding: '0.8rem 1rem',
                                            borderRadius: '18px',
                                            fontSize: '0.95rem',
                                            lineHeight: '1.4',
                                            position: 'relative',
                                            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
                                            backgroundColor: msg.sender === "bot" ? '#fff' : '#8b4513',
                                            color: msg.sender === "bot" ? '#333' : '#fff',
                                            borderBottomLeftRadius: msg.sender === "bot" ? '4px' : '18px',
                                            borderBottomRightRadius: msg.sender === "bot" ? '18px' : '4px',
                                            border: msg.sender === "bot" ? '1px solid #e0e0e0' : 'none'
                                        }}
                                    >
                                        {msg.text.split('\n').map((line, i) => (
                                            <span key={i}>{line}<br /></span>
                                        ))}

                                        {msg.drinks && msg.drinks.length > 0 && (
                                            <div className={styles.recommendations}>
                                                {msg.drinks.map((drink, idx) => (
                                                    <div key={idx} className={styles.drinkCard}>
                                                        {drink.image_url && (
                                                            <div className={styles.drinkImageWrapper}>
                                                                <img
                                                                    src={drink.image_url}
                                                                    alt={drink.name}
                                                                    className={styles.drinkImage}
                                                                />
                                                            </div>
                                                        )}
                                                        <div className={styles.drinkInfo}>
                                                            <div className={styles.drinkName}>{drink.name}</div>
                                                            <div className={styles.drinkMeta}>{drink.abv}% | {drink.volume}</div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                            {isLoading && (
                                <div
                                    style={{
                                        display: 'flex',
                                        gap: '0.5rem',
                                        alignItems: 'flex-end',
                                        justifyContent: 'flex-start'
                                    }}
                                >
                                    <div className={styles.avatar}>🍶</div>
                                    <div
                                        style={{
                                            maxWidth: '70%',
                                            padding: '0.8rem 1rem',
                                            borderRadius: '18px',
                                            fontSize: '0.95rem',
                                            lineHeight: '1.4',
                                            position: 'relative',
                                            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
                                            backgroundColor: '#fff',
                                            color: '#333',
                                            borderBottomLeftRadius: '4px',
                                            border: '1px solid #e0e0e0'
                                        }}
                                    >
                                        <span className={styles.loadingDots}>주모가 생각 중이오...</span>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                        {messages.length === 1 && (
                            <div className={styles.quickReplies}>
                                {suggestions.map((suggestion, index) => (
                                    <button
                                        key={index}
                                        className={styles.quickReplyButton}
                                        onClick={() => handleSuggestionClick(suggestion)}
                                    >
                                        {suggestion}
                                    </button>
                                ))}
                            </div>
                        )}

                        <div className={styles.inputArea}>
                            <input
                                type="text"
                                className={styles.input}
                                placeholder="궁금한 술이 있소?"
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                onKeyDown={handleKeyDown} {/* <-- 수정된 부분: onKeyPress -> onKeyDown */}
                            />
                            <button className={styles.sendButton} onClick={() => handleSendMessage()}>
                                ➤
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
