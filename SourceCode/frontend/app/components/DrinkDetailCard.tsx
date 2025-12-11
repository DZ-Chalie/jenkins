"use client";

import Image from "next/image";
import { useState, useEffect } from "react";
import styles from "./DrinkDetailCard.module.css";

interface Cocktail {
    cocktail_title: string;
    cocktail_base: string;
    cocktail_garnish: string;
    cocktail_recipe: string;
    cocktail_image_url?: string;
    youtube_video_id?: string;
    youtube_video_title?: string;
    youtube_thumbnail_url?: string;
}

interface SimilarDrink {
    id: number;
    name: string;
    image_url?: string;
    score: number;
}

interface HansangItem {
    name: string;
    image_url?: string;
    reason: string;
    link_url?: string;
    specialty_used?: string;  // Which specialty product was used
}

export interface DrinkDetail {
    id?: number;
    name: string;
    description: string;
    intro?: string;
    image_url?: string;
    url?: string;
    abv?: string;
    volume?: string;
    type?: string;
    province?: string;
    city?: string;
    tags?: string[];
    foods?: string[];
    pairing_food?: string[];
    cocktails?: Cocktail[];
    encyclopedia?: {
        title: string;
        text: string;
        images?: { src: string; alt: string; }[];
    }[];
    selling_shops?: {
        shop_id: number;
        name: string;
        address: string;
        contact: string;
        url: string;
        price: number;
    }[];
    brewery?: {
        name?: string;
        address?: string;
        homepage?: string;
        contact?: string;
    };
    detail?: {
        알콜도수?: string;
        용량?: string;
        종류?: string;
        원재료?: string;
        수상내역?: string;
    };
    candidates?: any[];
    score?: number;
    // NEW: Encyclopedia price fields
    price_is_reference?: boolean;
    encyclopedia_price_text?: string;
    encyclopedia_url?: string;
}

interface DrinkDetailCardProps {
    drink: DrinkDetail;
    isOCR?: boolean;
    onGenerateCocktail?: (name: string) => void;
    generatedFood?: { name: string, reason: string } | null;
    generatedCocktails?: Cocktail[];
    isGeneratingCocktail?: boolean;
    onGenerateHansang?: (province: string, city: string) => void;
    generatedHansang?: HansangItem[];
    isGeneratingHansang?: boolean;
}

type TabType = 'food' | 'cocktail' | 'hansang';

