import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import styles from './Chatbot.module.css';
import { Rnd } from 'react-rnd';

import Link from 'next/link';

type Drink = {
    id: number;
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

type ViewState = 'menu' | 'chat';

export default function Chatbot() {
    const [isOpen, setIsOpen] = useState(false);
    const [view, setView] = useState<ViewState>('chat');

    // Chat Logic State
    const [messages, setMessages] = useState<Message[]>([
        { id: 1, text: "어서오슈!!! 🍶\n무엇을 도와드릴까유~?", sender: "bot" }
    ]);
    const suggestions = [
        "오늘의 전통주 추천해줘",
        "인기 있는 술은 뭐야?",
        "전통주 칵테일 레시피 알려줘",
        "선물하기 좋은 술 추천해줘"
    ];
    const [inputText, setInputText] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [isMounted, setIsMounted] = useState(false);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        setIsMounted(true);
    }, []);

    useEffect(() => {
        if (view === 'chat') {
            scrollToBottom();
        }
    }, [messages, isOpen, isLoading, view]);

    // Handle click outside to close
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            // Check if the click is on the toggle button (to prevent immediate closing when opening)
            const target = event.target as HTMLElement;
            if (target.closest(`.${styles.button}`)) return;

            // Check if the click is inside the chatbot window (including resize handles)
            if (isOpen && !target.closest('.chatbot-main-window')) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen]);

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

    const toggleChat = () => {
        setIsOpen(!isOpen);
        if (!isOpen) {
        }
    };

    return (
        <>
            {isOpen && isMounted && (
                <Rnd
                    default={{
                        x: window.innerWidth - 420, // Initial position right
                        y: window.innerHeight - 600, // Initial position bottom
                        width: 380,
                        height: 550,
                    }}
                    minWidth={300}
                    minHeight={400}
                    bounds="window"
                    dragHandleClassName={styles.header} // Only header is draggable
                    style={{ zIndex: 9999 }}
                    className="chatbot-main-window"
                    enableUserSelectHack={false}
                >
                    <div className={`${styles.panel} ${styles.open}`} ref={containerRef}>
                        <div className={styles.header}>
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                {view === 'chat' && (
                                    <button className={styles.backButton} onClick={() => setView('menu')}>
                                        ←
                                    </button>
                                )}
                                <span className={styles.title}>
                                    주모
                                </span>
                            </div>
                            <button className={styles.closeBtn} onClick={() => setIsOpen(false)}>
                                ✕
                            </button>
                        </div>

                        <div className={styles.content}>
                            {view === 'menu' ? (
                                <div className={styles.menuGrid}>
                                    {/* ... menu items ... */}
                                    <button className={styles.menuItem} onClick={() => setView('chat')}>
                                        <span className={styles.icon}>🤖</span>
                                        <span>챗봇 대화</span>
                                    </button>
                                    <button className={styles.menuItem}>
                                        <span className={styles.icon}>🔍</span>
                                        <span>술 검색</span>
                                    </button>
                                    <button className={styles.menuItem}>
                                        <span className={styles.icon}>🗺️</span>
                                        <span>지도 보기</span>
                                    </button>
                                    <button className={styles.menuItem}>
                                        <span className={styles.icon}>❓</span>
                                        <span>도움말</span>
                                    </button>
                                </div>
                            ) : (
                                // Chat Interface
                                <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                                    <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', padding: '20px' }}>
                                        {messages.map((msg) => (
                                            <div
                                                key={msg.id}
                                                className={`${styles.messageRow} ${msg.sender === "bot" ? styles.botRow : styles.userRow}`}
                                            >
                                                {msg.sender === "bot" && (
                                                    <div className={styles.avatar}></div>
                                                )}
                                                <div className={`${styles.bubble} ${msg.sender === "bot" ? styles.botBubble : styles.userBubble}`}>
                                                    {msg.text.split('\n').map((line, i) => (
                                                        <span key={i}>{line}<br /></span>
                                                    ))}

                                                    {msg.drinks && msg.drinks.length > 0 && (
                                                        <div className={styles.recommendations}>
                                                            {msg.drinks.map((drink, idx) => (
                                                                <Link href={`/drink/${drink.id}`} key={idx} style={{ textDecoration: 'none', color: 'inherit' }}>
                                                                    <div className={styles.drinkCard}>
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
                                                                </Link>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                        {isLoading && (
                                            <div className={`${styles.messageRow} ${styles.botRow}`}>
                                                <div className={styles.avatar}></div>
                                                <div className={`${styles.bubble} ${styles.botBubble}`}>
                                                    <span className={styles.loadingDots}>주모가 생각 중이오...</span>
                                                </div>
                                            </div>
                                        )}
                                        <div ref={messagesEndRef} />
                                    </div>
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

                                    <div className={styles.inputArea}>
                                        <input
                                            type="text"
                                            className={styles.input}
                                            placeholder="궁금한 술이 있소?"
                                            value={inputText}
                                            onChange={(e) => setInputText(e.target.value)}
                                            onKeyDown={handleKeyDown}
                                        />
                                        <button className={styles.sendButton} onClick={() => handleSendMessage()}>
                                            ➤
                                        </button>
                                    </div>
                                </div>
                            )}
                    </div>
                </Rnd >
            )
            }

            {
                !isOpen && (
                    <div className={styles.container}>
                        <button className={styles.button} onClick={toggleChat}>
                            <Image
                                src="/이리오너라.png"
                                alt="이리오너라"
                                width={36}
                                height={36}
                                style={{ borderRadius: '50%' }}
                            />
                            <span>이리오너라~</span>
                        </button>
                    </div>
                )
            }
        </>
    );
}
