from consts.player import og_player_health, og_player_armor

player_rect = None
player_states = {
    'dead': False,
    'hurt': False,
    'heal': False,
    'armor': False,
    'invopen': False,
    'fade': False,
    'black': False,
    'title': False,
    'cspeed': 0,
    }
player_health = og_player_health
player_armor = og_player_armor
player_pos = [0,0]
player_map_pos = []
mouse_btn_active = False
mouse2_btn_active = False
reload_key_active = False
aiming = False
player = None
last_player_map_pos = None