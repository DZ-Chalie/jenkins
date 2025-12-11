"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useSession, signIn } from "next-auth/react";
import styles from "./page.module.css";
import DrinkDetailCard from "../components/DrinkDetailCard";
import { Upload } from 'lucide-react';


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

interface HansangItem {
    name: string;
    image_url?: string;
    reason: string;
    link_url?: string;
}

interface SearchResult {
    id?: number;
    name: string;
    description: string;
    intro?: string;
    tags: string[];
    image_url?: string;
    url?: string;
    province?: string;
    city?: string;
    detail?: {
        알콜도수?: string;
        용량?: string;
        종류?: string;
        원재료?: string;
        수상내역?: string;
    };
    brewery?: {
        name?: string;
        address?: string;
        homepage?: string;
        contact?: string;
    };
    pairing_food?: string[];
    cocktails?: Cocktail[];

    selling_shops?: {
        shop_id: number;
        name: string;
        address: string;
        contact: string;
        url: string;
        price: number;
    }[];
    encyclopedia?: {
        title: string;
        text: string;
        images?: { src: string; alt: string; }[];
    }[];
    candidates?: {
        name: string;
        score: number;
        image_url: string;
        id?: number;
    }[];
    score: number;
}

function OCRContent() {
    const { data: session } = useSession();
    const router = useRouter();
    const searchParams = useSearchParams();
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [result, setResult] = useState<string>("");
    const [provider, setProvider] = useState<string>("gemini");
    const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
    const [viewState, setViewState] = useState<'input' | 'loading' | 'result'>('input');
    const [isGeneratingCocktail, setIsGeneratingCocktail] = useState<boolean>(false);
    const [generatedFood, setGeneratedFood] = useState<{ name: string, reason: string } | null>(null);
    const [generatedCocktails, setGeneratedCocktails] = useState<Cocktail[]>([]);
    const [autoGenerateAI, setAutoGenerateAI] = useState<boolean>(false);
    const [generatedHansang, setGeneratedHansang] = useState<HansangItem[]>([]);
    const [isGeneratingHansang, setIsGeneratingHansang] = useState<boolean>(false);
    const [isDragging, setIsDragging] = useState<boolean>(false);

    // Handle URL query params for direct search
    useEffect(() => {
        const query = searchParams.get('q');
        if (query) {
            setViewState('loading');
            setGeneratedFood(null);
            setIsGeneratingCocktail(false);
            setGeneratedCocktails([]);
            fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            })
                .then(res => {
                    if (res.ok) return res.json();
                    throw new Error('Search failed');
                })
                .then(data => {
                    setSearchResult(data);
                    setViewState('result');
                    setResult(`Direct search for: ${query}`);

                    // Auto-generate if enabled
                    if (autoGenerateAI) {
                        generateCocktail(data.name);
                    }
                })
                .catch(err => {
                    console.error(err);
                    setViewState('input');
                });
        }
    }, [searchParams, autoGenerateAI]);

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setSelectedImage(file);
            setPreviewUrl(URL.createObjectURL(file));
            setResult("");
            setSearchResult(null);
            setIsGeneratingCocktail(false);
            setGeneratedFood(null);
            setGeneratedCocktails([]);
        }
    };

    // Drag and drop handlers
    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const file = e.dataTransfer.files[0];
            if (file.type.startsWith('image/')) {
                setSelectedImage(file);
                setPreviewUrl(URL.createObjectURL(file));
                setResult("");
                setSearchResult(null);
                setIsGeneratingCocktail(false);
                setGeneratedFood(null);
                setGeneratedCocktails([]);
            }
        }
    };

    const generateCocktail = async (drinkName: string) => {
        setIsGeneratingCocktail(true);
        try {
            // Use /api/python prefix to route through Next.js proxy to backend
            const response = await fetch('/api/python/cocktail/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ drink_name: drinkName }),
            });
            if (response.ok) {
                const data = await response.json();

                // Extract Cocktail Data
                const newCocktail = {
                    cocktail_title: data.cocktail_title,
                    cocktail_base: data.cocktail_base,
                    cocktail_garnish: data.cocktail_garnish,
                    cocktail_recipe: data.cocktail_recipe,
                    cocktail_image_url: data.cocktail_image_url,
                    youtube_video_id: data.youtube_video_id,
                    youtube_video_title: data.youtube_video_title,
                    youtube_thumbnail_url: data.youtube_thumbnail_url
                };

                // Extract Food Data
                if (data.food_pairing_name) {
                    setGeneratedFood({
                        name: data.food_pairing_name,
                        reason: data.food_pairing_reason || ""
                    });
                }

                // Append to generatedCocktails state instead of searchResult
                setGeneratedCocktails(prev => [...prev, newCocktail]);
            }
        } catch (error) {
            console.error("Failed to generate cocktail", error);
        } finally {
            setIsGeneratingCocktail(false);
        }
    };

    const generateHansang = async (province: string, city: string) => {
        setIsGeneratingHansang(true);
        try {
            const response = await fetch('/api/python/hansang/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    drink_name: searchResult?.name || '',
                    province,
                    city,
                    drink_description: searchResult?.description || searchResult?.intro || ''
                }),
            });
            if (response.ok) {
                const data = await response.json();
                setGeneratedHansang(data.items || []);
            } else {
                console.error("Failed to generate hansang:", await response.text());
            }
        } catch (error) {
            console.error("Failed to generate hansang", error);
        } finally {
            setIsGeneratingHansang(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedImage) return;

        setViewState('loading');
        setResult("");
        setSearchResult(null);
        setIsGeneratingCocktail(false);
        setGeneratedFood(null);
        setGeneratedCocktails([]);

        const formData = new FormData();
        formData.append("file", selectedImage);
        formData.append("provider", provider);

        try {
            // Minimum loading time of 2 seconds to show the video
            const minLoadingTime = new Promise(resolve => setTimeout(resolve, 2000));
            // Use relative path to leverage Next.js rewrites (proxy)
            // This avoids Mixed Content errors (HTTPS frontend -> HTTP backend)
            const apiRequest = fetch(`/api/python/ocr/analyze`, {
                method: "POST",
                body: formData,
            });

            const [_, response] = await Promise.all([minLoadingTime, apiRequest]);
            const data = await response.json();

            if (response.ok) {
                setResult(data.text);
                if (data.search_result) {
                    setSearchResult(data.search_result);
                    // Check if cocktails exist, if not, generate one if auto-generation is enabled
                    if (autoGenerateAI && (!data.search_result.cocktails || data.search_result.cocktails.length === 0)) {
                        generateCocktail(data.search_result.name);
                    }
                }
                setViewState('result');
            } else {
                setResult(`Error: ${data.detail}`);
                setViewState('result'); // Show error in result view
            }
        } catch (error) {
            setResult("Error: Failed to connect to server");
            setViewState('result');
        }
    };

    const handleRetry = () => {
        setViewState('input');
        setSelectedImage(null);
        setPreviewUrl(null);
        setResult("");
        setSearchResult(null);
        setIsGeneratingCocktail(false);
        setGeneratedFood(null);
        setGeneratedHansang([]);
        setIsGeneratingHansang(false);
        setGeneratedCocktails([]);
    };

    return (
        <div className={styles.container} style={{

            backgroundImage: "linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('/background.png')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundAttachment: 'fixed',
            minHeight: '100vh'
        }}>
            {viewState === 'loading' && (
                <div className={styles.loadingContainer}>
                    <video autoPlay loop muted playsInline className={styles.loadingVideo}>
                        <source src="/jumo.mp4" type="video/mp4" />
                        Your browser does not support the video tag.
                    </video>
                    <p className={styles.loadingText}>주모가 술을 감별중입니다...</p>
                </div>
            )}

            {viewState === 'input' && (
                <>
                    <h1 className={styles.title}>전통주 라벨 인식</h1>
                    <p className={styles.description}>
                        전통주 라벨 사진을 업로드하면 AI가 어떤 술인지 알려드려요!
                    </p>

                    {/* OCR Toggle Buttons */}
                    <div className={styles.ocrToggleContainer}>
                        <button
                            className={`${styles.ocrToggleButton} ${provider === 'gemini' ? styles.active : ''}`}
                            onClick={() => setProvider('gemini')}
                        >
                            Gemini Vision
                        </button>
                        <button
                            className={`${styles.ocrToggleButton} ${provider === 'clova' ? styles.active : ''}`}
                            onClick={() => setProvider('clova')}
                        >
                            Clova OCR
                        </button>
                    </div>

                    {/* AI Auto-Generation Toggle */}
                    <div style={{ marginBottom: "20px", textAlign: "center" }}>
                        <label style={{ display: "inline-flex", alignItems: "center", cursor: "pointer", background: "url('/한지.jpg')", backgroundSize: "cover", padding: "10px 20px", borderRadius: "30px", boxShadow: "0 2px 5px rgba(0,0,0,0.1)", border: "1px solid #d7ccc8" }}>
                            <span style={{ marginRight: "10px", fontWeight: "bold", color: "#333" }}>🤖 AI 자동 추천</span>
                            <div style={{ position: "relative", width: "50px", height: "26px", background: autoGenerateAI ? "#4caf50" : "#ccc", borderRadius: "13px", transition: "background 0.3s" }}>
                                <div style={{ position: "absolute", top: "3px", left: autoGenerateAI ? "27px" : "3px", width: "20px", height: "20px", background: "white", borderRadius: "50%", transition: "left 0.3s", boxShadow: "0 1px 3px rgba(0,0,0,0.2)" }}></div>
                            </div>
                            <input type="checkbox" checked={autoGenerateAI} onChange={(e) => setAutoGenerateAI(e.target.checked)} style={{ display: "none" }} />
                        </label>
                    </div>

                    <form onSubmit={handleSubmit} className={styles.form}>
                        <div
                            className={`${styles.uploadBox} ${isDragging ? styles.dragging : ''}`}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                        >
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleImageChange}
                                id="imageUpload"
                                className={styles.fileInput}
                            />
                            <label htmlFor="imageUpload" className={styles.uploadLabel}>
                                {previewUrl ? (
                                    <img src={previewUrl} alt="Preview" className={styles.previewImage} />
                                ) : (
                                    <div className={styles.placeholder}>
                                        <Upload size={60} strokeWidth={1.5} color="#5d4037" />
                                        <span style={{ color: '#5d4037', fontWeight: 'bold', marginTop: '12px' }}>사진 업로드 또는 드래그</span>
                                    </div>
                                )}
                            </label>
                        </div>

                        <button
                            type="submit"
                            className={styles.submitButton}
                            disabled={!selectedImage}
                        >
                            분석하기
                        </button>
                    </form>
                </>
            )}

            {viewState === 'result' && (
                <div className={styles.resultContainer} style={{ maxWidth: '100%', width: '98%', margin: '0 auto', padding: '0 20px', position: 'relative' }}>
                    <h1 className={styles.title}>분석 결과</h1>

                    {/* Blur overlay when not logged in */}
                    {!session && (
                        <div className={styles.authOverlay}>
                            <div className={styles.authCard}>
                                <div className={styles.authIcon}>🔒</div>
                                <h2 className={styles.authTitle}>로그인이 필요한 서비스입니다</h2>
                                <p className={styles.authDescription}>
                                    OCR 분석 결과를 보려면 로그인해야 합니다
                                </p>
                                <button
                                    className={styles.authButton}
                                    onClick={() => signIn("cognito", { callbackUrl: "/ocr" })}
                                >
                                    로그인하기
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Blurred content */}
                    <div className={!session ? styles.blurredContent : ''}>
                        {searchResult ? (
                            <>
                                <DrinkDetailCard
                                    drink={searchResult}
                                    isOCR={true}
                                    onGenerateCocktail={generateCocktail}
                                    generatedFood={generatedFood}
                                    generatedCocktails={generatedCocktails}
                                    isGeneratingCocktail={isGeneratingCocktail}
                                    onGenerateHansang={generateHansang}
                                    generatedHansang={generatedHansang}
                                    isGeneratingHansang={isGeneratingHansang}
                                />

                                <div className={styles.rawTextSection}>
                                    <details>
                                        <summary>OCR 인식 텍스트 보기</summary>
                                        <pre className={styles.rawText}>{result}</pre>
                                    </details>
                                </div>
                            </>
                        ) : (
                            <div className={styles.noMatch}>
                                <h3>일치하는 술을 찾지 못했습니다.</h3>
                                <p>인식된 텍스트:</p>
                                <pre>{result}</pre>
                            </div>
                        )}
                    </div>

                    <button onClick={handleRetry} className={styles.retryButton} style={{ marginTop: '40px', padding: '15px 40px', fontSize: '1.3rem' }}>
                        다른 술 분석하기
                    </button>
                </div>
            )}
        </div>
    );
}

export default function OCRPage() {
    return (
        <Suspense fallback={
            <div className={styles.loadingContainer}>
                <p className={styles.loadingText}>Loading...</p>
            </div>
        }>
            <OCRContent />
        </Suspense>
    );
}
