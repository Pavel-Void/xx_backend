import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


class IncidentManager:
    def __init__(self, db_config):
        self.db_config = db_config

    @contextmanager
    def get_cursor(self):
        conn = psycopg2.connect(**self.db_config)
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            yield cur
            conn.commit()
        finally:
            cur.close()
            conn.close()


    def add_zone(self, address: str, zone_type: str):
        query = """
                INSERT INTO zones (address, type)
                VALUES (%s, %s) RETURNING id; 
                """
        with self.get_cursor() as cur:
            cur.execute(query, (address, zone_type))
            zone_id = cur.fetchone()['id']
            print(f"[+] Добавлена зона ID: {zone_id}")
            return zone_id

    def get_all_zones(self):
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM zones;")
            return cur.fetchall()


    def add_incident(self, title, description, latitude, longitude,
                     sla, number, zone_id=None,
                     priority='Низкий', status='Новая'):
        query = """
                INSERT INTO incidents (title, description, latitude, longitude,
                                       sla, number, zone_id, priority, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """
        with self.get_cursor() as cur:
            cur.execute(query, (
                title, description, latitude, longitude,
                sla, number, zone_id, priority, status
            ))
            incident_id = cur.fetchone()['id']
            print(f"[+] Добавлен инцидент ID: {incident_id}")
            return incident_id

    def get_all_incidents(self):
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM incidents;")
            return cur.fetchall()



if __name__ == '__main__':
    db_config = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': 'admin',
        'host': 'localhost',
        'port': '5432'
    }

    manager = IncidentManager(db_config)

    # Добавляем зону
    zone_id = manager.add_zone("ЖК Солнечный", "ЖК")

    # Показываем все зоны
    print("\n[Все зоны]")
    for zone in manager.get_all_zones():
        print(zone)

    # Добавляем инцидент
    incident_id = manager.add_incident(
        title="Протечка в подвале",
        description="Вода поступает в подвал.",
        latitude=55.7558,
        longitude=37.6173,
        sla="4 часа",
        number=1003,
        zone_id=zone_id,
        priority="Высокий",
        status="Назначена"
    )

    # Показываем все инциденты
    print("\n[Все инциденты]")
    for incident in manager.get_all_incidents():
        print(incident)
