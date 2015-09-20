#   This file is part of PARPG.

#   PARPG is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   PARPG is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with PARPG.  If not, see <http://www.gnu.org/licenses/>.

# sounds.py holds the object code to play sounds and sound effects
from fife import fife

class SoundEngine:
    def __init__(self, fife_engine):
        """Initialise the SoundEngine instance
           @type fife_engine: fine.Engine
           @param fife_engine: Instance of the Fife engine
           @return: None"""
        self.engine = fife_engine
        self.sound_engine = self.engine.getSoundManager()
        #self.sound_engine.init()
        # set up the sound
        self.music = self.sound_engine.createEmitter()
        self.music_on = False
        self.music_init = False
    
    def playMusic(self, sfile=None):
        """Play music, with the given file if passed
           @type sfile: string
           @param sfile: Filename to play
           @return: None"""
        if(sfile is not None):
            # setup the new sound
            sound = self.engine.getSoundClipManager().load(sfile)
            self.music.setSoundClip(sound)
            self.music.setLooping(True)
            self.music_init = True
        self.music.play()
        self.music_on = True

    def pauseMusic(self):
        """Stops current playback
           @return: None"""
        if(self.music_init == True):
            self.music.pause()
            self.music_on = False

    def toggleMusic(self):
        """Toggle status of music, either on or off
           @return: None"""
        if((self.music_on == False)and(self.music_init == True)):
            self.playMusic()
        else:
            self.pauseMusic()

    def setVolume(self, volume):
        """Set the volume of the music
           @type volume: integer
           @param volume: The volume wanted, 0 to 100
           @return: None"""
        self.sound_engine.setVolume(0.01 * volume)

