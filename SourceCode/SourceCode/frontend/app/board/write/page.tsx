"use client";

import { useSession } from "next-auth/react";
import { useState, useEffect, Suspense, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import styles from "./page.module.css";

function WriteForm() {
    const { data: session, status } = useSession();
    const router = useRouter();
    const searchParams = useSearchParams();
    const editId = searchParams.get("edit");

    // Search State
    const [searchQuery, setSearchQuery] = useState("");
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [showDropdown, setShowDropdown] = useState(false);
    const searchTimeout = useRef<NodeJS.Timeout | null>(null);

    const [formData, setFormData] = useState({
        liquor_id: 999, // Default dummy
        liquor_name: "",
        image_url: "",
        content: "",
        rating: 5,
        sweet: 3,
        sour: 3,
        body: 3,
        scent: 3,
        throat: 3
    });

    useEffect(() => {
        if (status === "unauthenticated") {
            alert("로그인이 필요한 서비스입니다.");
            router.push("/board");
        }
    }, [status, router]);

    // Fetch existing note if editing
    useEffect(() => {
        if (editId && session?.user) {
            const userId = (session.user as any).id || session.user.email;
            fetch(`/api/python/notes/user/${userId}`)
                .then(res => res.json())
                .then(notes => {
                    const note = notes.find((n: any) => n._id === editId);
                    if (note) {
                        setFormData({
                            liquor_id: note.liquor_id,
                            liquor_name: note.liquor_name,
                            image_url: note.images?.[0] || "",
                            content: note.content,
                            rating: note.rating,
                            sweet: note.flavor_profile.sweet,
                            sour: note.flavor_profile.sour,
                            body: note.flavor_profile.body,
                            scent: note.flavor_profile.scent,
                            throat: note.flavor_profile.throat
                        });
                        setSearchQuery(note.liquor_name); // Pre-fill search
                    }
                });
        }
    }, [editId, session]);

    // Search Logic with Debounce
    const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const query = e.target.value;
        setSearchQuery(query);
        setFormData(prev => ({ ...prev, liquor_name: query }));

        if (searchTimeout.current) clearTimeout(searchTimeout.current);

        if (query.length > 1) {
            searchTimeout.current = setTimeout(async () => {
                try {
                    const res = await fetch("/api/python/search", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ query })
                    });
                    if (res.ok) {
                        const data = await res.json();
                        // Search API returns a single "best match" object with "candidates" list inside
                        // We primarily use candidates for dropdown
                        if (data && data.candidates) {
                            setSearchResults(data.candidates);
                            setShowDropdown(true);
                        } else if (data) {
                            // Only one result found
                            setSearchResults([{
                                name: data.name,
                                id: 999, // Search endpoint might not return ID in top level? Check schema.
                                image_url: data.image_url
                            }]);
                            setShowDropdown(true);
                        }
                    }
                } catch (err) {
                    console.error("Search failed", err);
                }
            }, 300); // 300ms debounce
        } else {
            setShowDropdown(false);
        }
    };

    const selectLiquor = (liquor: any) => {
        setFormData(prev => ({
            ...prev,
            liquor_name: liquor.name,
            liquor_id: liquor.id || 999,
            image_url: liquor.image_url || ""
        }));
        setSearchQuery(liquor.name);
        setShowDropdown(false);
    };

    const handleStarClick = (rating: number) => {
        setFormData(prev => ({ ...prev, rating }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!session?.user) return;
        const userId = (session.user as any).id || session.user.email;
        const authorName = session.user.name || (session.user as any).nickname || "익명";

        const payload = {
            user_id: userId,
            author_name: authorName,
            liquor_id: formData.liquor_id,
            liquor_name: formData.liquor_name,
            rating: formData.rating,
            flavor_profile: {
                sweet: formData.sweet,
                sour: formData.sour,
                body: formData.body,
                scent: formData.scent,
                throat: formData.throat
            },
            content: formData.content,
            tags: [],
            images: formData.image_url ? [formData.image_url] : [], // Save image
            is_public: true
        };

        try {
            const url = editId ? `/api/python/notes/${editId}` : "/api/python/notes";
            const method = editId ? "PUT" : "POST";

            const res = await fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                alert(editId ? "수정되었습니다!" : "시음 노트가 등록되었습니다!");
                router.push(editId ? "/mypage" : "/board");
            } else {
                alert("작업에 실패했습니다.");
            }
        } catch (error) {
            console.error("Failed to save note:", error);
            alert("오류가 발생했습니다.");
        }
    };

    if (status === "loading") return <div>Loading...</div>;

    return (
        <div className={styles.container}>
            <h1 className={styles.title}>{editId ? "시음 노트 수정" : "시음 노트 작성"}</h1>

            <div className={styles.formCard}>
                <form onSubmit={handleSubmit}>
                    {/* Liquor Search with Autocomplete */}
                    <div className={styles.formGroup} style={{ position: 'relative' }}>
                        <label className={styles.label}>술 이름</label>
                        <input
                            className={styles.input}
                            value={searchQuery}
                            onChange={handleSearchChange}
                            placeholder="술 이름을 입력하면 리스트가 나옵니다"
                            required
                        />
                        {showDropdown && searchResults.length > 0 && (
                            <ul className={styles.autocompleteDropdown}>
                                {searchResults.map((item, idx) => (
                                    <li key={idx} onClick={() => selectLiquor(item)} className={styles.autocompleteItem}>
                                        {item.image_url ? (
                                            <img src={item.image_url} alt="" style={{ width: 30, height: 30, marginRight: 10, borderRadius: 4, objectFit: 'cover' }} />
                                        ) : (
                                            <span style={{ width: 30, height: 30, marginRight: 10, borderRadius: 4, background: '#eee', display: 'inline-block' }} />
                                        )}
                                        <span>{item.name}</span>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>

                    {/* Image Preview */}
                    {formData.image_url && (
                        <div className={styles.previewContainer} style={{ marginBottom: 20, textAlign: 'center' }}>
                            <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: 5 }}>선택된 술</p>
                            <img
                                src={formData.image_url}
                                alt="Liquor Preview"
                                style={{ maxHeight: 200, borderRadius: 8, boxShadow: '0 4px 10px rgba(0,0,0,0.1)' }}
                            />
                        </div>
                    )}

                    {/* Star Rating */}
                    <div className={styles.formGroup}>
                        <label className={styles.label}>별점 (Click)</label>
                        <div className={styles.starRating}>
                            {[1, 2, 3, 4, 5].map((star) => (
                                <span
                                    key={star}
                                    onClick={() => handleStarClick(star)}
                                    style={{
                                        cursor: 'pointer',
                                        fontSize: '2rem',
                                        color: star <= formData.rating ? '#FFD700' : '#ddd',
                                        transition: 'color 0.2s'
                                    }}
                                >
                                    ★
                                </span>
                            ))}
                            <span style={{ marginLeft: 10, fontSize: '1.2rem', color: '#555', fontWeight: 'bold' }}>
                                {formData.rating}점
                            </span>
                        </div>
                    </div>

                    <div className={styles.formGroup}>
                        <label className={styles.label}>맛 평가 (1-5)</label>
                        <div className={styles.sliderGroup}>
                            {['sweet', 'sour', 'body', 'scent', 'throat'].map((attr) => (
                                <div key={attr} className={styles.sliderContainer}>
                                    <span className={styles.sliderLabel}>
                                        {attr === 'sweet' ? '단맛' :
                                            attr === 'sour' ? '신맛' :
                                                attr === 'body' ? '바디' :
                                                    attr === 'scent' ? '향' : '목넘김'}
                                    </span>
                                    <input
                                        type="range"
                                        min="1" max="5"
                                        className={styles.slider}
                                        value={(formData as any)[attr]}
                                        onChange={e => setFormData({ ...formData, [attr]: parseInt(e.target.value) })}
                                    />
                                    <span className={styles.sliderValue}>{(formData as any)[attr]}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className={styles.formGroup}>
                        <label className={styles.label}>한줄 평</label>
                        <textarea
                            className={styles.textarea}
                            value={formData.content}
                            onChange={e => setFormData({ ...formData, content: e.target.value })}
                            placeholder="맛과 향, 그리고 분위기는 어땠나요?"
                            required
                        />
                    </div>

                    <button type="submit" className={styles.submitButton}>
                        {editId ? "수정 완료" : "커뮤니티에 등록하기"}
                    </button>
                </form>
            </div>
        </div>
    );
}

export default function WritePage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <WriteForm />
        </Suspense>
    );
}
