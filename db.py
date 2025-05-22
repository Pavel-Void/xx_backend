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
        select_query = """
        SELECT id FROM zones WHERE address = %s AND type = %s;
            """
        insert_query = """
                INSERT INTO zones (address, type)
                VALUES (%s, %s) RETURNING id; 
                """
        with self.get_cursor() as cur:
            cur.execute(select_query, (address, zone_type))
            existing_zone = cur.fetchone()
            if existing_zone:
                zone_id = existing_zone['id']
                print(f"[=] Зона уже существует с ID: {zone_id}")
                return zone_id
            else:
                cur.execute(insert_query, (address, zone_type))
                zone_id = cur.fetchone()['id']
                print(f"[+] Добавлена новая зона ID: {zone_id}")
                return zone_id

    def get_all_zones(self):
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM zones;")
            return cur.fetchall()


    def get_incident_by_number(self, number):
        query = "SELECT * FROM incidents WHERE number = %s;"
        with self.get_cursor() as cur:
            cur.execute(query, (number,))
            return cur.fetchone()

    def add_or_update_incident(self, title, description, latitude, longitude,
                               sla, number, zone_id=None,
                               priority='Низкий', status='Новая'):
        existing = self.get_incident_by_number(number)
        if existing:
            if existing['status'] != status:
                query = """
                        UPDATE incidents
                        SET title=%s, \
                            description=%s, \
                            latitude=%s, \
                            longitude=%s,
                            sla=%s, \
                            zone_id=%s, \
                            priority=%s, \
                            status=%s
                        WHERE number = %s RETURNING id; \
                        """
                with self.get_cursor() as cur:
                    cur.execute(query, (
                        title, description, latitude, longitude,
                        sla, zone_id, priority, status, number
                    ))
                    updated_id = cur.fetchone()['id']
                    print(f"[~] Обновлён инцидент ID: {updated_id}")
                    return updated_id
            else:
                print(f"[=] Инцидент с номером {number} уже существует и статус не изменился.")
                return existing['id']
        else:
            query = """
                    INSERT INTO incidents (title, description, latitude, longitude,
                                           sla, number, zone_id, priority, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id; \
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
            cur.execute("SELECT * FROM incidents WHERE status != 'Возвращена';")
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
    incident_id = manager.add_or_update_incident(
        title="Протечка в подвале",
        description="Вода поступает в подвал.",
        latitude=55.7558,
        longitude=37.6173,
        sla="4 часа",
        number=1003,
        zone_id=zone_id,
        priority="Высокий",
        status="В работе"
    )


    # Показываем все инциденты
    print("\n[Все инциденты]")
    for incident in manager.get_all_incidents():
        print(incident)
