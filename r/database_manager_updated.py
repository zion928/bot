
import pymysql

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '7856',
    'db': 'LoLDB',
    'charset': 'utf8'
}

class DatabaseManager:
    def __init__(self, config):
        self.connection = pymysql.connect(**config)
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)

    def insert(self, summoner_id, summoner_name, tier, rank, main_lane, secondary_lane):
        query = """
        INSERT INTO summoners (id, name, tier, rank, main_lane, secondary_lane) 
        VALUES (%s, %s, %s, %s, %s, %s) 
        ON DUPLICATE KEY UPDATE name=%s, tier=%s, rank=%s, main_lane=%s, secondary_lane=%s
        """
        
        data = (summoner_id, summoner_name, tier, rank, main_lane, secondary_lane, 
                summoner_name, tier, rank, main_lane, secondary_lane)
        
        try:
            self.cursor.execute(query, data)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error inserting into database: {e}")
            return False
        
    def select(self, query, data=None):
        try:
            self.cursor.execute(query, data)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching from database: {e}")
            return None

    def update(self, query, data):
        try:
            self.cursor.execute(query, data)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating database: {e}")
            return False

    def delete(self, query, data):
        try:
            self.cursor.execute(query, data)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting from database: {e}")
            return False

    def close(self):
        self.cursor.close()
        self.connection.close()


    
    def get_summoner_info(self, summoner_name):
        query = "SELECT * FROM summoners WHERE name=%s"
        data = (summoner_name,)
        
        result = self.select(query, data)
        return result[0] if result else None
    
