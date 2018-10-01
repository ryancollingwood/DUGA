from consts.player import og_player_health, og_player_armor
from PATHFINDING import has_line_of_sight

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


def damage_player(damage_amount, attack_type, attack_position):
    global player_armor
    global player_health
    global player_pos
    
    if has_line_of_sight(attack_position, player_map_pos):
        if player_armor > 0:
            player_health -= int(damage_amount * 0.65)
            if player_armor >= damage_amount * 2:
                player_armor -= damage_amount * 2
            else:
                player_armor = 0
        else:
            player_health -= damage_amount
        
        return True
    else:
        return False