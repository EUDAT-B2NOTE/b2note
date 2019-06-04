# 04/06/2019 TODO refactor
from b2note_api import app as application
import os

activate_this = os.environ['B2NOTE_PREFIX_SW_PATH'] + '/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

