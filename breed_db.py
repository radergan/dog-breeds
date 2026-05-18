"""
Data Access Layer for Dog Breeds Database
Provides clean API for querying and manipulating breed data
"""
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

DB_FILE = 'dog_breeds.db'


class BreedDB:
    """Database access layer for dog breeds"""
    
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
    
    def _get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== BREED QUERIES ====================
    
    def get_all_breeds(self, order_by='name') -> List[Dict]:
        """Get all breeds"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'SELECT * FROM breeds ORDER BY {order_by}')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_breed_by_uuid(self, uuid: str) -> Optional[Dict]:
        """Get single breed by UUID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM breeds WHERE uuid = ?', (uuid,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_breed_by_slug(self, slug: str) -> Optional[Dict]:
        """Get single breed by slug"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM breeds WHERE slug = ?', (slug,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_breed_by_name(self, name: str) -> Optional[Dict]:
        """Get single breed by exact name"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM breeds WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def search_breeds(self, query: str) -> List[Dict]:
        """Search breeds by name (case-insensitive)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM breeds WHERE name LIKE ? ORDER BY name',
            (f'%{query}%',)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def filter_breeds(self, 
                     size: Optional[str] = None,
                     group: Optional[str] = None,
                     shedding: Optional[str] = None,
                     good_with_kids: Optional[bool] = None,
                     good_with_pets: Optional[bool] = None) -> List[Dict]:
        """Filter breeds by various criteria"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if size:
            conditions.append('size = ?')
            params.append(size)
        
        if group:
            conditions.append('group_slug = ?')
            params.append(group)
        
        if shedding:
            conditions.append('shedding = ?')
            params.append(shedding)
        
        if good_with_kids is not None:
            conditions.append('good_with_kids = ?')
            params.append(good_with_kids)
        
        if good_with_pets is not None:
            conditions.append('good_with_pets = ?')
            params.append(good_with_pets)
        
        where_clause = ' AND '.join(conditions) if conditions else '1=1'
        query = f'SELECT * FROM breeds WHERE {where_clause} ORDER BY name'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_breeds_by_size(self, size: str) -> List[Dict]:
        """Get all breeds of a specific size"""
        return self.filter_breeds(size=size)
    
    def get_breeds_by_group(self, group: str) -> List[Dict]:
        """Get all breeds in a specific group"""
        return self.filter_breeds(group=group)
    
    # ==================== IMAGES ====================
    
    def get_breed_images(self, breed_uuid: str) -> List[Dict]:
        """Get all images for a breed"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM breed_images WHERE breed_uuid = ? ORDER BY is_primary DESC, created_at',
            (breed_uuid,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_breed_image(self, breed_uuid: str, image_url: str, 
                       caption: Optional[str] = None,
                       source: Optional[str] = None,
                       is_primary: bool = False):
        """Add an image to a breed"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO breed_images (breed_uuid, image_url, caption, source, is_primary)
        VALUES (?, ?, ?, ?, ?)
        ''', (breed_uuid, image_url, caption, source, is_primary))
        
        conn.commit()
        image_id = cursor.lastrowid
        conn.close()
        
        return image_id
    
    # ==================== VIDEOS ====================
    
    def get_breed_videos(self, breed_uuid: str) -> List[Dict]:
        """Get all videos for a breed"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM breed_videos WHERE breed_uuid = ? ORDER BY is_featured DESC, created_at',
            (breed_uuid,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_breed_video(self, breed_uuid: str, platform: str, video_id: str,
                       video_url: str, title: Optional[str] = None,
                       thumbnail_url: Optional[str] = None,
                       duration: Optional[int] = None,
                       is_featured: bool = False):
        """Add a video to a breed"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO breed_videos 
        (breed_uuid, platform, video_id, video_url, title, thumbnail_url, duration, is_featured)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (breed_uuid, platform, video_id, video_url, title, thumbnail_url, duration, is_featured))
        
        conn.commit()
        video_id_result = cursor.lastrowid
        conn.close()
        
        return video_id_result
    
    # ==================== COMMENTS ====================
    
    def get_breed_comments(self, breed_uuid: str, approved_only: bool = True) -> List[Dict]:
        """Get comments for a breed"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if approved_only:
            cursor.execute(
                'SELECT * FROM comments WHERE breed_uuid = ? AND is_approved = 1 ORDER BY created_at DESC',
                (breed_uuid,)
            )
        else:
            cursor.execute(
                'SELECT * FROM comments WHERE breed_uuid = ? ORDER BY created_at DESC',
                (breed_uuid,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_comment(self, breed_uuid: str, comment_text: str,
                   user_name: Optional[str] = None,
                   user_email: Optional[str] = None,
                   rating: Optional[int] = None):
        """Add a comment to a breed (requires approval)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO comments (breed_uuid, user_name, user_email, comment_text, rating, is_approved)
        VALUES (?, ?, ?, ?, ?, 0)
        ''', (breed_uuid, user_name, user_email, comment_text, rating))
        
        conn.commit()
        comment_id = cursor.lastrowid
        conn.close()
        
        return comment_id
    
    def approve_comment(self, comment_id: int):
        """Approve a comment"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE comments SET is_approved = 1 WHERE id = ?', (comment_id,))
        
        conn.commit()
        conn.close()
    
    def get_pending_comments(self) -> List[Dict]:
        """Get all comments pending approval"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM comments WHERE is_approved = 0 ORDER BY created_at DESC'
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== STATISTICS ====================
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM breeds')
        stats['total_breeds'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM breed_images')
        stats['total_images'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM breed_videos')
        stats['total_videos'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM comments WHERE is_approved = 1')
        stats['approved_comments'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM comments WHERE is_approved = 0')
        stats['pending_comments'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT size, COUNT(*) as count FROM breeds GROUP BY size')
        stats['breeds_by_size'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute('SELECT group_display, COUNT(*) as count FROM breeds GROUP BY group_display ORDER BY count DESC')
        stats['breeds_by_group'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return stats


# ==================== EXAMPLE USAGE ====================

if __name__ == '__main__':
    db = BreedDB()
    
    # Get all breeds
    print("🐕 All Breeds:")
    breeds = db.get_all_breeds()
    print(f"   Found {len(breeds)} breeds\n")
    
    # Search for a breed
    print("🔍 Search for 'Golden':")
    results = db.search_breeds('Golden')
    for breed in results:
        print(f"   - {breed['name']} ({breed['uuid']})")
    print()
    
    # Filter by size
    print("📏 Small Breeds:")
    small_breeds = db.get_breeds_by_size('Small')
    print(f"   Found {len(small_breeds)} small breeds\n")
    
    # Filter by multiple criteria
    print("🏠 Small, Non-Shedding, Good with Kids:")
    filtered = db.filter_breeds(
        size='Small',
        shedding='Non-Shedding',
        good_with_kids=True
    )
    for breed in filtered:
        print(f"   - {breed['name']}")
    print()
    
    # Get statistics
    print("📊 Database Statistics:")
    stats = db.get_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"      {k}: {v}")
        else:
            print(f"   {key}: {value}")
