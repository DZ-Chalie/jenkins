"use client";

import Link from "next/link";
import { signIn, signOut, useSession } from "next-auth/react";
import RealTimeSearchRanking from "./RealTimeSearchRanking";
import styles from "./Header.module.css";

export default function Header() {
    const { data: session } = useSession();

    const handleSignOut = async () => {
        // Get Cognito configuration
        const cognitoDomain = process.env.NEXT_PUBLIC_COGNITO_DOMAIN;
        const clientId = process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID;
        const logoutRedirectUri = window.location.origin;

        // Sign out from NextAuth first
        await signOut({ redirect: false });

        // Then redirect to Cognito logout to clear Cognito session
        if (cognitoDomain && clientId) {
            // Construct Cognito logout URL
            const logoutUrl = `${cognitoDomain}/logout?client_id=${clientId}&logout_uri=${encodeURIComponent(logoutRedirectUri)}`;
            window.location.href = logoutUrl;
        } else {
            // Fallback if env vars not set
            window.location.replace("/");
        }
    };

    return (
        <header className={styles.header}>
            <Link href="/" className={styles.logoSection}>
                {/* Placeholder for Logo */}
                <div style={{ width: 40, height: 40, background: "white", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", color: "black", fontSize: "0.8rem" }}>
                    Logo
                </div>
                <span>JUMAK</span>
            </Link>

            <nav className={styles.nav}>
                <Link href="/ocr" className={styles.navLink}>
                    이미지로 전통주 찾기
                </Link>
                <Link href="/info" className={styles.navLink}>
                    전통주 정보 찾기
                </Link>
                <Link href="/board" className={styles.navLink}>
                    커뮤니티
                </Link>
                {session && (
                    <Link href="/mypage" className={styles.navLink}>
                        마이페이지
                    </Link>
                )}
            </nav>

            <div className={styles.authSection}>
                <RealTimeSearchRanking />
                {session ? (
                    <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                        <span style={{ fontSize: "0.9rem" }}>{session.user?.name}님</span>
                        <button
                            className={styles.loginButton}
                            onClick={handleSignOut}
                        >
                            로그아웃
                        </button>
                    </div>
                ) : (
                    <button
                        className={styles.loginButton}
                        onClick={() => signIn("cognito", { callbackUrl: "/" })}
                    >
                        로그인
                    </button>
                )}
            </div>
        </header>
    );
}
