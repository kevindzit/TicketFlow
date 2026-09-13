import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import bcrypt

from app import create_app, db
from app.models.user import User
from config import Config


class AuthTests(unittest.TestCase):
    def setUp(self):
        # use a separate in-memory database for every test
        with patch.object(Config, 'SQLALCHEMY_DATABASE_URI', 'sqlite://'):
            self.app = create_app()
        self.app.config.update(TESTING=True, SECRET_KEY='test-secret')
        self.context = self.app.app_context()
        self.context.push()
        self.client = self.app.test_client()

        self.password = 'original-test-password'
        self.password_hash = bcrypt.hashpw(
            self.password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')
        self.user = User(
            name='Test User',
            email='user@example.test',
            password_hash=self.password_hash,
            role='technician'
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def login(self, password=None):
        return self.client.post('/login', data={
            'email': self.user.email,
            'password': self.password if password is None else password
        })

    def assert_password_unchanged(self):
        db.session.refresh(self.user)
        self.assertEqual(self.user.password_hash, self.password_hash)

    def test_login_page_has_no_reset_link(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'/forgot-password', response.data)

    def test_forgot_password_get_is_disabled(self):
        response = self.client.get('/forgot-password')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Password reset is disabled in this demo.', response.data)

    def test_forgot_password_post_does_not_issue_tokens(self):
        responses = []
        for email in (self.user.email, 'missing@example.test', ''):
            with self.subTest(email=email):
                response = self.client.post('/forgot-password', data={'email': email})
                responses.append(response.data)
                self.assertEqual(response.status_code, 403)
                self.assertNotIn(b'/reset-password/', response.data)
                self.assert_password_unchanged()
                self.assertIsNone(self.user.reset_token)
                self.assertIsNone(self.user.reset_token_expiry)
                with self.client.session_transaction() as session:
                    self.assertFalse(session.get('_flashes'))
        self.assertEqual(responses[0], responses[1])
        self.assertEqual(responses[0], responses[2])

    def test_previously_issued_tokens_cannot_reset_passwords(self):
        token = 'previously-issued-test-token'
        for hours in (1, -1):
            self.user.reset_token = token
            self.user.reset_token_expiry = datetime.utcnow() + timedelta(hours=hours)
            db.session.commit()
            for method in ('GET', 'POST'):
                with self.subTest(hours=hours, method=method):
                    response = self.client.open('/reset-password/' + token, method=method, data={
                        'new_password': 'unauthorized-new-password',
                        'confirm_password': 'unauthorized-new-password'
                    })
                    self.assertEqual(response.status_code, 403)
                    self.assertNotIn(token.encode('utf-8'), response.data)
                    self.assert_password_unchanged()

    def test_unknown_reset_token_is_disabled(self):
        for method in ('GET', 'POST'):
            with self.subTest(method=method):
                response = self.client.open('/reset-password/unknown-token', method=method)
                self.assertEqual(response.status_code, 403)
                self.assert_password_unchanged()

    def test_valid_login_still_works(self):
        response = self.login()
        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as session:
            self.assertEqual(session.get('_user_id'), str(self.user.id))
        self.assertEqual(self.client.get('/profile').status_code, 200)

    def test_invalid_login_is_rejected(self):
        response = self.login('wrong-password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)
        with self.client.session_transaction() as session:
            self.assertNotIn('_user_id', session)

    def test_profile_password_change_requires_login(self):
        response = self.client.post('/profile/password', data={
            'current_password': self.password,
            'new_password': 'new-test-password',
            'confirm_password': 'new-test-password'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])
        self.assert_password_unchanged()

    def test_profile_password_change_requires_current_password(self):
        self.login()
        self.client.post('/profile/password', data={
            'current_password': 'wrong-password',
            'new_password': 'new-test-password',
            'confirm_password': 'new-test-password'
        })
        self.assert_password_unchanged()

    def test_profile_password_change_still_works(self):
        self.login()
        response = self.client.post('/profile/password', data={
            'current_password': self.password,
            'new_password': 'new-test-password',
            'confirm_password': 'new-test-password'
        })
        self.assertEqual(response.status_code, 302)
        db.session.refresh(self.user)
        self.assertTrue(bcrypt.checkpw(
            b'new-test-password', self.user.password_hash.encode('utf-8')
        ))


if __name__ == '__main__':
    unittest.main()
