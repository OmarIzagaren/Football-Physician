from django.test import TestCase
from django.contrib.auth import get_user_model
from website.models import Player, Injury
from datetime import date

class BasicModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Create a test player linked to that user
        self.player = Player.objects.create(
            user=self.user,
            first_name="Lionel",
            last_name="Messi",
            position="FW",
            date_of_birth=date(1987, 6, 24),
            height=170,
            weight=72,
            country="Argentina"
        )

    def test_player_creation(self):
        """Player is correctly created and linked to user"""
        self.assertEqual(self.player.first_name, "Lionel")
        self.assertEqual(self.player.user.username, "testuser")

    def test_injury_creation(self):
        """Injury can be created and linked to a player"""
        injury = Injury.objects.create(
            player=self.player,
            injury="Hamstring",
            injury_start_date=date.today(),
            injury_end_date=None,
            injury_age=36,
            injured=True
        )
        self.assertEqual(injury.player.first_name, "Lionel")
        self.assertTrue(injury.injured)

