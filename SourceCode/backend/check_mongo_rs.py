#!/usr/bin/env python3
"""
MongoDB Replica Set 이름 확인 스크립트
"""
from pymongo import MongoClient
import urllib.parse

# MongoDB 연결 정보
HOSTS = ["192.168.0.182", "192.168.0.183", "192.168.0.184"]
PORT = 27017
USER = "root"
PASSWORD = "pass123#"
DB = "admin"

def check_replica_set():
    """각 MongoDB 서버에 연결하여 Replica Set 정보 확인"""
    
    encoded_password = urllib.parse.quote_plus(PASSWORD)
    
    print("=" * 60)
    print("🔍 MongoDB Replica Set 정보 확인 중...")
    print("=" * 60)
    
    for host in HOSTS:
        print(f"\n📍 {host}:{PORT} 연결 시도...")
        
        try:
            # 연결 문자열
            mongo_url = f"mongodb://{USER}:{encoded_password}@{host}:{PORT}/{DB}"
            
            # 연결 (타임아웃 짧게)
            client = MongoClient(
                mongo_url,
                serverSelectionTimeoutMS=3000,
                connectTimeoutMS=5000
            )
            
            # Ping 테스트
            client.admin.command('ping')
            print(f"  ✅ 연결 성공!")
            
            # Replica Set 상태 확인
            try:
                status = client.admin.command("replSetGetStatus")
                replica_set_name = status.get('set', 'Unknown')
                members = status.get('members', [])
                
                print(f"\n  🎯 Replica Set 이름: {replica_set_name}")
                print(f"  👥 멤버 수: {len(members)}")
                print(f"\n  📋 멤버 목록:")
                
                for member in members:
                    state = member.get('stateStr', 'Unknown')
                    name = member.get('name', 'Unknown')
                    health = '✅' if member.get('health') == 1 else '❌'
                    primary = '⭐ PRIMARY' if state == 'PRIMARY' else state
                    
                    print(f"    {health} {name} - {primary}")
                
                print(f"\n  ✨ backend.env에 추가할 내용:")
                print(f"     MONGODB_REPLICA_SET={replica_set_name}")
                
                # 첫 번째 성공한 서버에서 정보를 얻었으면 종료
                return replica_set_name
                
            except Exception as rs_error:
                print(f"  ⚠️  Replica Set 정보 확인 실패: {rs_error}")
                print(f"     (Replica Set이 아닌 단일 서버일 수 있습니다)")
            
            client.close()
            
        except Exception as e:
            print(f"  ❌ 연결 실패: {e}")
    
    print("\n" + "=" * 60)
    print("❌ 모든 MongoDB 서버 연결 실패")
    print("=" * 60)
    return None

if __name__ == "__main__":
    replica_set_name = check_replica_set()
    
    if replica_set_name:
        print(f"\n✅ Replica Set 이름 확인 완료: {replica_set_name}")
    else:
        print("\n⚠️  Replica Set 이름을 확인할 수 없습니다.")
        print("   일반적인 이름 (rs0, myReplicaSet 등)을 시도해보세요.")
