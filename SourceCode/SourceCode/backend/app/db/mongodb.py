import os
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    client: AsyncIOMotorClient = None

db = MongoDB()

async def get_database():
    return db.client.get_database("myapp_db")

async def connect_to_mongo():
    """
    MongoDB Replica Set에 연결합니다.
    Primary가 다운되면 자동으로 Secondary로 failover됩니다.
    Replica Set 연결 실패 시 단일 노드로 fallback합니다.
    """
    # 단일 호스트 또는 여러 호스트 지원
    hosts = os.getenv("MONGODB_HOSTS", "192.168.0.182,192.168.0.183,192.168.0.184")
    port = os.getenv("MONGODB_PORT", "27017")
    user = os.getenv("MONGODB_USER", "root")
    password = os.getenv("MONGODB_PASSWORD", "pass123#")
    db_name = os.getenv("MONGODB_DB", "admin")
    replica_set = os.getenv("MONGODB_REPLICA_SET", "rs0")
    
    # Password URL encoding
    import urllib.parse
    encoded_password = urllib.parse.quote_plus(password)
    
    # 여러 호스트를 파싱
    host_list = [host.strip() for host in hosts.split(",")]
    
    # 먼저 Replica Set으로 연결 시도
    hosts_string = ",".join([f"{host}:{port}" for host in host_list])
    replica_url = f"mongodb://{user}:{encoded_password}@{hosts_string}/{db_name}?replicaSet={replica_set}"
    
    print(f"🔍 MongoDB Replica Set 연결 시도: {host_list}")
    
    try:
        db.client = AsyncIOMotorClient(
            replica_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True,
            maxPoolSize=50
        )
        
        # 연결 테스트
        await db.client.admin.command('ping')
        
        # 연결된 서버 정보 출력
        server_info = await db.client.server_info()
        
        print("=" * 60)
        print("✅ MongoDB Replica Set 연결 성공!")
        print(f"📦 MongoDB 버전: {server_info.get('version', 'Unknown')}")
        
        # Replica Set 상태 확인
        try:
            replica_status = await db.client.admin.command('replSetGetStatus')
            members = replica_status.get('members', [])
            
            print(f"🖥️  Replica Set: {replica_set}")
            print(f"🔗 총 멤버 수: {len(members)}")
            print("\n📋 Replica Set 멤버 목록:")
            
            for member in members:
                state_str = member.get('stateStr', 'Unknown')
                health = '✅' if member.get('health') == 1 else '❌'
                primary_mark = '⭐ (PRIMARY)' if state_str == 'PRIMARY' else ''
                host = member.get('name', 'Unknown')
                
                print(f"  {health} {host} | {state_str} {primary_mark}")
                
        except Exception as e:
            print(f"⚠️  Replica Set 상태 확인 불가: {e}")
        
        print("=" * 60)
        return
        
    except Exception as replica_error:
        print(f"⚠️  Replica Set 연결 실패: {replica_error}")
        print("🔄 단일 노드 연결로 fallback 시도 중...")
        
        # Fallback: 각 호스트에 직접 연결 시도
        for host in host_list:
            try:
                single_url = f"mongodb://{user}:{encoded_password}@{host}:{port}/{db_name}"
                print(f"  📍 {host}:{port} 연결 시도...")
                
                db.client = AsyncIOMotorClient(
                    single_url,
                    serverSelectionTimeoutMS=3000,
                    connectTimeoutMS=5000,
                    maxPoolSize=50
                )
                
                # 연결 테스트
                await db.client.admin.command('ping')
                server_info = await db.client.server_info()
                
                print("=" * 60)
                print(f"✅ MongoDB 단일 노드 연결 성공!")
                print(f"📍 연결된 호스트: {host}:{port}")
                print(f"📦 MongoDB 버전: {server_info.get('version', 'Unknown')}")
                print("=" * 60)
                return
                
            except Exception as single_error:
                print(f"  ❌ {host} 연결 실패: {single_error}")
                if db.client:
                    db.client.close()
                    db.client = None
                continue
        
        # 모든 연결 시도 실패
        print("=" * 60)
        print("❌ MongoDB 연결 완전 실패 - 모든 호스트 연결 불가")
        print(f"   시도한 호스트: {host_list}")
        print("=" * 60)
        raise Exception(f"MongoDB 연결 실패: 모든 호스트({host_list})에 연결할 수 없습니다")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")
