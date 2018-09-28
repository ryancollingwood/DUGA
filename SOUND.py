from pygame import mixer
import SETTINGS
import consts.geom
import consts.raycast


def play_sound(sound, distance):
    if distance <= consts.geom.tile_size * consts.raycast.render:
        if distance >= consts.geom.tile_size * (consts.raycast.render * 0.8):
            mixer.Sound.set_volume(sound, 0.2 * SETTINGS.volume)

        elif distance >= consts.geom.tile_size * (consts.raycast.render * 0.4):
            mixer.Sound.set_volume(sound, 0.5 * SETTINGS.volume)

        else:
            mixer.Sound.set_volume(sound, SETTINGS.volume)

        mixer.Sound.play(sound)
