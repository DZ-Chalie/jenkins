"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import styles from "./WeatherBanner.module.css";

interface WeatherData {
    city: string;
    temperature: number;
    weather: string;
    message: string;
    keyword: string;
    liquors: any[];
}

interface WeatherBannerProps {
    onRecommendationUpdate: (data: WeatherData | null) => void;
    onRegionSelect?: (provinceName: string, cityName: string | null) => void;
    activeProvinceName?: string | null;
    activeCityName?: string | null;
}

const PROVINCES = [
    { code: "11", name: "서울특별시" },
    { code: "26", name: "부산광역시" },
    { code: "27", name: "대구광역시" },
    { code: "28", name: "인천광역시" },
    { code: "29", name: "광주광역시" },
    { code: "30", name: "대전광역시" },
    { code: "31", name: "울산광역시" },
    { code: "36", name: "세종특별자치시" },
    { code: "41", name: "경기도" },
    { code: "42", name: "강원도" },
    { code: "43", name: "충청북도" },
    { code: "44", name: "충청남도" },
    { code: "45", name: "전라북도" },
    { code: "46", name: "전라남도" },
    { code: "47", name: "경상북도" },
    { code: "48", name: "경상남도" },
    { code: "50", name: "제주특별자치도" },
];

export default function WeatherBanner({ onRecommendationUpdate, onRegionSelect, activeProvinceName, activeCityName }: WeatherBannerProps) {
    const [selectedProvince, setSelectedProvince] = useState(""); // Default: Empty
    const [selectedCity, setSelectedCity] = useState("");
    const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
    const [availableCities, setAvailableCities] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchWeather = async (admCd: string, city: string = "") => {
        setLoading(true);
        try {
            // Use API proxy with city param
            let url = `/api/python/weather/recommend?adm_cd=${admCd}`;
            if (city) {
                url += `&city=${encodeURIComponent(city)}`;
            }

            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                setWeatherData(data);
                onRecommendationUpdate(data);

                // Update available cities if provided (usually on province fetch)
                if (data.available_cities) {
                    setAvailableCities(data.available_cities);
                }

                // Sync with parent map if requested
                if (onRegionSelect) {
                    const provinceName = PROVINCES.find(p => p.code === admCd)?.name;
                    if (provinceName) {
                        onRegionSelect(provinceName, city || null);
                    }
                }
            } else {
                console.error("Weather fetch failed");
            }
        } catch (error) {
            console.error("Error fetching weather:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // Initial fetch removed to allow user to select first
    }, []);

    // Sync with external props (Map selection)
    useEffect(() => {
        if (!activeProvinceName) return;

        const prov = PROVINCES.find(p => p.name === activeProvinceName);
        if (prov) {
            // Only update if different from current state to avoid loops
            const isProvDiff = prov.code !== selectedProvince;
            const isCityDiff = (activeCityName || "") !== selectedCity;

            if (isProvDiff || isCityDiff) {
                // If it's a new province, usually we want to reset city unless specific city is passed
                // If the change comes from Map, we trust activeCityName
                setSelectedProvince(prov.code);
                setSelectedCity(activeCityName || "");

                // Fetch weather for the new selection
                // Note: We avoid calling onRegionSelect back here to prevent infinite loop logic if not handled carefully
                // But fetchWeather calls onRegionSelect. 
                // However, page.tsx handles "if same, ignore".
                fetchWeather(prov.code, activeCityName || "");
            }
        }
    }, [activeProvinceName, activeCityName]);

    const handleProvinceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const code = e.target.value;
        setSelectedProvince(code);
        setSelectedCity(""); // Reset city
        fetchWeather(code, ""); // Fetch province level (gets city list)
    };

    const handleCityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const city = e.target.value;
        setSelectedCity(city);
        fetchWeather(selectedProvince, city);
    };

    // Center coordinates for approximation (Lat, Lon)
    const PROVINCE_COORDINATES: Record<string, { lat: number; lon: number }> = {
        "11": { lat: 37.5665, lon: 126.9780 }, // Seoul
        "26": { lat: 35.1796, lon: 129.0756 }, // Busan
        "27": { lat: 35.8714, lon: 128.6014 }, // Daegu
        "28": { lat: 37.4563, lon: 126.7052 }, // Incheon
        "29": { lat: 35.1595, lon: 126.8526 }, // Gwangju
        "30": { lat: 36.3504, lon: 127.3845 }, // Daejeon
        "31": { lat: 35.5384, lon: 129.3114 }, // Ulsan
        "36": { lat: 36.4801, lon: 127.2892 }, // Sejong
        "41": { lat: 37.4138, lon: 127.5183 }, // Gyeonggi
        "42": { lat: 37.8228, lon: 128.1555 }, // Gangwon
        "43": { lat: 36.6350, lon: 127.4914 }, // Chungbuk
        "44": { lat: 36.6588, lon: 126.6728 }, // Chungnam
        "45": { lat: 35.7175, lon: 127.1530 }, // Jeonbuk
        "46": { lat: 34.8679, lon: 126.9910 }, // Jeonnam
        "47": { lat: 36.5783, lon: 128.5093 }, // Gyeongbuk
        "48": { lat: 35.2383, lon: 128.6922 }, // Gyeongnam
        "50": { lat: 33.4996, lon: 126.5312 }, // Jeju
    };

    const getDistanceFromLatLonInKm = (lat1: number, lon1: number, lat2: number, lon2: number) => {
        const R = 6371; // Radius of the earth in km
        const dLat = (lat2 - lat1) * (Math.PI / 180);
        const dLon = (lon2 - lon1) * (Math.PI / 180);
        const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        const d = R * c; // Distance in km
        return d;
    };

    const findNearestProvince = (lat: number, lon: number): string => {
        let minDistance = Infinity;
        let nearestCode = "11"; // Default to Seoul

        Object.entries(PROVINCE_COORDINATES).forEach(([code, coords]) => {
            const distance = getDistanceFromLatLonInKm(lat, lon, coords.lat, coords.lon);
            if (distance < minDistance) {
                minDistance = distance;
                nearestCode = code;
            }
        });
        return nearestCode;
    };

    const handleCurrentLocation = () => {
        if (!navigator.geolocation) {
            alert("브라우저가 위치 정보를 지원하지 않습니다.");
            return;
        }

        setLoading(true);
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                const nearestCode = findNearestProvince(latitude, longitude);
                const provinceName = PROVINCES.find(p => p.code === nearestCode)?.name;

                // alert(`현재 위치에서 가장 가까운 ${provinceName}(으)로 이동합니다.`); // Optional feedback
                setSelectedProvince(nearestCode);
                fetchWeather(nearestCode);
                setLoading(false);
            },
            (error) => {
                console.error("Geolocation error:", error);
                alert("위치 정보를 가져올 수 없습니다. 권한을 확인해주세요.");
                setLoading(false);
            }
        );
    };

    const getWeatherIconPath = (desc: string) => {
        if (desc.includes("비")) return "/weather_icons/rain.png";
        if (desc.includes("눈")) return "/weather_icons/snow.png";
        if (desc.includes("번개") || desc.includes("뇌우")) return "/weather_icons/lightenig.png";
        if (desc.includes("흐림")) return "/weather_icons/cloud.png";
        if (desc.includes("구름많음") || desc.includes("구름")) return "/weather_icons/cloud_sunny.png";
        if (desc.includes("무더움") || desc.includes("맑음")) return "/weather_icons/sunny.png";
        if (desc.includes("추움") || desc.includes("바람")) return "/weather_icons/wind.png";
        return "/weather_icons/cloud_sunny.png"; // Default fallback
    };

    return (
        <div className={styles.bannerContainer}>
            <div className={styles.title}>오늘의 날씨 & 우리술</div>

            <button className={styles.locationButton} onClick={handleCurrentLocation}>
                📍 내 위치 날씨 보기
            </button>

            <div className={styles.selectGroup}>
                <select
                    className={styles.select}
                    value={selectedProvince}
                    onChange={handleProvinceChange}
                >
                    {PROVINCES.map((prov) => (
                        <option key={prov.code} value={prov.code}>
                            {prov.name}
                        </option>
                    ))}
                </select>

                {availableCities.length > 0 && (
                    <select
                        className={styles.select}
                        value={selectedCity}
                        onChange={handleCityChange}
                        style={{ marginTop: '8px' }}
                    >
                        <option value="">시/군/구 선택</option>
                        {availableCities.map((city) => (
                            <option key={city} value={city}>
                                {city}
                            </option>
                        ))}
                    </select>
                )}
            </div>

            {loading ? (
                <div style={{ textAlign: "center", padding: "20px" }}>불러오는 중...</div>
            ) : weatherData && weatherData.weather ? (
                <div className={styles.weatherInfo}>
                    <div className={styles.weatherIcon}>
                        <Image
                            src={getWeatherIconPath(weatherData.weather)}
                            alt={weatherData.weather}
                            width={80}
                            height={80}
                            style={{ objectFit: 'contain' }}
                            priority
                        />
                    </div>
                    <div className={styles.temperature}>{weatherData.temperature}°C</div>
                    <div className={styles.condition}>{weatherData.city} ({weatherData.weather})</div>

                    <div className={styles.recommendationBox}>
                        <div>추천: <span className={styles.keyword}>{weatherData.keyword}</span></div>
                        <div style={{ marginTop: "5px", fontSize: "0.8rem", color: "#5d4037", display: "flex", alignItems: "center", justifyContent: "center", gap: "4px" }}>
                            <Image
                                src={getWeatherIconPath(weatherData.weather)}
                                alt=""
                                width={20}
                                height={20}
                            />
                            <span>{weatherData.message.split("\n")[1] || weatherData.message}</span>
                        </div>
                    </div>
                </div>
            ) : (
                <div style={{ textAlign: "center", color: "gray", padding: "20px" }}>
                    {selectedProvince ? "시/군을 선택하면 날씨가 표시됩니다 👆" : "지역을 선택하면 날씨와 추천 술이 표시됩니다 📍"}
                </div>
            )}
        </div>
    );
}