export default function DrinkDetailCard({
    drink,
    isOCR = false,
    onGenerateCocktail,
    generatedFood,
    generatedCocktails = [],
    isGeneratingCocktail = false,
    onGenerateHansang,
    generatedHansang = [],
    isGeneratingHansang = false
}: DrinkDetailCardProps) {

    // Normalize data
    const foods = drink.foods || drink.pairing_food || [];
    const intro = drink.intro || drink.description;
    const abv = drink.abv || drink.detail?.알콜도수;
    const volume = drink.volume || drink.detail?.용량;
    const type = drink.type || drink.detail?.종류;

    // Tab state
    const [activeTab, setActiveTab] = useState<TabType>('food');

    // Similar Drinks State
    const [similarDrinks, setSimilarDrinks] = useState<SimilarDrink[]>([]);

    useEffect(() => {
        if (drink.name) {
            fetch('/api/python/search/similar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: drink.name,
                    exclude_id: drink.id || null  // Explicitly set null if undefined
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (Array.isArray(data)) {
                        setSimilarDrinks(data);
                    }
                })
                .catch(err => console.error("Failed to fetch similar drinks:", err));
        }
    }, [drink.name, drink.id]);

    return (
        <div className={styles.card}>

            {/* HERO SECTION */}
            <section style={{ display: 'flex', gap: '40px', alignItems: 'flex-start', flexWrap: 'wrap', marginBottom: '40px' }}>

                {/* Image Column */}
                <div style={{ flex: '0 0 400px', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {drink.image_url ? (
                        <div style={{ background: "url('/한지.jpg')", backgroundSize: 'cover', padding: '10px', borderRadius: '16px', border: '1px solid #d7ccc8', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                            {isOCR && <p style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: '#666', fontWeight: '600', textAlign: 'center' }}>🔍 검색된 술 정보</p>}
                            <div style={{ width: '100%', height: '400px', overflow: 'hidden', borderRadius: '8px', background: '#f8f9fa', position: 'relative' }}>
                                <Image
                                    src={`/api/image-proxy?url=${encodeURIComponent(drink.image_url)}`}
                                    alt={drink.name}
                                    fill
                                    style={{ objectFit: 'contain' }}
                                    sizes="(max-width: 768px) 100vw, 400px"
                                    unoptimized={true}
                                />
                            </div>
                        </div>
                    ) : (
                        <div style={{ width: '100%', height: '400px', background: '#eee', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '16px' }}>
                            🍶 이미지 없음
                        </div>
                    )}

                    {drink.url && (
                        <a href={drink.url} target="_blank" rel="noopener noreferrer" className={styles.moreInfoButton} style={{ display: 'block', textAlign: 'center', padding: '12px', fontSize: '1.1rem', background: '#333', color: '#fff', borderRadius: '12px', textDecoration: 'none', fontWeight: 'bold' }}>
                            더 자세한 정보 보기
                        </a>
                    )}
                </div>

                {/* Info Column */}
                <div style={{ flex: '1', minWidth: '300px', display: 'flex', flexDirection: 'column', gap: '25px' }}>
                    {/* Header & Stats */}
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '15px', flexWrap: 'wrap' }}>
                            <h2 style={{ fontSize: '2.8rem', fontWeight: '800', margin: 0, color: '#222' }}>{drink.name}</h2>
                            {type && (
                                <span style={{ background: '#333', color: '#fff', padding: '6px 12px', borderRadius: '20px', fontSize: '1rem', fontWeight: '600' }}>
                                    {type}
                                </span>
                            )}
                        </div>
                        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                            {abv && <span style={{ background: '#e3f2fd', color: '#1565c0', padding: '8px 14px', borderRadius: '8px', fontWeight: '600', fontSize: '1.1rem' }}>💧 {abv}</span>}
                            {volume && <span style={{ background: '#f3e5f5', color: '#7b1fa2', padding: '8px 14px', borderRadius: '8px', fontWeight: '600', fontSize: '1.1rem' }}>🧴 {volume}</span>}
                            {(drink.province || drink.city) && (
                                <span style={{ background: '#fff3e0', color: '#e65100', padding: '8px 14px', borderRadius: '8px', fontWeight: '600', fontSize: '1.1rem' }}>
                                    📍 {drink.province}{drink.city ? ` ${drink.city}` : ''}
                                </span>
                            )}
                        </div>
                    </div>

                    {/* Description */}
                    <div style={{
                        background: "url('/한지.jpg')",
                        backgroundSize: 'cover',
                        padding: '25px',
                        borderRadius: '16px',
                        border: '1px solid #d7ccc8',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                    }}>
                        <h4 style={{ margin: '0 0 10px 0', color: '#575151', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            📜 술 설명
                        </h4>
                        <p style={{ fontSize: '1.1rem', lineHeight: '1.8', color: '#333', margin: 0 }}>
                            {intro}
                        </p>
                    </div>

                    {/* Details Grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                        {drink.brewery && drink.brewery.name && (
                            <div style={{ background: "url('/한지.jpg')", backgroundSize: 'cover', border: '1px solid #d7ccc8', padding: '15px', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                <h4 style={{ margin: '0 0 8px 0', color: '#5d4037', fontSize: '0.95rem' }}>🏭 양조장</h4>
                                <p style={{ margin: 0, fontWeight: '600', fontSize: '1rem', color: '#3e2723' }}>{drink.brewery.name}</p>
                                {drink.brewery.address && <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#795548' }}>{drink.brewery.address}</p>}
                            </div>
                        )}
                        {drink.detail?.원재료 && (
                            <div style={{ background: "url('/한지.jpg')", backgroundSize: 'cover', border: '1px solid #d7ccc8', padding: '15px', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                <h4 style={{ margin: '0 0 8px 0', color: '#5d4037', fontSize: '0.95rem' }}>🌾 원재료</h4>
                                <p style={{ margin: 0, fontSize: '1rem', color: '#3e2723', lineHeight: '1.4' }}>{drink.detail.원재료}</p>
                            </div>
                        )}
                        {drink.detail?.수상내역 && (
                            <div style={{ background: "url('/한지.jpg')", backgroundSize: 'cover', border: '1px solid #d7ccc8', padding: '15px', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                <h4 style={{ margin: '0 0 8px 0', color: '#5d4037', fontSize: '0.95rem' }}>🏅 수상내역</h4>
                                <p style={{ margin: 0, fontSize: '0.95rem', color: '#3e2723', lineHeight: '1.4' }}>{drink.detail.수상내역}</p>
                            </div>
                        )}
                        {foods.length > 0 && (
                            <div style={{ background: "url('/한지.jpg')", backgroundSize: 'cover', border: '1px solid #d7ccc8', padding: '15px', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                <h4 style={{ margin: '0 0 8px 0', color: '#5d4037', fontSize: '0.95rem' }}>🥘 어울리는 음식</h4>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                    {foods.map((food, idx) => (
                                        <span key={idx} style={{ background: 'rgba(255,255,255,0.6)', border: '1px solid #a1887f', color: '#3e2723', padding: '4px 10px', borderRadius: '12px', fontSize: '0.85rem', fontWeight: '600' }}>
                                            {food}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </section>

            {/* AI RECOMMENDATIONS TABS */}
            {(onGenerateCocktail || onGenerateHansang) && (
                <section className={styles.aiTabs}>
                    <div className={styles.tabButtons}>
                        <button
                            className={activeTab === 'food' ? styles.active : ''}
                            onClick={() => setActiveTab('food')}
                        >
                            🍽️ AI 안주 추천
                        </button>
                        <button
                            className={activeTab === 'cocktail' ? styles.active : ''}
                            onClick={() => setActiveTab('cocktail')}
                        >
                            🍹 AI 칵테일
                        </button>
                        {drink.province && onGenerateHansang && (
                            <button
                                className={activeTab === 'hansang' ? styles.active : ''}
                                onClick={() => setActiveTab('hansang')}
                            >
                                🍚 지역 한상차림
                            </button>
                        )}
                    </div>

                    <div className={styles.tabContent}>
                        {/* AI Food Tab */}
                        {activeTab === 'food' && (
                            <div>
                                {isGeneratingCocktail ? (
                                    <div style={{ textAlign: 'center', padding: '40px', background: 'rgba(255,255,255,0.8)', borderRadius: '12px' }}>
                                        <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🤖🍽️</div>
                                        <h4 style={{ fontSize: '1.2rem', color: '#0277bd', marginBottom: '10px' }}>AI가 안주를 생각 중!</h4>
                                        <p style={{ color: '#555', fontSize: '1rem' }}>잠시만 기다려주세요...</p>
                                    </div>
                                ) : generatedFood ? (
                                    <div>
                                        <div style={{ background: "url('/한지흰색.jpg')", backgroundSize: 'cover', border: '2px solid #d7ccc8', padding: '30px', borderRadius: '16px', marginBottom: '20px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}>
                                            <h3 style={{ margin: '0 0 15px 0', color: '#e65100', fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                                🍽️ AI 추천 안주
                                            </h3>
                                            <div style={{ fontSize: '2rem', fontWeight: '800', color: '#bf360c', marginBottom: '15px' }}>{generatedFood.name}</div>
                                            <p style={{ margin: 0, fontSize: '1.1rem', color: '#5d4037', lineHeight: '1.6' }}>{generatedFood.reason}</p>
                                        </div>
                                        {onGenerateCocktail && (
                                            <button
                                                onClick={() => onGenerateCocktail(drink.name)}
                                                style={{
                                                    background: 'linear-gradient(45deg, #ff6f00, #ffca28)',
                                                    color: 'white',
                                                    border: 'none',
                                                    padding: '12px 24px',
                                                    borderRadius: '25px',
                                                    fontSize: '1rem',
                                                    fontWeight: 'bold',
                                                    cursor: 'pointer',
                                                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                                    transition: 'transform 0.2s',
                                                    width: '100%'
                                                }}
                                                onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
                                                onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                            >
                                                🔄 다시 추천받기
                                            </button>
                                        )}
                                    </div>
                                ) : (
                                    <div style={{ textAlign: 'center', padding: '40px', background: 'rgba(255,255,255,0.7)', borderRadius: '12px' }}>
                                        <p style={{ color: '#666', marginBottom: '20px', fontSize: '1.1rem' }}>
                                            이 술과 잘 어울리는<br />안주를 AI가 추천해드려요!
                                        </p>
                                        {onGenerateCocktail && (
                                            <button
                                                onClick={() => onGenerateCocktail(drink.name)}
                                                style={{
                                                    background: 'linear-gradient(45deg, #ff6f00, #ffca28)',
                                                    color: 'white',
                                                    border: 'none',
                                                    padding: '14px 32px',
                                                    borderRadius: '25px',
                                                    fontSize: '1.1rem',
                                                    fontWeight: 'bold',
                                                    cursor: 'pointer',
                                                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                                    transition: 'transform 0.2s'
                                                }}
                                                onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                                                onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                            >
                                                🤖 AI 추천 받기
                                            </button>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* AI Cocktail Tab */}
                        {activeTab === 'cocktail' && (
                            <div>
                                {isGeneratingCocktail ? (
                                    <div style={{ textAlign: 'center', padding: '40px', background: 'rgba(255,255,255,0.8)', borderRadius: '12px' }}>
                                        <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🤖🍹</div>
                                        <h4 style={{ fontSize: '1.2rem', color: '#0277bd', marginBottom: '10px' }}>AI가 칵테일 레시피를 생성 중!</h4>
                                        <p style={{ color: '#555', fontSize: '1rem' }}>잠시만 기다려주세요...</p>
                                    </div>
                                ) : generatedCocktails.length > 0 ? (
                                    <div>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginBottom: '20px' }}>
                                            {generatedCocktails.map((cocktail, index) => (
                                                <div key={index} style={{
                                                    background: 'linear-gradient(135deg, rgba(255, 248, 240, 0.98), rgba(255, 243, 224, 0.98))',
                                                    borderRadius: '20px',
                                                    overflow: 'hidden',
                                                    border: '2px solid #ffb74d',
                                                    boxShadow: '0 6px 20px rgba(255, 152, 0, 0.2)'
                                                }}>
                                                    {cocktail.cocktail_image_url && (
                                                        <div style={{ height: '200px', overflow: 'hidden', position: 'relative' }}>
                                                            <Image src={`/api/image-proxy?url=${encodeURIComponent(cocktail.cocktail_image_url)}`} alt={cocktail.cocktail_title} fill style={{ objectFit: 'cover' }} />
                                                        </div>
                                                    )}
                                                    <div style={{ padding: '30px' }}>
                                                        <h3 style={{
                                                            margin: '0 0 20px 0',
                                                            fontSize: '1.8rem',
                                                            fontWeight: '900',
                                                            color: '#e65100',
                                                            textShadow: '1px 1px 2px rgba(0,0,0,0.1)'
                                                        }}>
                                                            🍹 {cocktail.cocktail_title}
                                                        </h3>
                                                        <div style={{
                                                            background: 'linear-gradient(135deg, rgba(255,235,59,0.3), rgba(255,193,7,0.3))',
                                                            padding: '15px 18px',
                                                            borderRadius: '12px',
                                                            marginBottom: '15px',
                                                            border: '1px solid rgba(255,152,0,0.4)'
                                                        }}>
                                                            <strong style={{ color: '#e65100', fontSize: '1.05rem' }}>재료:</strong>{' '}
                                                            <span style={{ color: '#3e2723', fontSize: '1rem', fontWeight: '500' }}>{cocktail.cocktail_base}</span>
                                                        </div>
                                                        {cocktail.cocktail_garnish && (
                                                            <div style={{
                                                                background: 'linear-gradient(135deg, rgba(129,199,132,0.3), rgba(102,187,106,0.3))',
                                                                padding: '15px 18px',
                                                                borderRadius: '12px',
                                                                marginBottom: '15px',
                                                                border: '1px solid rgba(102,187,106,0.4)'
                                                            }}>
                                                                <strong style={{ color: '#2e7d32', fontSize: '1.05rem' }}>가니쉬:</strong>{' '}
                                                                <span style={{ color: '#1b5e20', fontSize: '1rem', fontWeight: '500' }}>{cocktail.cocktail_garnish}</span>
                                                            </div>
                                                        )}
                                                        <div style={{
                                                            background: 'linear-gradient(135deg, rgba(100,181,246,0.25), rgba(66,165,245,0.25))',
                                                            padding: '20px',
                                                            borderRadius: '12px',
                                                            border: '1px solid rgba(66,165,245,0.4)'
                                                        }}>
                                                            <strong style={{
                                                                color: '#01579b',
                                                                fontSize: '1.1rem',
                                                                display: 'block',
                                                                marginBottom: '12px'
                                                            }}>📝 레시피:</strong>
                                                            <ol style={{
                                                                margin: '0',
                                                                paddingLeft: '20px',
                                                                listStyleType: 'decimal'
                                                            }}>
                                                                {cocktail.cocktail_recipe.split(/\d+\./).filter(step => step.trim()).map((step, stepIndex) => (
                                                                    <li key={stepIndex} style={{
                                                                        margin: '10px 0',
                                                                        fontSize: '1rem',
                                                                        color: '#01579b',
                                                                        lineHeight: '1.8',
                                                                        fontWeight: '500'
                                                                    }}>
                                                                        {step.trim()}
                                                                    </li>
                                                                ))}
                                                            </ol>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                        {onGenerateCocktail && (
                                            <button
                                                onClick={() => onGenerateCocktail(drink.name)}
                                                style={{
                                                    background: 'linear-gradient(45deg, #ff6f00, #ffca28)',
                                                    color: 'white',
                                                    border: 'none',
                                                    padding: '12px 24px',
                                                    borderRadius: '25px',
                                                    fontSize: '1rem',
                                                    fontWeight: 'bold',
                                                    cursor: 'pointer',
                                                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                                    transition: 'transform 0.2s',
                                                    width: '100%'
                                                }}
                                                onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
                                                onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                            >
                                                🔄 더 추천받기
                                            </button>
                                        )}
                                    </div>
                                ) : (
                                    <div style={{ textAlign: 'center', padding: '40px', background: 'rgba(255,255,255,0.7)', borderRadius: '12px' }}>
                                        <p style={{ color: '#666', marginBottom: '20px', fontSize: '1.1rem' }}>
                                            이 술로 만들 수 있는<br />창의적인 칵테일을 AI가 추천해드려요!
                                        </p>
                                        {onGenerateCocktail && (
                                            <button
                                                onClick={() => onGenerateCocktail(drink.name)}
                                                style={{
                                                    background: 'linear-gradient(45deg, #ff6f00, #ffca28)',
                                                    color: 'white',
                                                    border: 'none',
                                                    padding: '14px 32px',
                                                    borderRadius: '25px',
                                                    fontSize: '1.1rem',
                                                    fontWeight: 'bold',
                                                    cursor: 'pointer',
                                                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                                    transition: 'transform 0.2s'
                                                }}
                                                onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                                                onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                            >
                                                🤖 AI 추천 받기
                                            </button>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Hansang Tab */}
                        {activeTab === 'hansang' && drink.province && onGenerateHansang && (
                            <div>
                                {isGeneratingHansang ? (
                                    <div style={{ textAlign: 'center', padding: '40px', background: 'rgba(255,255,255,0.8)', borderRadius: '12px' }}>
                                        <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🤖🍚</div>
                                        <h4 style={{ fontSize: '1.2rem', color: '#0277bd', marginBottom: '10px' }}>
                                            {drink.province} 특산물로 한상차림을 준비하는 중!
                                        </h4>
                                        <p style={{ color: '#555', fontSize: '1rem' }}>잠시만 기다려주세요...</p>
                                    </div>
                                ) : generatedHansang.length > 0 ? (
                                    <div>
                                        <div style={{ background: 'rgba(255,255,255,0.8)', padding: '20px', borderRadius: '12px', marginBottom: '20px', border: '2px solid #ffca28' }}>
                                            <h3 style={{ margin: '0 0 10px 0', color: '#e65100', fontSize: '1.3rem' }}>
                                                🍚 {drink.province} 특산물 한상차림
                                            </h3>
                                            <p style={{ margin: 0, color: '#666', fontSize: '0.95rem' }}>
                                                AI가 {drink.province}{drink.city ? ` ${drink.city}` : ''}의 특산물로 추천하는 안주입니다
                                            </p>
                                        </div>
                                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '20px', marginBottom: '20px' }}>
                                            {generatedHansang.map((item, index) => (
                                                <div key={index} style={{
                                                    background: item.specialty_used
                                                        ? "linear-gradient(135deg, rgba(255, 243, 224, 0.95), rgba(255, 235, 205, 0.95))"
                                                        : "linear-gradient(135deg, rgba(250, 250, 250, 0.95), rgba(240, 240, 240, 0.95))",
                                                    borderRadius: '16px',
                                                    overflow: 'hidden',
                                                    border: item.specialty_used ? '2px solid #ffca28' : '2px solid #bdbdbd',
                                                    boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                                                    transition: 'transform 0.2s'
                                                }}
                                                    onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
                                                    onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                                                >
                                                    {item.image_url && (
                                                        <div style={{ height: '180px', position: 'relative', background: '#f8f9fa' }}>
                                                            <Image
                                                                src={`/api/image-proxy?url=${encodeURIComponent(item.image_url)}`}
                                                                alt={item.name}
                                                                fill
                                                                style={{ objectFit: 'cover' }}
                                                                sizes="250px"
                                                                onError={(e) => {
                                                                    // Replace broken image with placeholder
                                                                    const target = e.target as HTMLImageElement;
                                                                    target.style.display = 'none';
                                                                    const parent = target.parentElement;
                                                                    if (parent && !parent.querySelector('.placeholder')) {
                                                                        const placeholder = document.createElement('div');
                                                                        placeholder.className = 'placeholder';
                                                                        placeholder.style.cssText = 'width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 4rem; background: linear-gradient(135deg, #fff3e0, #ffecb3)';
                                                                        placeholder.textContent = '🍽️';
                                                                        parent.appendChild(placeholder);
                                                                    }
                                                                }}
                                                            />
                                                        </div>
                                                    )}
                                                    <div style={{ padding: '20px' }}>
                                                        {item.specialty_used && (
                                                            <div style={{
                                                                display: 'inline-block',
                                                                background: 'linear-gradient(45deg, #ff6f00, #ffca28)',
                                                                color: 'white',
                                                                padding: '4px 12px',
                                                                borderRadius: '12px',
                                                                fontSize: '0.75rem',
                                                                fontWeight: '700',
                                                                marginBottom: '10px',
                                                                boxShadow: '0 2px 4px rgba(255, 111, 0, 0.3)'
                                                            }}>
                                                                🌾 {item.specialty_used}
                                                            </div>
                                                        )}
                                                        {!item.specialty_used && (
                                                            <div style={{
                                                                display: 'inline-block',
                                                                background: '#757575',
                                                                color: 'white',
                                                                padding: '4px 12px',
                                                                borderRadius: '12px',
                                                                fontSize: '0.75rem',
                                                                fontWeight: '700',
                                                                marginBottom: '10px'
                                                            }}>
                                                                🍽️ AI 추천
                                                            </div>
                                                        )}
                                                        <h4 style={{ margin: '0 0 10px 0', fontSize: '1.3rem', fontWeight: '800', color: '#3e2723' }}>
                                                            {item.name}
                                                        </h4>
                                                        <p style={{ margin: 0, fontSize: '0.95rem', color: '#5d4037', lineHeight: '1.5' }}>
                                                            {item.reason}
                                                        </p>
                                                        {item.link_url && (
                                                            <a href={item.link_url} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-block', marginTop: '12px', color: '#ff6f00', fontSize: '0.9rem', textDecoration: 'underline', fontWeight: '600' }}>
                                                                🛒 특산물 구매하기 →
                                                            </a>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                        <button
                                            onClick={() => onGenerateHansang(drink.province || '', drink.city || '')}
                                            style={{
                                                background: 'linear-gradient(45deg, #ff6f00, #ffca28)',
                                                color: 'white',
                                                border: 'none',
                                                padding: '12px 24px',
                                                borderRadius: '25px',
                                                fontSize: '1rem',
                                                fontWeight: 'bold',
                                                cursor: 'pointer',
                                                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                                transition: 'transform 0.2s',
                                                width: '100%'
                                            }}
                                            onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
                                            onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                        >
                                            🔄 한상차림 다시 추천받기
                                        </button>
                                    </div>
                                ) : (
                                    <div style={{ textAlign: 'center', padding: '40px', background: 'rgba(255,255,255,0.7)', borderRadius: '12px' }}>
                                        <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🍚</div>
                                        <h4 style={{ fontSize: '1.3rem', color: '#333', marginBottom: '10px' }}>
                                            {drink.province} 특산물 한상차림
                                        </h4>
                                        <p style={{ color: '#666', marginBottom: '20px', fontSize: '1rem', lineHeight: '1.6' }}>
                                            {drink.province}{drink.city ? ` ${drink.city}` : ''}의 특산물로<br />
                                            이 술과 어울리는 한상차림을 AI가 추천해드려요!
                                        </p>
                                        <button
                                            onClick={() => onGenerateHansang(drink.province || '', drink.city || '')}
                                            style={{
                                                background: 'linear-gradient(45deg, #ff6f00, #ffca28)',
                                                color: 'white',
                                                border: 'none',
                                                padding: '14px 32px',
                                                borderRadius: '25px',
                                                fontSize: '1.1rem',
                                                fontWeight: 'bold',
                                                cursor: 'pointer',
                                                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                                transition: 'transform 0.2s'
                                            }}
                                            onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                                            onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                        >
                                            🤖 한상차림 추천받기
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </section>
            )}

            {/* BREWERY INFORMATION SECTION */}
            {drink.brewery && drink.brewery.name && (
                <section style={{ borderTop: '2px solid #f0f0f0', paddingTop: '40px', marginTop: '40px' }}>
                    <h3 style={{ margin: '0 0 25px 0', color: '#5d4037', fontSize: '1.6rem', display: 'flex', alignItems: 'center', gap: '10px', fontWeight: '800' }}>
                        🏭 양조장 정보
                    </h3>
                    <div style={{
                        background: "url('/한지.jpg')",
                        backgroundSize: 'cover',
                        border: '2px solid rgba(141, 110, 99, 0.3)',
                        borderRadius: '20px',
                        padding: '35px',
                        boxShadow: '0 8px 24px rgba(141, 110, 99, 0.15)',
                        animation: 'fadeIn 0.5s ease-out'
                    }}>
                        <div style={{ display: 'grid', gap: '20px' }}>
                            {/* Brewery Name */}
                            <div style={{
                                background: 'rgba(255, 255, 255, 0.8)',
                                padding: '20px',
                                borderRadius: '16px',
                                border: '1px solid rgba(141, 110, 99, 0.2)',
                                backdropFilter: 'blur(8px)'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                                    <span style={{ fontSize: '1.5rem' }}>🏠</span>
                                    <span style={{ fontSize: '0.9rem', color: '#8d6e63', fontWeight: '600', letterSpacing: '1px' }}>양조장</span>
                                </div>
                                <div style={{ fontSize: '1.4rem', fontWeight: '800', color: '#4e342e', letterSpacing: '0.5px' }}>
                                    {drink.brewery.name}
                                </div>
                            </div>

                            {/* Address */}
                            {drink.brewery.address && (
                                <div style={{
                                    background: 'rgba(255, 255, 255, 0.7)',
                                    padding: '18px 20px',
                                    borderRadius: '14px',
                                    border: '1px solid rgba(141, 110, 99, 0.15)',
                                    transition: 'all 0.3s'
                                }}
                                    onMouseOver={(e) => {
                                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.95)';
                                        e.currentTarget.style.transform = 'translateX(5px)';
                                    }}
                                    onMouseOut={(e) => {
                                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.7)';
                                        e.currentTarget.style.transform = 'translateX(0)';
                                    }}
                                >
                                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                                        <span style={{ fontSize: '1.3rem', marginTop: '2px' }}>📍</span>
                                        <div>
                                            <div style={{ fontSize: '0.85rem', color: '#8d6e63', fontWeight: '600', marginBottom: '6px' }}>주소</div>
                                            <div style={{ fontSize: '1.05rem', color: '#3e2723', lineHeight: '1.6' }}>
                                                {drink.brewery.address}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Contact & Homepage Grid */}
                            <div style={{ display: 'grid', gridTemplateColumns: drink.brewery.contact && drink.brewery.homepage ? '1fr 1fr' : '1fr', gap: '15px' }}>
                                {/* Contact */}
                                {drink.brewery.contact && (
                                    <div style={{
                                        background: 'rgba(255, 255, 255, 0.7)',
                                        padding: '18px 20px',
                                        borderRadius: '14px',
                                        border: '1px solid rgba(141, 110, 99, 0.15)',
                                        transition: 'all 0.3s'
                                    }}
                                        onMouseOver={(e) => {
                                            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.95)';
                                            e.currentTarget.style.boxShadow = '0 4px 12px rgba(141, 110, 99, 0.2)';
                                        }}
                                        onMouseOut={(e) => {
                                            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.7)';
                                            e.currentTarget.style.boxShadow = 'none';
                                        }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                                            <span style={{ fontSize: '1.2rem' }}>📞</span>
                                            <span style={{ fontSize: '0.85rem', color: '#8d6e63', fontWeight: '600' }}>연락처</span>
                                        </div>
                                        <div style={{ fontSize: '1.1rem', color: '#3e2723', fontWeight: '600', letterSpacing: '0.5px' }}>
                                            {drink.brewery.contact}
                                        </div>
                                    </div>
                                )}

                                {/* Homepage */}
                                {drink.brewery.homepage && (
                                    <a href={drink.brewery.homepage} target="_blank" rel="noopener noreferrer" style={{
                                        background: 'linear-gradient(135deg, rgba(141, 110, 99, 0.15), rgba(109, 76, 65, 0.2))',
                                        padding: '18px 20px',
                                        borderRadius: '14px',
                                        border: '1px solid rgba(141, 110, 99, 0.25)',
                                        textDecoration: 'none',
                                        transition: 'all 0.3s',
                                        display: 'block'
                                    }}
                                        onMouseOver={(e) => {
                                            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(141, 110, 99, 0.25), rgba(109, 76, 65, 0.3))';
                                            e.currentTarget.style.transform = 'translateY(-3px)';
                                            e.currentTarget.style.boxShadow = '0 6px 16px rgba(141, 110, 99, 0.3)';
                                        }}
                                        onMouseOut={(e) => {
                                            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(141, 110, 99, 0.15), rgba(109, 76, 65, 0.2))';
                                            e.currentTarget.style.transform = 'translateY(0)';
                                            e.currentTarget.style.boxShadow = 'none';
                                        }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                                            <span style={{ fontSize: '1.2rem' }}>🌐</span>
                                            <span style={{ fontSize: '0.85rem', color: '#8d6e63', fontWeight: '600' }}>홈페이지</span>
                                        </div>
                                        <div style={{ fontSize: '0.95rem', color: '#5d4037', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            방문하기
                                            <span style={{ fontSize: '1.1rem' }}>→</span>
                                        </div>
                                    </a>
                                )}
                            </div>
                        </div>
                    </div>
                </section>
            )}

            {/* DB COCKTAILS SECTION */}
            {drink.cocktails && drink.cocktails.length > 0 && (
                <section style={{ borderTop: '2px solid #f0f0f0', paddingTop: '40px', marginTop: '40px' }}>
                    <h3 style={{ margin: '0 0 20px 0', color: '#d32f2f', fontSize: '1.6rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        🏆 추천 칵테일
                    </h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '25px' }}>
                        {drink.cocktails.map((cocktail, index) => (
                            <div key={index} style={{
                                background: '#fff',
                                borderRadius: '16px',
                                overflow: 'hidden',
                                border: '1px solid #eee',
                                boxShadow: '0 8px 24px rgba(0,0,0,0.06)',
                                transition: 'transform 0.2s, box-shadow 0.2s',
                                display: 'flex',
                                flexDirection: 'column'
                            }}
                                onMouseOver={(e) => {
                                    e.currentTarget.style.transform = 'translateY(-5px)';
                                    e.currentTarget.style.boxShadow = '0 12px 32px rgba(0,0,0,0.1)';
                                }}
                                onMouseOut={(e) => {
                                    e.currentTarget.style.transform = 'translateY(0)';
                                    e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.06)';
                                }}
                            >
                                {cocktail.cocktail_image_url ? (
                                    <div style={{ height: '200px', width: '100%', position: 'relative' }}>
                                        <Image
                                            src={`/api/image-proxy?url=${encodeURIComponent(cocktail.cocktail_image_url)}`}
                                            alt={cocktail.cocktail_title}
                                            fill
                                            style={{ objectFit: 'cover' }}
                                        />
                                    </div>
                                ) : (
                                    <div style={{ height: '140px', background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '3rem' }}>
                                        🍸
                                    </div>
                                )}
                                <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                                    <h5 style={{ margin: '0 0 10px 0', fontSize: '1.25rem', fontWeight: '800', color: '#333' }}>
                                        {cocktail.cocktail_title}
                                    </h5>
                                    <div style={{ width: '40px', height: '3px', background: '#ffca28', marginBottom: '15px', borderRadius: '2px' }}></div>
                                    <p style={{ fontSize: '0.95rem', color: '#555', margin: 0, lineHeight: '1.6', whiteSpace: 'pre-line' }}>
                                        {cocktail.cocktail_recipe}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* SELLING SHOPS OR ENCYCLOPEDIA LINK */}
            {drink.price_is_reference ? (
                <section style={{ borderTop: '2px solid #f0f0f0', paddingTop: '40px', marginTop: '40px' }}>
                    <div style={{
                        background: "url('/한지.jpg')",
                        backgroundSize: 'cover',
                        border: '2px solid #d7ccc8',
                        borderRadius: '16px',
                        padding: '30px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '3rem', marginBottom: '15px' }}>📚</div>
                        <h3 style={{ margin: '0 0 15px 0', color: '#333', fontSize: '1.5rem', fontWeight: '800' }}>
                            구매 정보
                        </h3>
                        <p style={{ fontSize: '1.1rem', color: '#666', marginBottom: '20px', lineHeight: '1.6' }}>
                            현재 온라인 판매처 정보가 없습니다.
                        </p>

                        {drink.encyclopedia_price_text && (
                            <div style={{
                                background: 'rgba(255,243,224,0.6)',
                                border: '1px solid #ffca28',
                                borderRadius: '12px',
                                padding: '20px',
                                marginBottom: '20px'
                            }}>
                                <strong style={{ display: 'block', marginBottom: '10px', color: '#e65100', fontSize: '1.1rem' }}>
                                    💰 참고 가격
                                </strong>
                                <div style={{ fontSize: '1.2rem', color: '#3e2723', fontWeight: '600', lineHeight: '1.8' }}>
                                    {(() => {
                                        const priceText = drink.encyclopedia_price_text.replace(/\(가격은 판매처 별로 상이할 수 있습니다\)/g, '');
                                        const matches = priceText.match(/(\d+ml\s*￦[\d,]+)/g) || [];
                                        return matches.map((item, idx) => (
                                            <div key={idx} style={{ marginBottom: idx < matches.length - 1 ? '6px' : '0' }}>
                                                {item.trim()}
                                            </div>
                                        ));
                                    })()}
                                </div>
                                <p style={{ margin: '8px 0 0 0', fontSize: '0.9rem', color: '#795548' }}>
                                    (가격은 판매처 별로 상이할 수 있습니다)
                                </p>
                            </div>
                        )}

                        <p style={{ fontSize: '1rem', color: '#666', marginBottom: '20px', lineHeight: '1.6' }}>
                            더 자세한 제품 정보는 네이버 지식백과에서 확인하실 수 있습니다.
                        </p>

                        {drink.encyclopedia_url && (
                            <a
                                href={drink.encyclopedia_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                    display: 'inline-block',
                                    background: 'linear-gradient(45deg, #ff6f00, #ffca28)',
                                    color: 'white',
                                    padding: '14px 32px',
                                    borderRadius: '25px',
                                    fontSize: '1.1rem',
                                    fontWeight: 'bold',
                                    textDecoration: 'none',
                                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                    transition: 'transform 0.2s'
                                }}
                                onMouseOver={(e) => (e.currentTarget as HTMLElement).style.transform = 'scale(1.05)'}
                                onMouseOut={(e) => (e.currentTarget as HTMLElement).style.transform = 'scale(1)'}
                            >
                                📖 지식백과에서 보기 →
                            </a>
                        )}
                    </div>
                </section>
            ) : drink.selling_shops && drink.selling_shops.length > 0 && (
                <section style={{ borderTop: '2px solid #f0f0f0', paddingTop: '40px', marginTop: '40px' }}>
                    <h3 style={{ fontSize: '1.6rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        🍚🥢 <span style={{ fontWeight: '800', color: '#333' }}>주막 (판매처)</span>
                    </h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '15px' }}>
                        {drink.selling_shops.map((shop, index) => (
                            <div key={index} style={{ background: "url('/한지.jpg')", backgroundSize: 'cover', border: '1px solid #d7ccc8', borderRadius: '12px', padding: '15px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
                                <h4 style={{ margin: '0 0 10px 0', fontSize: '1.1rem', fontWeight: '700', color: '#222' }}>{shop.name}</h4>
                                <p style={{ margin: '0 0 5px 0', fontSize: '0.9rem', color: '#555' }}>📍 {shop.address}</p>
                                <p style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: '#555' }}>📞 {shop.contact}</p>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
                                    <span style={{ fontSize: '1.05rem', fontWeight: '700', color: '#d32f2f' }}>
                                        {shop.price ? `${shop.price.toLocaleString()}원` : '-'}
                                    </span>
                                    <a href={`https://map.naver.com/v5/search/${encodeURIComponent(shop.name)}`} target="_blank" rel="noopener noreferrer" style={{ background: '#03C75A', color: '#fff', padding: '5px 10px', borderRadius: '6px', fontSize: '0.85rem', textDecoration: 'none', fontWeight: 'bold' }}>
                                        지도보기
                                    </a>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* SIMILAR DRINKS */}
            {similarDrinks.length > 0 && (
                <section style={{ borderTop: '2px solid #f0f0f0', paddingTop: '40px', marginTop: '40px' }}>
                    <h3 style={{ fontSize: '1.6rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        🔍 <span style={{ fontWeight: '800', color: '#333' }}>이런 술은 어떠오?</span>
                    </h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '15px' }}>
                        {similarDrinks.filter(simDrink => simDrink.id).map((simDrink, index) => (
                            <a key={index} href={`/drink/${simDrink.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                                <div style={{ background: "url('/한지.jpg')", backgroundSize: 'cover', borderRadius: '12px', overflow: 'hidden', border: '1px solid #d7ccc8', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', transition: 'transform 0.2s' }}
                                    onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
                                    onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                                >
                                    <div style={{ height: '160px', position: 'relative', background: '#f8f9fa' }}>
                                        {simDrink.image_url ? (
                                            <Image
                                                src={`/api/image-proxy?url=${encodeURIComponent(simDrink.image_url)}`}
                                                alt={simDrink.name}
                                                fill
                                                style={{ objectFit: 'contain', padding: '10px' }}
                                                sizes="160px"
                                                unoptimized={true}
                                            />
                                        ) : (
                                            <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🍶</div>
                                        )}
                                    </div>
                                    <div style={{ padding: '10px', textAlign: 'center' }}>
                                        <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: '700', color: '#333' }}>{simDrink.name}</h4>
                                    </div>
                                </div>
                            </a>
                        ))}
                    </div>
                </section>
            )}

            {/* ENCYCLOPEDIA */}
            {drink.encyclopedia && drink.encyclopedia.length > 0 && (
                <section style={{ borderTop: '2px solid #f0f0f0', paddingTop: '40px', marginTop: '40px' }}>
                    <details style={{ background: '#fff3e0', borderRadius: '12px', border: '1px solid #ffe0b2', overflow: 'hidden' }}>
                        <summary style={{ padding: '15px 20px', cursor: 'pointer', fontWeight: '700', color: '#e65100', fontSize: '1.1rem', listStyle: 'none', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <span>📖 전통주 지식백과 (더보기)</span>
                            <span style={{ fontSize: '0.9rem' }}>▼</span>
                        </summary>
                        <div style={{ padding: '20px', borderTop: '1px solid #ffe0b2', background: '#fff' }}>
                            {drink.encyclopedia.map((section, idx) => (
                                <div key={idx} style={{ marginBottom: '25px' }}>
                                    <h4 style={{ fontSize: '1.1rem', color: '#333', marginBottom: '10px', borderLeft: '4px solid #ff9800', paddingLeft: '10px' }}>{section.title}</h4>
                                    <p style={{ fontSize: '1rem', lineHeight: '1.7', color: '#555', whiteSpace: 'pre-line' }}>{section.text}</p>
                                    {section.images && section.images.length > 0 && (
                                        <div style={{ display: 'flex', gap: '10px', overflowX: 'auto', marginTop: '10px', paddingBottom: '10px' }}>
                                            {section.images.map((img, imgIdx) => (
                                                <div key={imgIdx} style={{ height: '150px', width: '200px', position: 'relative', flexShrink: 0 }}>
                                                    <Image
                                                        src={`/api/image-proxy?url=${encodeURIComponent(img.src)}`}
                                                        alt={img.alt}
                                                        fill
                                                        style={{ borderRadius: '8px', objectFit: 'cover' }}
                                                    />
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </details>
                </section>
            )}
        </div>
    );
}
