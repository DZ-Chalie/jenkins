"use client";

import { useSession } from "next-auth/react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import styles from "./page.module.css";
import Link from "next/link"; // Import Link for navigation

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
    created_at: string;
}

export default function MyPage() {
    const { data: session, status } = useSession();
    const router = useRouter();
    const [notes, setNotes] = useState<TastingNote[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (status === "unauthenticated") {
            router.push("/");
        } else if (session?.user) {
            // TS safe access
            const user = session.user as any;
            const userId = user.id || user.email;
            if (userId) fetchNotes(userId);
        }
    }, [status, session]);

    const fetchNotes = async (userId: string) => {
        try {
            const res = await fetch(`/api/python/notes/user/${userId}`);
            if (res.ok) {
                const data = await res.json();
                setNotes(data);
            }
        } catch (error) {
            console.error("Failed to fetch notes:", error);
        } finally {
            setLoading(false);
        }
    };

    if (status === "loading" || loading) {
        return <div className={styles.container}>Loading...</div>;
    }

    if (!session) {
        return null;
    }

    return (
        <div className={styles.container}>
            {/* Profile Header */}
            <div className={styles.profileSection}>
                <div className={styles.avatar}>
                    {session.user?.name?.[0] || "U"}
                </div>
                <div className={styles.profileInfo}>
                    <h1>{session.user?.name}님의 술장</h1>
                    <p>{session.user?.email}</p>
                    <p>작성한 시음 노트: <strong>{notes.length}</strong>개</p>
                </div>
            </div>

            {/* Tasting Notes Section */}
            <div className={styles.sectionTitle}>
                <h2>🍶 나의 기록 모아보기</h2>
                {/* Removed Write Button */}
                <Link href="/board/write" style={{ fontSize: '0.9rem', color: '#666', textDecoration: 'none' }}>
                    + 새 글 쓰러 가기
                </Link>
            </div>

            {notes.length === 0 ? (
                <div className={styles.emptyState}>
                    <p>아직 작성된 시음 노트가 없습니다.</p>
                    <Link href="/board/write" style={{ color: '#333', fontWeight: 'bold' }}>
                        첫 번째 기록 남기기
                    </Link>
                </div>
            ) : (
                <div className={styles.notesGrid}>
                    {notes.map((note) => (
                        <div key={note._id} className={styles.noteCard}>
                            <h3 className={styles.liquorName}>{note.liquor_name}</h3>
                            <div className={styles.chartContainer}>
                                <div style={{ width: '100%', height: 200 }}>
                                    <ResponsiveContainer>
                                        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={[
                                            { subject: '단맛', A: note.flavor_profile.sweet, fullMark: 5 },
                                            { subject: '신맛', A: note.flavor_profile.sour, fullMark: 5 },
                                            { subject: '바디', A: note.flavor_profile.body, fullMark: 5 },
                                            { subject: '향', A: note.flavor_profile.scent, fullMark: 5 },
                                            { subject: '목넘김', A: note.flavor_profile.throat, fullMark: 5 },
                                        ]}>
                                            <PolarGrid />
                                            <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
                                            <PolarRadiusAxis angle={30} domain={[0, 5]} tick={false} axisLine={false} />
                                            <Radar name="맛" dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                                        </RadarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                            <p className={styles.noteContent}>{note.content}</p>
                            <div className={styles.tags}>
                                <span className={styles.tag}>⭐ {note.rating}</span>
                                {note.tags.map(tag => <span key={tag} className={styles.tag}>{tag}</span>)}
                            </div>
                            <div className={styles.actions} style={{ marginTop: '15px', display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        router.push(`/board/write?edit=${note._id}`);
                                    }}
                                    style={{ padding: '5px 10px', fontSize: '0.8rem', cursor: 'pointer', background: '#f0f0f0', border: 'none', borderRadius: '4px' }}
                                >
                                    수정
                                </button>
                                <button
                                    onClick={async (e) => {
                                        e.stopPropagation();
                                        if (confirm("정말 삭제하시겠습니까?")) {
                                            try {
                                                const res = await fetch(`/api/python/notes/${note._id}`, { method: 'DELETE' });
                                                if (res.ok) {
                                                    alert("삭제되었습니다.");
                                                    fetchNotes((session?.user as any).id || session?.user?.email);
                                                } else {
                                                    alert("삭제 실패");
                                                }
                                            } catch (err) {
                                                console.error(err);
                                            }
                                        }
                                    }}
                                    style={{ padding: '5px 10px', fontSize: '0.8rem', cursor: 'pointer', background: '#ffeeee', color: 'red', border: 'none', borderRadius: '4px' }}
                                >
                                    삭제
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
