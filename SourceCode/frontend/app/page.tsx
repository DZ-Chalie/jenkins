"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import styles from "./page.module.css";
import InteractiveMap from './components/InteractiveMap';
import WeatherBanner from "./components/WeatherBanner";
import MainSecondPage from "./components/MainSecondPage";

interface Liquor {
  id: number;
  name: string;
  type: string;
  alcohol: string;
  image_url: string;
  price: number;
  volume: string;
}

interface Product {
  name: string;
  price: number;
  shop: string;
  url: string;
  image_url: string;
}

export default function Home() {
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [selectedCity, setSelectedCity] = useState<string | null>(null);
  const [selectedSeason, setSelectedSeason] = useState<string | null>(null);
  const [sortField, setSortField] = useState<'price' | 'alcohol' | 'weather' | null>(null);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [liquors, setLiquors] = useState<Liquor[]>([]);
  const [loading, setLoading] = useState(false);
  const [weatherRec, setWeatherRec] = useState<any>(null);
  const [weatherSource, setWeatherSource] = useState<'user' | 'map'>('user');
  const [selectedLiquor, setSelectedLiquor] = useState<Liquor | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(false);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 5;

  // Helper to determine weather condition from weather data
  const getWeatherCondition = (weather: any): string => {
    if (!weather) return 'clear';
    const rain = weather.PCPTTN_SHP || '';
    const temp = parseFloat(weather.NOW_AIRTP || '20');

    if (rain.includes('비') || rain === '1' || rain === '2') return 'rain';
    if (rain.includes('눈') || rain === '3') return 'snow';
    if (temp < 5) return 'cold';
    if (temp > 28) return 'hot';
    return 'clear';
  };

  const fetchLiquors = async (province: string, city: string | null = null, season: string | null = null) => {
    setLoading(true);
    try {
      let url = `/api/python/search/region?province=${encodeURIComponent(province)}&size=1000`;
      if (city) {
        url += `&city=${encodeURIComponent(city)}`;
      }
      if (season) {
        url += `&season=${encodeURIComponent(season)}`;
      }

      // Add weather sorting if enabled
      if (sortField === 'weather' && weatherRec?.weather) {
        const condition = getWeatherCondition(weatherRec.weather);
        url += `&weather_condition=${condition}&weather_sort=true`;
      }

      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setLiquors(data);
      } else {
        setLiquors([]);
      }
    } catch (error) {
      console.error("Failed to fetch regional liquors:", error);
      setLiquors([]);
    } finally {
      setLoading(false);
      setCurrentPage(1);
    }
  };

  const fetchProducts = async (drinkName: string) => {
    setLoadingProducts(true);
    try {
      const response = await fetch(`/api/python/search/products/${encodeURIComponent(drinkName)}`);
      if (response.ok) {
        const data = await response.json();
        setProducts(data.products || []);
      } else {
        setProducts([]);
      }
    } catch (error) {
      console.error("Failed to fetch products:", error);
      setProducts([]);
    } finally {
      setLoadingProducts(false);
    }
  };

  const handleSelectRegion = (region: string) => {
    if (selectedRegion === region) return;

    setSelectedRegion(region);
    setSelectedCity(null);
    setSelectedLiquor(null);
    setProducts([]);
    fetchLiquors(region, null, selectedSeason);
  };

  const handleSelectCity = (city: string) => {
    setSelectedCity(city);
    if (selectedRegion) {
      fetchLiquors(selectedRegion, city, selectedSeason);
    }
  };

  const handleBackToOverview = () => {
    setSelectedRegion(null);
    setSelectedCity(null);
    setLiquors([]);
    setSelectedLiquor(null);
    setProducts([]);
  };

  return (
    <div className={styles.container}>
      {/* Section 1: Map and List */}
      <section className={styles.section}>
        <div className={styles.background}>
          <Image
            src="/jumak.png"
            alt="Jumak Background"
            fill
            quality={100}
            sizes="100vw"
            style={{ objectFit: "cover", objectPosition: "center" }}
            priority
          />
          <div className={styles.overlay} />
        </div>

        <div className={styles.heroContent}>
          {/* Left: Maps Container */}
          <div className={styles.mapSection}>
            <InteractiveMap
              selectedRegion={selectedRegion}
              onSelectRegion={handleSelectRegion}
              onSelectCity={handleSelectCity}
            />
          </div>

          {/* Right: Content Panels Container */}
          <div className={styles.contentPanels}>
            {/* Panel 1: Weather Banner */}
            <div style={{ flex: '0 0 auto' }}>
              <WeatherBanner
                onRecommendationUpdate={setWeatherRec}
                onRegionSelect={(province, city) => {
                  handleSelectRegion(province);
                  if (city) handleSelectCity(city);
                }}
                activeProvinceName={selectedRegion}
                activeCityName={selectedCity}
              />
            </div>

            {/* Panel 2: Liquor List */}
            <div className={styles.listContainer}>
              <h2 className={styles.sectionTitle} style={{ color: '#333', marginTop: 0 }}>
                {selectedRegion ? `${selectedRegion} ${selectedCity || ''}의 전통주` : "지역을 선택해주세요"}
              </h2>

              {/* Season Tabs */}
              {selectedRegion && (
                <div className={styles.seasonTabs} style={{ marginBottom: '4px' }}>
                  {['전체', '봄', '여름', '가을', '겨울'].map((season) => (
                    <button
                      key={season}
                      className={`${styles.seasonChip} ${((selectedSeason === null && season === '전체') || selectedSeason === season) ? styles.active : ''}`}
                      onClick={() => {
                        const newSeason = season === '전체' ? null : season;
                        setSelectedSeason(newSeason);
                        if (selectedRegion) {
                          fetchLiquors(selectedRegion, selectedCity, newSeason);
                        }
                      }}
                    >
                      {season}
                    </button>
                  ))}
                </div>
              )}

              {/* Sort Buttons */}
              {selectedRegion && (
                <div className={styles.sortButtons} style={{ marginBottom: '6px' }}>
                  <button
                    className={sortField === 'price' ? styles.activeSortBtn : ''}
                    onClick={() => {
                      setSortField('price');
                      if (selectedRegion) fetchLiquors(selectedRegion, selectedCity, selectedSeason);
                    }}
                  >
                    가격
                  </button>
                  <button
                    className={sortField === 'alcohol' ? styles.activeSortBtn : ''}
                    onClick={() => {
                      setSortField('alcohol');
                      if (selectedRegion) fetchLiquors(selectedRegion, selectedCity, selectedSeason);
                    }}
                  >
                    도수
                  </button>
                  <button
                    className={sortField === 'weather' ? styles.activeSortBtn : ''}
                    onClick={() => {
                      setSortField('weather');
                      if (selectedRegion) fetchLiquors(selectedRegion, selectedCity, selectedSeason);
                    }}
                  >
                    날씨 ☀️
                  </button>
                </div>
              )}

              {/* Location Preference Toggle */}
              {weatherRec && weatherRec.weather && (
                <div style={{ marginBottom: '6px', textAlign: 'center' }}>
                  <button
                    onClick={() => setWeatherSource(prev => prev === 'user' ? 'map' : 'user')}
                    style={{
                      padding: '4px 10px',
                      fontSize: '0.75rem',
                      borderRadius: '12px',
                      border: '1px solid #8b4513',
                      background: 'white',
                      color: '#8b4513',
                      cursor: 'pointer',
                      fontWeight: '500'
                    }}
                  >
                    📍 {weatherSource === 'user' ? '내 위치' : '지도 위치'} 기준
                  </button>
                </div>
              )}

              {/* Weather Recommendation Banner */}
              {weatherRec && weatherRec.weather && (
                <div style={{
                  marginBottom: '6px',
                  padding: '6px 8px',
                  background: "url('/한지.jpg')",
                  backgroundSize: 'cover',
                  borderRadius: '8px',
                  border: '1px solid #ffcc80',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ fontSize: '1.1rem' }}>
                      {weatherRec.weather.includes('비') ? '☔' : weatherRec.weather.includes('눈') ? '❄️' : '☀️'}
                    </span>
                    <div style={{ fontSize: '0.8rem', color: '#5d4037' }}>
                      {sortField === 'weather' ? (
                        <>
                          😊 <strong style={{ color: '#e65100' }}>이 날씨에 어울리는 술을 먼저 추천드릴게요!</strong>
                        </>
                      ) : (
                        <>
                          <strong style={{ color: '#e65100' }}>{weatherRec.city}</strong> {weatherRec.message.split('\n')[0]}
                          <span style={{ marginLeft: '6px', color: '#d84315', fontWeight: 'bold' }}>→ {weatherRec.keyword}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Sort Buttons */}
              {selectedRegion && (
                <div style={{ display: 'flex', gap: '8px', marginBottom: '10px', flexWrap: 'wrap' }}>
                  <button
                    className={`${styles.seasonChip} ${sortField === 'price' ? styles.active : ''}`}
                    onClick={() => {
                      if (sortField === 'price') {
                        if (sortOrder === 'asc') {
                          setSortOrder('desc');
                        } else {
                          setSortField(null);
                          setSortOrder('asc');
                        }
                      } else {
                        setSortField('price');
                        setSortOrder('asc');
                      }
                    }}
                    style={{ fontSize: '0.85rem', padding: '6px 12px' }}
                  >
                    💰 가격 {sortField === 'price' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
                  </button>
                  <button
                    className={`${styles.seasonChip} ${sortField === 'alcohol' ? styles.active : ''}`}
                    onClick={() => {
                      if (sortField === 'alcohol') {
                        if (sortOrder === 'asc') {
                          setSortOrder('desc');
                        } else {
                          setSortField(null);
                          setSortOrder('asc');
                        }
                      } else {
                        setSortField('alcohol');
                        setSortOrder('asc');
                      }
                    }}
                    style={{ fontSize: '0.85rem', padding: '6px 12px' }}
                  >
                    🍶 도수 {sortField === 'alcohol' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
                  </button>
                </div>
              )}

              <div className={styles.liquorList}>
                {selectedRegion ? (
                  loading ? (
                    <div className={styles.loadingMessage}>불러오는 중... 🍶</div>
                  ) : liquors && liquors.length > 0 ? (
                    <>
                      {(() => {
                        // Apply sorting
                        let sortedLiquors = [...liquors];
                        if (sortField === 'price') {
                          sortedLiquors.sort((a, b) => {
                            const priceA = a.price || 0;
                            const priceB = b.price || 0;
                            return sortOrder === 'asc' ? priceA - priceB : priceB - priceA;
                          });
                        } else if (sortField === 'alcohol') {
                          sortedLiquors.sort((a, b) => {
                            const alcoholA = parseFloat(a.alcohol) || 0;
                            const alcoholB = parseFloat(b.alcohol) || 0;
                            return sortOrder === 'asc' ? alcoholA - alcoholB : alcoholB - alcoholA;
                          });
                        }
                        return sortedLiquors.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE);
                      })().map((liquor) => (
                        <div
                          key={liquor.id}
                          className={`${styles.liquorCard} ${selectedLiquor?.id === liquor.id ? styles.selectedCard : ''}`}
                          onClick={() => {
                            setSelectedLiquor(liquor);
                            fetchProducts(liquor.name);
                          }}
                        >
                          <div
                            className={styles.liquorImagePlaceholder}
                            onClick={(e) => {
                              e.stopPropagation();
                              window.location.href = `/drink/${liquor.id}`;
                            }}
                            style={{ cursor: 'pointer' }}
                          >
                            {liquor.image_url ? (
                              <img src={`/api/image-proxy?url=${encodeURIComponent(liquor.image_url)}`} alt={liquor.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                            ) : (
                              <span>🍶</span>
                            )}
                          </div>
                          <div className={styles.liquorInfo}>
                            <h3>{liquor.name}</h3>
                            <p>{liquor.type} | {liquor.alcohol}</p>
                            <p style={{ color: '#d32f2f', fontWeight: 'bold' }}>
                              {liquor.price ? `${liquor.price.toLocaleString()}원~` : '가격 정보 없음'}
                            </p>
                          </div>
                          <button
                            className={styles.detailButton}
                            onClick={(e) => {
                              e.stopPropagation();
                              window.location.href = `/drink/${liquor.id}`;
                            }}
                          >
                            상세보기 →
                          </button>
                        </div>
                      ))}

                      {/* Pagination Controls */}
                      {liquors.length > ITEMS_PER_PAGE && (
                        <div className={styles.pagination}>
                          {(() => {
                            const totalPages = Math.ceil(liquors.length / ITEMS_PER_PAGE);
                            const pageGroupSize = 5;
                            const currentGroup = Math.ceil(currentPage / pageGroupSize);
                            const startPage = (currentGroup - 1) * pageGroupSize + 1;
                            const endPage = Math.min(startPage + pageGroupSize - 1, totalPages);

                            return (
                              <>
                                {/* Prev 10 Pages (Jump) */}
                                {startPage > 1 && (
                                  <button
                                    className={styles.pageButton}
                                    onClick={() => setCurrentPage(startPage - 1)}
                                    title="이전 10페이지"
                                  >
                                    &lt;&lt;
                                  </button>
                                )}

                                {/* Prev Page */}
                                <button
                                  className={styles.pageButton}
                                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                                  disabled={currentPage === 1}
                                  title="이전 페이지"
                                >
                                  &lt;
                                </button>

                                {/* Page Numbers Window */}
                                {Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i).map((pageNum) => (
                                  <button
                                    key={pageNum}
                                    className={`${styles.pageButton} ${currentPage === pageNum ? styles.activePage : ''}`}
                                    onClick={() => setCurrentPage(pageNum)}
                                  >
                                    {pageNum}
                                  </button>
                                ))}

                                {/* Next Page */}
                                <button
                                  className={styles.pageButton}
                                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                                  disabled={currentPage === totalPages}
                                  title="다음 페이지"
                                >
                                  &gt;
                                </button>

                                {/* Next 10 Pages (Jump) */}
                                {endPage < totalPages && (
                                  <button
                                    className={styles.pageButton}
                                    onClick={() => setCurrentPage(endPage + 1)}
                                    title="다음 10페이지"
                                  >
                                    &gt;&gt;
                                  </button>
                                )}
                              </>
                            );
                          })()}
                        </div>
                      )}
                    </>
                  ) : (
                    <p className={styles.emptyMessage}>등록된 전통주 정보가 없습니다.</p>
                  )
                ) : (
                  <div className={styles.instructionMessage}>
                    <p>👈 왼쪽 지도에서 지역을 선택하면</p>
                    <p>해당 지역의 대표 전통주가 여기에 표시됩니다.</p>
                  </div>
                )}
              </div>
            </div>

            {/* Panel 3: Products Comparison / Side Dish */}
            <div className={styles.sideDishPanel}>
              {selectedLiquor ? (
                <>
                  <h2 style={{ color: '#333', marginTop: 0, fontSize: '1.5rem', marginBottom: '15px' }}>
                    {selectedLiquor.name} 구매처
                  </h2>
                  {loadingProducts ? (
                    <div style={{ textAlign: 'center', padding: '40px 20px', color: '#999' }}>
                      <p>불러오는 중...</p>
                    </div>
                  ) : products.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', overflowY: 'auto', maxHeight: '600px' }}>
                      {products.map((product, index) => (
                        <a
                          key={index}
                          href={product.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            padding: '10px',
                            background: 'url(\'/한지흰색.jpg\') repeat',
                            backgroundSize: '200px',
                            borderRadius: '8px',
                            textDecoration: 'none',
                            color: '#333',
                            border: '1px solid #d7ccc8',
                            transition: 'transform 0.2s, box-shadow 0.2s',
                            display: 'flex',
                            gap: '10px',
                            alignItems: 'center'
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-2px)';
                            e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = 'none';
                          }}
                        >
                          {product.image_url && (
                            <div style={{ flexShrink: 0, width: '55px', height: '55px', borderRadius: '6px', overflow: 'hidden', background: '#f5f5f5' }}>
                              <img
                                src={product.image_url}
                                alt={product.name}
                                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                onError={(e) => { e.currentTarget.style.display = 'none'; }}
                              />
                            </div>
                          )}
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: '2px' }}>
                              {product.shop}
                            </div>
                            <div style={{ fontSize: '0.85rem', fontWeight: '500', marginBottom: '4px', lineHeight: '1.2', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {product.name}
                            </div>
                            <div style={{ fontSize: '1rem', fontWeight: 'bold', color: '#d32f2f' }}>
                              {product.price.toLocaleString()}원
                            </div>
                          </div>
                          <div style={{ fontSize: '1.2rem', color: '#8d6e63' }}>→</div>
                        </a>
                      ))}
                    </div>
                  ) : (
                    <div style={{ textAlign: 'center', padding: '40px 20px', color: '#888' }}>
                      <p style={{ fontSize: '2rem', marginBottom: '10px' }}>🍶</p>
                      <p>온라인 판매처 정보가 없습니다.</p>
                      <p style={{ fontSize: '0.85rem', color: '#aaa' }}>양조장에 직접 문의해주세요.</p>
                    </div>
                  )}
                </>
              ) : (
                <div style={{ textAlign: 'center', padding: '60px 20px', color: '#999' }}>
                  <p style={{ fontSize: '3rem', marginBottom: '15px' }}>🍶</p>
                  <p style={{ fontSize: '1.1rem', color: '#666' }}>전통주를 선택하면</p>
                  <p style={{ fontSize: '1.1rem', color: '#666' }}>최저가 판매처가 표시됩니다</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className={styles.scrollIndicator}>
          <span>아래로 스크롤하여 더 많은 정보 보기</span>
          <div className={styles.arrow}>↓</div>
        </div>
      </section>

      {/* Second Page Section */}
      <section className={styles.section}>
        <MainSecondPage />
      </section>
    </div>
  );
}
