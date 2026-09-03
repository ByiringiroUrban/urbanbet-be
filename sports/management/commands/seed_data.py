from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed initial data: sports, countries, leagues, events, predictions, casino games'

    def handle(self, *args, **kwargs):
        self._seed_users()
        self._seed_sports()
        self._seed_countries()
        self._seed_leagues()
        self._seed_events()
        self._seed_predictions()
        self._seed_casino_games()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully.'))

    # ------------------------------------------------------------------
    def _seed_users(self):
        from users.models import User
        users_data = [
            {'email': 'admin@urbanbet.com', 'name': 'Admin User', 'password': 'password123', 'role': User.ADMIN, 'balance': 1000000, 'is_superuser': True, 'is_staff': True},
            {'email': 'test1@urbanbet.com', 'name': 'Test User 1', 'password': 'password123', 'role': User.USER, 'balance': 50000},
            {'email': 'test2@urbanbet.com', 'name': 'Test User 2', 'password': 'password123', 'role': User.USER, 'balance': 10000},
            {'email': 'test3@urbanbet.com', 'name': 'Test User 3', 'password': 'password123', 'role': User.USER, 'balance': 0},
        ]
        
        for data in users_data:
            email = data.pop('email')
            password = data.pop('password')
            is_superuser = data.pop('is_superuser', False)
            if not User.objects.filter(email=email).exists():
                if is_superuser:
                    User.objects.create_superuser(email=email, password=password, **data)
                else:
                    User.objects.create_user(email=email, password=password, **data)
        self.stdout.write('  Users seeded.')

    def _seed_sports(self):
        from sports.models import Sport
        sports_data = [
            {'name': 'Football', 'icon': 'football', 'order': 1},
            {'name': 'Basketball', 'icon': 'basketball', 'order': 2},
            {'name': 'Tennis', 'icon': 'tennis', 'order': 3},
            {'name': 'Rugby', 'icon': 'rugby', 'order': 4},
            {'name': 'Cricket', 'icon': 'cricket', 'order': 5},
            {'name': 'eSports', 'icon': 'esports', 'order': 6},
        ]
        for data in sports_data:
            Sport.objects.get_or_create(name=data['name'], defaults=data)
        self.stdout.write('  Sports seeded.')

    def _seed_countries(self):
        from sports.models import Country
        countries = [
            ('England', 'ENG'), ('Spain', 'ESP'), ('Germany', 'GER'),
            ('France', 'FRA'), ('Italy', 'ITA'), ('Rwanda', 'RWA'),
            ('USA', 'USA'), ('Brazil', 'BRA'), ('Argentina', 'ARG'),
        ]
        for name, code in countries:
            Country.objects.get_or_create(name=name, defaults={'code': code})
        self.stdout.write('  Countries seeded.')

    def _seed_leagues(self):
        from sports.models import Sport, Country, League
        football = Sport.objects.get(name='Football')
        basketball = Sport.objects.get(name='Basketball')
        tennis = Sport.objects.get(name='Tennis')

        eng = Country.objects.get(name='England')
        esp = Country.objects.get(name='Spain')
        ger = Country.objects.get(name='Germany')
        fra = Country.objects.get(name='France')
        usa = Country.objects.get(name='USA')

        leagues = [
            {'name': 'Premier League', 'sport': football, 'country': eng},
            {'name': 'La Liga', 'sport': football, 'country': esp},
            {'name': 'Bundesliga', 'sport': football, 'country': ger},
            {'name': 'Ligue 1', 'sport': football, 'country': fra},
            {'name': 'Champions League', 'sport': football, 'country': None},
            {'name': 'NBA', 'sport': basketball, 'country': usa},
            {'name': 'ATP Tour', 'sport': tennis, 'country': None},
        ]
        for data in leagues:
            League.objects.get_or_create(
                name=data['name'], sport=data['sport'],
                defaults={'country': data['country']}
            )
        self.stdout.write('  Leagues seeded.')

    def _seed_events(self):
        from sports.models import Sport, League, Country, SportEvent, Market
        football = Sport.objects.get(name='Football')
        pl = League.objects.get(name='Premier League')
        ll = League.objects.get(name='La Liga')
        bl = League.objects.get(name='Bundesliga')
        cl = League.objects.get(name='Champions League')
        eng = Country.objects.get(name='England')
        esp = Country.objects.get(name='Spain')
        ger = Country.objects.get(name='Germany')

        now = timezone.now()

        events_data = [
            {
                'sport': football, 'league': pl, 'country': eng,
                'home_team': 'Arsenal', 'away_team': 'Chelsea',
                'start_time': now + timedelta(hours=2),
                'status': SportEvent.STATUS_SCHEDULED,
                'home_odds': 2.10, 'draw_odds': 3.40, 'away_odds': 3.20,
            },
            {
                'sport': football, 'league': bl, 'country': ger,
                'home_team': 'Bayern Munich', 'away_team': 'Borussia Dortmund',
                'start_time': now - timedelta(minutes=30),
                'status': SportEvent.STATUS_LIVE,
                'home_odds': 1.80, 'draw_odds': 3.70, 'away_odds': 4.20,
            },
            {
                'sport': football, 'league': ll, 'country': esp,
                'home_team': 'Barcelona', 'away_team': 'Real Madrid',
                'start_time': now + timedelta(hours=5),
                'status': SportEvent.STATUS_SCHEDULED,
                'home_odds': 2.40, 'draw_odds': 3.20, 'away_odds': 2.90,
            },
            {
                'sport': football, 'league': cl, 'country': None,
                'home_team': 'PSG', 'away_team': 'Manchester City',
                'start_time': now + timedelta(days=1),
                'status': SportEvent.STATUS_SCHEDULED,
                'home_odds': 2.60, 'draw_odds': 3.10, 'away_odds': 2.50,
            },
            {
                'sport': football, 'league': pl, 'country': eng,
                'home_team': 'Liverpool', 'away_team': 'Manchester United',
                'start_time': now + timedelta(days=2),
                'status': SportEvent.STATUS_SCHEDULED,
                'home_odds': 1.95, 'draw_odds': 3.50, 'away_odds': 3.80,
            },
        ]

        standard_markets = [
            {'name': 'Match Result', 'options': ['Home Win', 'Draw', 'Away Win']},
            {'name': 'Both Teams To Score', 'options': ['Yes', 'No']},
            {'name': 'Over/Under 2.5 Goals', 'options': ['Over 2.5', 'Under 2.5']},
            {'name': 'Double Chance', 'options': ['Home or Draw', 'Away or Draw', 'Home or Away']},
        ]

        for data in events_data:
            event, created = SportEvent.objects.get_or_create(
                home_team=data['home_team'],
                away_team=data['away_team'],
                league=data['league'],
                defaults=data,
            )
            if created:
                for market_data in standard_markets:
                    Market.objects.create(event=event, **market_data)

        self.stdout.write('  Events & markets seeded.')

    def _seed_predictions(self):
        from predictions.models import AIPrediction
        preds = [
            {
                'match': 'Arsenal vs Liverpool',
                'prediction': 'Arsenal to win',
                'confidence': 75,
                'analysis': 'Arsenal has won 4 out of their last 5 home games against Liverpool. Strong home form and recent squad depth give them the edge.',
                'trend': 'Arsenal winning streak at home',
                'odds': '1.95',
                'is_featured': True,
            },
            {
                'match': 'PSG vs Bayern Munich',
                'prediction': 'Over 2.5 goals',
                'confidence': 82,
                'analysis': 'Both teams have scored in the last 7 encounters. High-pressing styles from both sides lead to an open, high-scoring affair.',
                'trend': 'High scoring matches in Champions League',
                'odds': '1.75',
                'is_featured': True,
            },
            {
                'match': 'Manchester City vs Liverpool',
                'prediction': 'Both teams to score: Yes',
                'confidence': 88,
                'analysis': 'Both teams have scored in 9 of the last 10 matches between them. Premier League top 2 clash guaranteed goals.',
                'trend': 'High scoring games in Premier League',
                'odds': '1.65',
                'is_featured': True,
            },
            {
                'match': 'Barcelona vs Real Madrid',
                'prediction': 'Real Madrid to win',
                'confidence': 60,
                'analysis': 'Real Madrid has better away form this season and strong defensive structure in big matches.',
                'trend': 'Real Madrid strong in El Clasico away',
                'odds': '2.90',
                'is_featured': False,
            },
        ]
        for data in preds:
            AIPrediction.objects.get_or_create(match=data['match'], defaults=data)
        self.stdout.write('  Predictions seeded.')

    def _seed_casino_games(self):
        from casino.models import CasinoGame
        games = [
            {'title': 'Book of Dead', 'provider': 'Play\'n GO', 'category': 'slots', 'is_popular': True, 'rtp': 96.21, 'min_bet': 100, 'max_bet': 500000},
            {'title': 'Starburst', 'provider': 'NetEnt', 'category': 'slots', 'is_popular': True, 'rtp': 96.09, 'min_bet': 100, 'max_bet': 100000},
            {'title': 'Gonzo\'s Quest', 'provider': 'NetEnt', 'category': 'slots', 'is_new': False, 'rtp': 95.97, 'min_bet': 200, 'max_bet': 200000},
            {'title': 'Mega Moolah', 'provider': 'Microgaming', 'category': 'jackpots', 'is_popular': True, 'rtp': 88.12, 'min_bet': 100, 'max_bet': 1000000},
            {'title': 'Divine Fortune', 'provider': 'NetEnt', 'category': 'jackpots', 'rtp': 96.59, 'min_bet': 100, 'max_bet': 500000},
            {'title': 'Blackjack Classic', 'provider': 'Evolution', 'category': 'table-games', 'is_popular': True, 'rtp': 99.28, 'min_bet': 1000, 'max_bet': 2000000},
            {'title': 'European Roulette', 'provider': 'NetEnt', 'category': 'table-games', 'rtp': 97.30, 'min_bet': 500, 'max_bet': 1000000},
            {'title': 'Live Blackjack', 'provider': 'Evolution', 'category': 'live-casino', 'is_new': True, 'is_popular': True, 'rtp': 99.28, 'min_bet': 2000, 'max_bet': 5000000},
            {'title': 'Live Roulette', 'provider': 'Evolution', 'category': 'live-casino', 'is_popular': True, 'rtp': 97.30, 'min_bet': 1000, 'max_bet': 3000000},
            {'title': 'Crazy Time', 'provider': 'Evolution', 'category': 'game-shows', 'is_new': True, 'is_popular': True, 'rtp': 96.08, 'min_bet': 500, 'max_bet': 1000000},
            {'title': 'Monopoly Live', 'provider': 'Evolution', 'category': 'game-shows', 'rtp': 96.23, 'min_bet': 500, 'max_bet': 500000},
            {'title': 'Sweet Bonanza', 'provider': 'Pragmatic Play', 'category': 'slots', 'is_new': True, 'rtp': 96.51, 'min_bet': 200, 'max_bet': 250000},
        ]
        for data in games:
            CasinoGame.objects.get_or_create(
                title=data['title'],
                provider=data['provider'],
                defaults=data,
            )
        self.stdout.write('  Casino games seeded.')
