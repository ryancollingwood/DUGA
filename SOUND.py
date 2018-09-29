from pygame import mixer
import SETTINGS
import consts.geom
import consts.raycast
import consts.tile


def play_sound(sound, distance):
    if distance <= consts.tile.TILE_SIZE * consts.raycast.render:
        if distance >= consts.tile.TILE_SIZE * (consts.raycast.render * 0.8):
            mixer.Sound.set_volume(sound, 0.2 * SETTINGS.volume)

        elif distance >= consts.tile.TILE_SIZE * (consts.raycast.render * 0.4):
            mixer.Sound.set_volume(sound, 0.5 * SETTINGS.volume)

        else:
            mixer.Sound.set_volume(sound, SETTINGS.volume)

        mixer.Sound.play(sound)
