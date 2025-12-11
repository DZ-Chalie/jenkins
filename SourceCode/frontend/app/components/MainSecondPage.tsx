"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import styles from './MainSecondPage.module.css';

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
        <div className={styles.container}>
            {/* Left: Cocktail List (Text Only) */}
            <div className={styles.leftSection}>
                <h2 className={styles.sectionTitle}>
                    <span className={styles.titleIcon}>🍸</span>
                    오늘의 칵테일 추천
                </h2>

                <div className={styles.cocktailList}>
                    {cocktails.slice(0, 8).map((cocktail, idx) => (
                        <div
                            key={cocktail.cocktail_id}
                            className={styles.cocktailItem}
                            onClick={() => {
                                if (cocktail.cocktail_homepage_url) {
                                    window.open(cocktail.cocktail_homepage_url, '_blank');
                                }
                            }}
                        >
                            <div className={styles.cocktailNumber}>{idx + 1}</div>
                            <div className={styles.cocktailName}>{cocktail.cocktail_title}</div>
                            <div className={styles.cocktailArrow}>→</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Right: Award Winners (Vertical Scroll) */}
            <div className={styles.rightSection}>
                <h2 className={styles.sectionTitle}>
                    <span className={styles.titleIcon}>🏆</span>
                    우리술 품평회 수상작
                </h2>

                <div className={styles.awardList}>
                    {fairs.map((fair) => (
                        <div
                            key={fair.fair_id}
                            className={styles.awardItem}
                            onClick={() => {
                                if (fair.fair_homepage_url) {
                                    window.open(fair.fair_homepage_url, '_blank');
                                }
                            }}
                        >
                            <div className={styles.awardImageWrapper}>
                                <Image
                                    src={fair.fair_image_url}
                                    alt={`${fair.fair_year} 우리술 품평회`}
                                    fill
                                    sizes="300px"
                                    style={{ objectFit: 'contain', padding: '10px' }}
                                />
                            </div>
                            <div className={styles.awardYear}>{fair.fair_year}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
