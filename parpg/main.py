#!/usr/bin/env python2 
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging
import sys
from os.path import abspath
      
def main(parser):

    opts, args = parser.parse_args()

    levels = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}

    #TODO: setup formating
    logging.basicConfig(filename=opts.logfile, level=levels[opts.loglevel])
    logger = logging.getLogger('parpg')

    try:
        old_path = sys.path
        if opts.fife_path:
            sys.path = [opts.fife_path]
        import fife
    except ImportError:
        logger.critical("Could not import fife module. Please install fife or set the --fife-path command line value")
        parser.print_help()
        sys.exit(1)
    finally:
        sys.path = old_path


    from fife.extensions.fife_settings import Setting

    settings = Setting(settings_file="settings.xml")
    
    data_dir =  abspath(settings.get("parpg","DataPath"))
    settings.set("parpg", "DataPath", data_dir)
    settings.set("FIFE", "WindowIcon", data_dir + "/" + settings.get("FIFE", "WindowIcon"))
    settings.set("FIFE", "Font", data_dir + "/" + settings.get("FIFE", "Font"))
   
    from parpg.application import PARPGApplication
    from parpg.common import utils
    
    # enable psyco if available and in settings file
    try:
        import psyco
        psyco_available = True
    except ImportError:
        logger.warning('Psyco Acceleration unavailable')
        psyco_available = False
    
    if settings.get("fife", "UsePsyco"):
        if psyco_available:
            psyco.full()
            logger.info('Psyco Acceleration enabled')
        else:
            logger.warning('Please install psyco before attempting to use it'
                            'Psyco Acceleration disabled')
    else:
        logger.info('Psycho Acceleration disabled')
    
    # run the game
    app = PARPGApplication(settings)
    app.run()
