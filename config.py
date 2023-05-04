from environs import Env


env = Env()
env.read_env()

POSTGRES_USER = env.str('POSTGRES_USER')
POSTGRES_PASSWD = env.str('POSTGRES_PASSWD')

TG_BOT_TOKEN = env.str('TG_BOT_TOKEN')

SLM_HOST = 'http://127.0.0.1'
