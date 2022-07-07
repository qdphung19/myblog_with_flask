from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post
 
class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
 
    def tearDown(self):
        db.session.remove()
        db.drop_all()
 
    def test_password_hashing(self):
        u = User(username='Jonathan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))
 
    # def test_avatar(self):
    #     u = User(username='Duong', email='Duong@example.com')
    #     self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
    #                                      'd4c74594d841139328695756648b6bd6'
    #                                      '?d=identicon&s=128'))
 
    def test_follow(self):
        u1 = User(username='Duong', email='Duong@example.com')
        u2 = User(username='Jonathan', email='Jonathan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])
 
        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'Jonathan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'Duong')
 
        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)
 
    def test_follow_posts(self):
        # Créer 4 users
        u1 = User(username='Duong', email='Duong@example.com')
        u2 = User(username='Jonathan', email='Jonathan@example.com')
        u3 = User(username='Macron', email='Macron@example.com')
        u4 = User(username='Holland', email='Holland@example.com')
        db.session.add_all([u1, u2, u3, u4])
 
        # Créer 4 posts
        now = datetime.utcnow()
        p1 = Post(body="post của thái", author=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post của nguyên", author=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post của Macron", author=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post của Holland", author=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()
 
        # Créer followers
        u1.follow(u2)  # thái follows nguyên
        u1.follow(u4)  # thái follows Holland
        u2.follow(u3)  # nguyên follows Macron
        u3.follow(u4)  # Macron follows Holland
        db.session.commit()
 
        # kiểm tra các bài viết được theo dõi từ các user
        # test des posts, qui sont followed des users
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])
 
if __name__ == '__main__':
    unittest.main(verbosity=2)