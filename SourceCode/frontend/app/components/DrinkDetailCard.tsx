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
    pairing_food?: string[]; // Handle both naming conventions
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
    candidates?: any[]; // For OCR candidates, not used in detail view but kept for compatibility
    score?: number;
}

interface DrinkDetailCardProps {
    drink: DrinkDetail;
    isOCR?: boolean; // Flag to show/hide specific OCR features if needed
    onGenerateCocktail?: (name: string) => void; // Callback for AI generation
    generatedFood?: { name: string, reason: string } | null;
    generatedCocktails?: Cocktail[];
    isGeneratingCocktail?: boolean;
}

export default function DrinkDetailCard({
    drink,
    isOCR = false,
    onGenerateCocktail,
    generatedFood,
    generatedCocktails = [],
    isGeneratingCocktail = false
}: DrinkDetailCardProps) {

    // Normalize data (handle different field names from different APIs)
    const foods = drink.foods || drink.pairing_food || [];
    const intro = drink.intro || drink.description;
    const abv = drink.abv || drink.detail?.알콜도수;
    const volume = drink.volume || drink.detail?.용량;
    const type = drink.type || drink.detail?.종류;

    // Similar Drinks State
    const [similarDrinks, setSimilarDrinks] = useState<SimilarDrink[]>([]);

    useEffect(() => {
        if (drink.name) {
            fetch('/api/python/search/similar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: drink.name, exclude_id: drink.id })
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
        <div className={styles.card} style={{ display: 'flex', gap: '30px', alignItems: 'flex-start' }}>

            {/* LEFT: Main Content (Image + Info + Details) */}
            <div style={{ flex: '1', minWidth: '0', display: 'flex', flexDirection: 'column', gap: '40px' }}>

                {/* HERO SECTION: Image | Info */}
                <div style={{ display: 'flex', gap: '40px', alignItems: 'flex-start', flexWrap: 'wrap' }}>

                    {/* Image */}
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

                        {/* More Info Button (moved here for balance) */}
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

                        {/* Description (Moved here, Hanji BG) */}
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

                        {/* Details Grid (Moved here) */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                            {/* Brewery */}
                            {drink.brewery && drink.brewery.name && (
                                <div style={{ background: "url('/한지.jpg')", backgroundSize: 'cover', border: '1px solid #d7ccc8', padding: '15px', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                    <h4 style={{ margin: '0 0 8px 0', color: '#5d4037', fontSize: '0.95rem' }}>🏭 양조장</h4>
                                    <p style={{ margin: 0, fontWeight: '600', fontSize: '1rem', color: '#3e2723' }}>{drink.brewery.name}</p>
                                    {drink.brewery.address && <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#795548' }}>{drink.brewery.address}</p>}
                                </div>
                            )}
                            {/* Ingredients */}
                            {drink.detail?.원재료 && (
                                <div style={{ background: "url('/한지.jpg')", backgroundSize: 'cover', border: '1px solid #d7ccc8', padding: '15px', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                    <h4 style={{ margin: '0 0 8px 0', color: '#5d4037', fontSize: '0.95rem' }}>🌾 원재료</h4>
                                    <p style={{ margin: 0, fontSize: '1rem', color: '#3e2723', lineHeight: '1.4' }}>{drink.detail.원재료}</p>
                                </div>
                            )}
                            {/* Awards */}
                            {drink.detail?.수상내역 && (
                                <div style={{ background: "url('/한지.jpg')", backgroundSize: 'cover', border: '1px solid #d7ccc8', padding: '15px', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                    <h4 style={{ margin: '0 0 8px 0', color: '#5d4037', fontSize: '0.95rem' }}>🏅 수상내역</h4>
                                    <p style={{ margin: 0, fontSize: '0.95rem', color: '#3e2723', lineHeight: '1.4' }}>{drink.detail.수상내역}</p>
                                </div>
                            )}
                            {/* Pairing Food (DB) */}
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
                </div>

                {/* Cocktails Section */}
                {drink.cocktails && drink.cocktails.length > 0 && (
                    <div style={{ marginTop: '10px' }}>
                        <h4 style={{ margin: '0 0 15px 0', color: '#d32f2f', fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            🏆 추천 칵테일
                        </h4>
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
                    </div>
                )}

                {/* Encyclopedia Section */}
                {drink.encyclopedia && drink.encyclopedia.length > 0 && (
                    <div style={{ marginTop: '10px' }}>
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
                    </div>
                )}

                {/* Selling Shops */}
                {drink.selling_shops && drink.selling_shops.length > 0 && (
                    <div style={{ borderTop: '2px solid #f0f0f0', paddingTop: '30px' }}>
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
                    </div>
                )}

                {/* Similar Drinks */}
                {similarDrinks.length > 0 && (
                    <div style={{ borderTop: '2px solid #f0f0f0', paddingTop: '30px' }}>
                        <h3 style={{ fontSize: '1.6rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                            🔍 <span style={{ fontWeight: '800', color: '#333' }}>이런 술은 어떠오?</span>
                        </h3>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '15px' }}>
                            {similarDrinks.map((simDrink, index) => (
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
                    </div>
                )}
            </div>

            {/* RIGHT: AI Sidebar */}
            {onGenerateCocktail && (
                <div style={{ flex: '0 0 320px', minWidth: '320px', position: 'sticky', top: '100px', height: 'fit-content', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{ background: "url('/한지.jpg')", backgroundSize: 'cover', borderRadius: '16px', padding: '25px', border: '1px solid #d7ccc8', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}>
                        <h3 style={{ fontSize: '1.4rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                            🤖 <span style={{ background: 'linear-gradient(120deg, #ff9a9e 0%, #fecfef 100%)', backgroundClip: 'text', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontWeight: '800' }}>AI 추천</span>
                        </h3>

                        {isGeneratingCocktail ? (
                            <div style={{ textAlign: 'center', padding: '30px', background: 'rgba(255,255,255,0.8)', borderRadius: '12px' }}>
                                <div style={{ fontSize: '2rem', marginBottom: '10px' }}>🤖🍹</div>
                                <h4 style={{ fontSize: '1.1rem', color: '#0277bd', marginBottom: '8px' }}>AI가 레시피를 생각 중!</h4>
                                <p style={{ color: '#555', fontSize: '0.9rem' }}>잠시만 기다려주세요...</p>
                            </div>
                        ) : (
                            <>
                                {/* AI Button */}
                                {generatedCocktails.length === 0 && (
                                    <div style={{ textAlign: 'center', padding: '20px', background: 'rgba(255,255,255,0.7)', borderRadius: '12px', marginBottom: '15px' }}>
                                        <p style={{ color: '#666', marginBottom: '15px', fontSize: '0.9rem' }}>
                                            이 술로 만들 수 있는<br />칵테일과 안주를 추천해드려요!
                                        </p>
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
                                            🤖 AI 추천 받기
                                        </button>
                                    </div>
                                )}

                                {/* AI Food Recommendation */}
                                {generatedFood && (
                                    <div style={{ background: "url('/한지흰색.jpg')", backgroundSize: 'cover', border: '1px solid #d7ccc8', padding: '15px', borderRadius: '12px', marginBottom: '15px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                        <h4 style={{ margin: '0 0 8px 0', color: '#e65100', fontSize: '1rem' }}>🍽️ AI 추천 안주</h4>
                                        <span style={{ fontSize: '1.2rem', fontWeight: '700', color: '#bf360c' }}>{generatedFood.name}</span>
                                        <p style={{ margin: '8px 0 0 0', fontSize: '0.85rem', color: '#5d4037', lineHeight: '1.4' }}>{generatedFood.reason}</p>
                                    </div>
                                )}

                                {/* AI Cocktails */}
                                {generatedCocktails.length > 0 && (
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                                        <h4 style={{ margin: 0, color: '#4e342e', fontSize: '1.1rem', fontWeight: '800' }}>🍹 AI 추천 칵테일</h4>
                                        {generatedCocktails.map((cocktail, index) => (
                                            <div key={index} style={{ background: "url('/한지흰색.jpg')", backgroundSize: 'cover', borderRadius: '12px', overflow: 'hidden', border: '1px solid #d7ccc8', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
                                                {cocktail.cocktail_image_url && (
                                                    <div style={{ height: '140px', overflow: 'hidden', position: 'relative' }}>
                                                        <Image src={`/api/image-proxy?url=${encodeURIComponent(cocktail.cocktail_image_url)}`} alt={cocktail.cocktail_title} fill style={{ objectFit: 'cover' }} />
                                                    </div>
                                                )}
                                                <div style={{ padding: '15px' }}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                                        <span style={{ background: '#d7ccc8', color: '#fff', width: '24px', height: '24px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.85rem', fontWeight: 'bold' }}>{index + 1}</span>
                                                        <h5 style={{ margin: '0', fontSize: '1.1rem', fontWeight: '700', color: '#3e2723' }}>{cocktail.cocktail_title}</h5>
                                                    </div>
                                                    <p style={{ fontSize: '0.9rem', color: '#5d4037', margin: 0, lineHeight: '1.5', whiteSpace: 'pre-line' }}>{cocktail.cocktail_recipe}</p>
                                                </div>
                                            </div>
                                        ))}

                                        {/* More Button */}
                                        <button
                                            onClick={() => onGenerateCocktail(drink.name)}
                                            style={{
                                                background: 'rgba(255,255,255,0.7)',
                                                color: '#ff6f00',
                                                border: '2px dashed #ffca28',
                                                padding: '10px',
                                                borderRadius: '12px',
                                                fontSize: '0.9rem',
                                                fontWeight: 'bold',
                                                cursor: 'pointer',
                                                marginTop: '10px'
                                            }}
                                        >
                                            + 더 추천받기
                                        </button>
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
