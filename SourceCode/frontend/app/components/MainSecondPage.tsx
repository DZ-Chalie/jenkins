"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { Swiper, SwiperSlide } from 'swiper/react';
import { EffectCoverflow, Pagination, Autoplay } from 'swiper/modules';

// Import Swiper styles
import 'swiper/css';
import 'swiper/css/effect-coverflow';
import 'swiper/css/pagination';

interface Cocktail {
    cocktail_id: number;
    cocktail_title: string;
    cocktail_image_url?: string;
    cocktail_homepage_url?: string;
}

interface Fair {
    fair_id: number;
    fair_year: number;
    fair_image_url: string;
    fair_homepage_url: string;
}

export default function MainSecondPage() {
    const [cocktails, setCocktails] = useState<Cocktail[]>([]);
    const [fairs, setFairs] = useState<Fair[]>([]);
    const [loading, setLoading] = useState(false);

    // Fetch initial random cocktails
    const fetchCocktails = async () => {
        if (loading) return;
        setLoading(true);
        try {
            const res = await fetch("/api/python/cocktail/random?limit=10");
            const data = await res.json();
            setCocktails(data);
        } catch (error) {
            console.error("Failed to fetch cocktails:", error);
        } finally {
            setLoading(false);
        }
    };

    // Hardcoded Fair Data using local images
    const hardcodedFairs: Fair[] = [
        {
            fair_id: 1,
            fair_year: 2024,
            fair_image_url: "/sool_award/2024품평회.PNG",
            fair_homepage_url: "https://thesool.com/front/publication/M000000090/view.do?bbsId=A000000050&publicationId=C000003159&page=&searchKey=&searchString=&searchCategory="
        },
        {
            fair_id: 2,
            fair_year: 2023,
            fair_image_url: "/sool_award/2023.PNG",
            fair_homepage_url: "https://thesool.com/front/publication/M000000090/view.do?bbsId=A000000050&publicationId=C000002964&page=&searchKey=&searchString=&searchCategory="
        },
        {
            fair_id: 3,
            fair_year: 2022,
            fair_image_url: "/sool_award/2022.PNG",
            fair_homepage_url: "https://thesool.com/front/publication/M000000090/view.do?bbsId=A000000050&publicationId=C000002724&page=&searchKey=&searchString=&searchCategory="
        }
    ];

    // Initialize fairs with hardcoded data and fetch cocktails
    useEffect(() => {
        setFairs(hardcodedFairs);
        fetchCocktails();
    }, []);

    return (
        <>
            {/* Override Swiper pagination styles - dots right below cards */}
            <style jsx global>{`
                .mySwiper .swiper-pagination {
                    position: relative !important;
                    bottom: 0 !important;
                    margin-top: 0px !important;
                }
                .mySwiper .swiper-pagination-bullet {
                    background: #888 !important;
                    opacity: 0.5;
                }
                .mySwiper .swiper-pagination-bullet-active {
                    background: #d4a574 !important;
                    opacity: 1;
                }
            `}</style>
            <div style={{
                height: '100%',
                width: '100%',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                padding: '95px 0 10px 0',
                boxSizing: 'border-box'
            }}>
                {/* Section 1: Today's Cocktail Recommendation (Carousel) */}
                <div style={{ flex: '1.4', minHeight: '0', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    <h2 style={{ fontSize: '1.4rem', fontWeight: '800', margin: '0 0 8px 40px', color: '#333' }}>
                        오늘의 칵테일 추천 🍸
                    </h2>

                    <div style={{ width: '100%', height: '100%' }}>
                        {cocktails.length > 0 && (
                            <Swiper
                                key={cocktails.length}
                                effect={'coverflow'}
                                grabCursor={true}
                                centeredSlides={true}
                                loop={true}
                                slidesPerView={5}
                                initialSlide={2}
                                coverflowEffect={{
                                    rotate: 0,
                                    stretch: 0,
                                    depth: 150,
                                    modifier: 2,
                                    slideShadows: false,
                                }}
                                pagination={{ clickable: true }}
                                autoplay={{ delay: 3000, disableOnInteraction: false }}
                                modules={[EffectCoverflow, Pagination, Autoplay]}
                                className="mySwiper"
                                style={{ width: '100%', height: '100%', paddingBottom: '0px' }}
                            >
                                {cocktails.map((cocktail, idx) => (
                                    <SwiperSlide key={`${cocktail.cocktail_id}-${idx}`} style={{
                                        backgroundPosition: 'center',
                                        backgroundSize: 'cover',
                                        width: '100%',
                                        height: '380px',
                                        borderRadius: '16px',
                                        overflow: 'hidden',
                                        boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
                                        background: '#fff'
                                    }}>
                                        <div
                                            onClick={() => {
                                                if (cocktail.cocktail_homepage_url) window.open(cocktail.cocktail_homepage_url, '_blank');
                                            }}
                                            style={{ width: '100%', height: '100%', position: 'relative', cursor: 'pointer' }}
                                        >
                                            {cocktail.cocktail_image_url ? (
                                                <Image
                                                    src={`/api/image-proxy?url=${encodeURIComponent(cocktail.cocktail_image_url)}`}
                                                    alt={cocktail.cocktail_title}
                                                    fill
                                                    unoptimized
                                                    style={{ objectFit: 'cover' }}
                                                    onError={(e) => {
                                                        const target = e.currentTarget;
                                                        target.style.display = 'none';
                                                        if (target.parentElement) {
                                                            target.parentElement.style.background = '#f5f5f5';
                                                            target.parentElement.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#aaa;flex-direction:column;gap:10px"><span style="font-size:30px">🍹</span><span>이미지 없음</span></div>';
                                                        }
                                                    }}
                                                />
                                            ) : (
                                                <div style={{ width: '100%', height: '100%', background: '#eee', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '10px' }}>
                                                    <span style={{ fontSize: '30px' }}>🍹</span>
                                                    <span style={{ color: '#aaa' }}>이미지 없음</span>
                                                </div>
                                            )}
                                            <div style={{
                                                position: 'absolute', bottom: 0, left: 0, right: 0,
                                                background: 'linear-gradient(to top, rgba(0,0,0,0.85), transparent)',
                                                padding: '12px 15px', color: '#fff',
                                                display: 'flex', flexDirection: 'column', gap: '3px'
                                            }}>
                                                <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: '700', textShadow: '0 1px 3px rgba(0,0,0,0.5)' }}>{cocktail.cocktail_title}</h3>
                                                <span style={{ fontSize: '0.75rem', opacity: 0.9 }}>자세히 보기 →</span>
                                            </div>
                                        </div>
                                    </SwiperSlide>
                                ))}
                            </Swiper>
                        )}
                    </div>
                </div>

                {/* Section 2: Fair Info - Portrait Image Gallery */}
                <div style={{
                    flex: '1.3',
                    minHeight: '0',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundImage: 'url(/한지.jpg)',
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    padding: '10px 20px',
                    borderRadius: '25px 25px 0 0',
                    boxShadow: '0 -8px 25px rgba(0,0,0,0.08)'
                }}>
                    <h2 style={{
                        fontSize: '1.3rem',
                        fontWeight: '800',
                        margin: '0 0 0px 0',
                        color: '#4a3728',
                        textAlign: 'center',
                        letterSpacing: '0.5px',
                        textShadow: '0 1px 2px rgba(255,255,255,0.8)'
                    }}>
                        🍶 우리술 품평회 수상작
                    </h2>

                    <div style={{
                        display: 'flex',
                        gap: '10px',
                        justifyContent: 'center',
                        alignItems: 'center',
                        width: '100%',
                        maxWidth: '900px',
                        height: '100%'
                    }}>
                        {fairs.map((fair) => (
                            <div key={fair.fair_id}
                                onClick={() => {
                                    if (fair.fair_homepage_url) window.open(fair.fair_homepage_url, '_blank');
                                }}
                                style={{
                                    flex: '0 0 auto',
                                    width: '220px',
                                    height: '270px',
                                    cursor: 'pointer',
                                    borderRadius: '12px',
                                    overflow: 'hidden',
                                    boxShadow: '0 6px 20px rgba(0,0,0,0.15)',
                                    background: '#fff',
                                    position: 'relative',
                                    border: '3px solid rgba(212,165,116,0.3)',
                                    transition: 'transform 0.3s, box-shadow 0.3s'
                                }}
                                onMouseOver={e => {
                                    e.currentTarget.style.transform = 'translateY(-6px) scale(1.03)';
                                    e.currentTarget.style.boxShadow = '0 12px 35px rgba(0,0,0,0.25)';
                                }}
                                onMouseOut={e => {
                                    e.currentTarget.style.transform = 'translateY(0) scale(1)';
                                    e.currentTarget.style.boxShadow = '0 6px 20px rgba(0,0,0,0.15)';
                                }}
                            >
                                <Image
                                    src={fair.fair_image_url}
                                    alt={`${fair.fair_year} 우리술 품평회`}
                                    fill
                                    sizes="180px"
                                    style={{ objectFit: 'contain', padding: '8px' }}
                                />
                                {/* Year badge */}
                                <div style={{
                                    position: 'absolute', bottom: '10px', left: '50%', transform: 'translateX(-50%)',
                                    background: 'linear-gradient(135deg, #d4a574, #c49a6c)',
                                    padding: '5px 15px', borderRadius: '15px',
                                    fontWeight: '800', color: '#fff', fontSize: '0.9rem',
                                    boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
                                }}>
                                    {fair.fair_year}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    );
}
