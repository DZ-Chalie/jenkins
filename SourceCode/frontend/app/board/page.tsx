"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import styles from "./board.module.css";

interface FlavorProfile {
    sweet: number;
    sour: number;
    body: number;
    scent: number;
    throat: number;
}

interface TastingNote {
    _id: string;
    liquor_id: number;
    liquor_name: string;
    rating: number;
    flavor_profile: FlavorProfile;
    content: string;
    tags: string[];
    images: string[];
    created_at: string;
    user_id: string;
    author_name?: string;
}

export default function BoardPage() {
    const [posts, setPosts] = useState<TastingNote[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchPosts();
    }, []);

    const fetchPosts = async () => {
        try {
            // Fetch from the new Public Notes endpoint
            const response = await fetch(`/api/python/notes`);
            if (response.ok) {
                const data = await response.json();
                setPosts(data);
            } else {
                console.error("Failed to fetch posts");
            }
        } catch (error) {
            console.error("Error fetching posts:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className={styles.container}>
                <div className={styles.background}>
                    <Image
                        src="/jumak.jpg"
                        alt="Background"
                        fill
                        style={{ objectFit: "cover" }}
                        priority
                    />
                    <div className={styles.overlay} />
                </div>
                <div className={styles.contentWrapper} style={{ textAlign: "center", paddingTop: "100px" }}>
                    Loading Community... 🍶
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.background}>
                <Image
                    src="/jumak.jpg"
                    alt="Background"
                    fill
                    style={{ objectFit: "cover" }}
                    priority
                />
                <div className={styles.overlay} />
            </div>

            <div className={styles.contentWrapper}>
                <div className={styles.header}>
                    <h1 className={styles.title}>🍶 전통주 시음 노트</h1>
                    <Link href="/board/write" className={styles.writeButton}>
                        + 노트 작성하기
                    </Link>
                </div>

                <div className={styles.grid}>
                    {posts.length === 0 ? (
                        <div style={{ gridColumn: "1/-1", textAlign: "center", padding: "40px", color: "#666" }}>
                            아직 등록된 시음 노트가 없습니다. 첫 번째 후기를 남겨주세요!
                        </div>
                    ) : (
                        posts.map((post) => (
                            <div key={post._id} className={styles.card}>
                                <h2 className={styles.cardTitle}>{post.liquor_name}</h2>
                                <div className={styles.cardMeta}>
                                    <span>{new Date(post.created_at).toLocaleDateString()}</span>
                                    <span>👤 {post.author_name || "익명"}</span>
                                    <span>⭐ {post.rating}</span>
                                </div>

                                <div className={styles.chartContainer}>
                                    {post.images && post.images.length > 0 && (
                                        <div style={{ marginBottom: 15 }}>
                                            <img
                                                src={post.images[0]}
                                                alt={post.liquor_name}
                                                style={{ width: '100%', height: '200px', objectFit: 'cover', borderRadius: '8px' }}
                                            />
                                        </div>
                                    )}
                                    <div style={{ width: '100%', height: 200 }}>
                                        <ResponsiveContainer>
                                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={[
                                                { subject: '단맛', A: post.flavor_profile.sweet, fullMark: 5 },
                                                { subject: '신맛', A: post.flavor_profile.sour, fullMark: 5 },
                                                { subject: '바디', A: post.flavor_profile.body, fullMark: 5 },
                                                { subject: '향', A: post.flavor_profile.scent, fullMark: 5 },
                                                { subject: '목넘김', A: post.flavor_profile.throat, fullMark: 5 },
                                            ]}>
                                                <PolarGrid />
                                                <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10 }} />
                                                <PolarRadiusAxis angle={30} domain={[0, 5]} tick={false} axisLine={false} />
                                                <Radar name="맛" dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                                            </RadarChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>

                                <p className={styles.cardContent}>{post.content}</p>
                                <div className={styles.tags}>
                                    {post.tags.map((tag, idx) => (
                                        <span key={idx} className={styles.tag}>{tag}</span>
                                    ))}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
